Param(
  [int]$Port = 16666,
  [switch]$Debug
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Set-Location $repo

# 确保日志目录
New-Item -ItemType Directory -Force -Path "$repo\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "$repo\output" | Out-Null
New-Item -ItemType Directory -Force -Path "$repo\.cache" | Out-Null

# 虚拟环境
$venv = Join-Path $repo ".venv"
$python = "$venv\Scripts\python.exe"

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
& "$venv\Scripts\pip.exe" install -U pip | Out-Null
& "$venv\Scripts\pip.exe" install -r "$repo\requirements.txt" | Out-Null

$env:GRAPH_MCP_PORT = "$Port"

# 组装参数
$args = @("graph_mcp.py","--port",$Port)
if ($Debug) { $args += "--debug" }

# 后台启动并隐藏窗口，日志重定向
$logOut = Join-Path $repo "logs\server.out.log"
$logErr = Join-Path $repo "logs\server.err.log"
$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = $python
$startInfo.Arguments = [string]::Join(" ", $args)
$startInfo.WorkingDirectory = $repo
$startInfo.UseShellExecute = $false
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
$startInfo.CreateNoWindow = $true

$proc = New-Object System.Diagnostics.Process
$proc.StartInfo = $startInfo
$proc.Start() | Out-Null

# 异步写日志
$proc.BeginOutputReadLine()
$proc.add_OutputDataReceived({ param($s,$e) if ($e.Data) { Add-Content -Path $logOut -Value $e.Data }})
$proc.BeginErrorReadLine()
$proc.add_ErrorDataReceived({ param($s,$e) if ($e.Data) { Add-Content -Path $logErr -Value $e.Data }})

# 防止任务计划因脚本退出而终止子进程
while (!$proc.HasExited) { Start-Sleep -Seconds 5 }