Param(
  [int]$Port = 16666,
  [switch]$Debug
)

$ErrorActionPreference = "Stop"

# 1) 定位仓库路径
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repo

# 2) 准备虚拟环境并安装依赖（首次）
$venv = Join-Path $repo ".venv"
$python = Join-Path $venv "Scripts\python.exe"

function Test-PyVersionOK {
  param([string]$exe)
  try {
    $v = & $exe -c "import sys;print(f'{sys.version_info[0]}.{sys.version_info[1]}')" 2>$null
    if ($LASTEXITCODE -ne 0) { return $false }
    $parts = $v -split '\.'
    if ([int]$parts[0] -gt 3) { return $true }
    if ([int]$parts[0] -eq 3 -and [int]$parts[1] -ge 10) { return $true }
    return $false
  } catch { return $false }
}

function Get-BasePython {
  $candidates = @(
    "py -3",
    "py",
    "python",
    "$env:LOCALAPPDATA\Programs\Python\Launcher\py.exe"
  )
  foreach ($c in $candidates) {
    try {
      if (Test-PyVersionOK -exe $c) { return $c }
    } catch { }
  }
  throw "No suitable Python (>=3.10) found. Please install Python 3.10+."
}
if (!(Test-Path $python)) {
  $basePy = Get-BasePython
  & $basePy -m venv $venv
}
& $python -m pip install -U pip
& $python -m pip install -r "$repo\requirements.txt"

# 3) 写入 MCP 配置
& "$python" "scripts\setup_mcp_configs.py" --port $Port

# 4) 注册任务计划：登录时后台运行
$taskName = "Graph-MCP-Server"
$runScript = Join-Path $repo "scripts\run_server.ps1"
$arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$runScript`" -Port $Port" + ($(if($Debug){" -Debug"}else{""}))

# 若已存在则先删除
$sched = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($sched) {
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

$action = New-ScheduledTaskAction -Execute "pwsh.exe" -Argument $arguments -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 24)
$principal = New-ScheduledTaskPrincipal -UserId "$env:UserDomain\$env:UserName" -LogonType Interactive -RunLevel Limited
# resolve shell executable (prefer pwsh, fallback to powershell)
$pwshExe = (Get-Command pwsh.exe -ErrorAction SilentlyContinue).Path
if (-not $pwshExe) { $pwshExe = (Get-Command powershell.exe -ErrorAction SilentlyContinue).Path }

$registered = $false
try {
  # 使用 schtasks 以当前用户创建登录触发的计划任务（无需管理员）
  $ru = "$env:UserDomain\$env:UserName"
  $tn = $taskName
  $cmd = "schtasks /Create /TN `"$tn`" /TR `"`"$pwshExe`" $arguments`" /SC ONLOGON /RL LIMITED /RU `"$ru`" /IT /F"
  # 捕获所有输出，避免 NativeCommandError 中断
  cmd.exe /c $cmd 2>&1 | Out-Null
  if ($LASTEXITCODE -eq 0) {
    $registered = $true
  } else {
    throw "schtasks exit code: $LASTEXITCODE"
  }
} catch {
  Write-Host "schtasks create failed: $($_.Exception.Message). Fallback to Startup shortcut..."
  # Fallback: 创建启动文件夹快捷方式
  $startup = [Environment]::GetFolderPath('Startup')
  $shell = New-Object -ComObject WScript.Shell
  $lnk = $shell.CreateShortcut((Join-Path $startup "$taskName.lnk"))
  $lnk.TargetPath = $pwshExe
  $lnk.Arguments = $arguments
  $lnk.WorkingDirectory = $repo
  $lnk.WindowStyle = 7
  $lnk.Save()
}

if ($registered) {
  # 5) 立即启动一次（schtasks）
  try {
    cmd.exe /c "schtasks /Run /TN `"$taskName`"" | Out-Null
  } catch {
    Write-Host "schtasks run failed: $($_.Exception.Message)"
  }
} else {
  # 5) 立即启动一次（Startup shortcut）
  try {
    Start-Process -FilePath $pwshExe -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden
  } catch {
    Write-Host "startup shortcut run failed: $($_.Exception.Message)"
  }
  Write-Host "Startup shortcut created at: $([System.IO.Path]::Combine([Environment]::GetFolderPath('Startup'), "$taskName.lnk"))"
}

Write-Host ("Install completed. Task name: {0}" -f $taskName)
Write-Host "Logs: $repo\logs\server.out.log , $repo\logs\server.err.log"
Write-Host "To change the port, rerun this script with -Port to recreate the task."
Write-Host "Now start/restart your ai client and enjoy it!"