Param(
  [switch]$Purge,        # additionally remove .venv, logs, output, .cache
  [switch]$RemoveVenv,   # remove only .venv (not equal to Purge)
  [switch]$Debug
)

$ErrorActionPreference = "Stop"

function Write-Info($msg){ Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg){ Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Ok($msg){ Write-Host "[OK] $msg" -ForegroundColor Green }
function Try-Do([scriptblock]$action){
  try { & $action } catch { Write-Warn $_.Exception.Message }
}

# Write UTF-8 without BOM for cross-version compatibility (PS 5.1/7)
function Write-FileUtf8NoBom([string]$path, [string]$content) {
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($path, $content, $utf8NoBom)
}

# repo path
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repo
$taskName = "Graph-MCP-Server"

Write-Info "Start uninstall on Windows (scheduled task / startup)"

# 1) Stop and delete scheduled task (if exists)
Try-Do { cmd.exe /c "schtasks /End /TN `"$taskName`"" | Out-Null }
Try-Do { cmd.exe /c "schtasks /Delete /TN `"$taskName`" /F" | Out-Null }

# 2) Remove Startup shortcut (fallback path from installer)
$startup = [Environment]::GetFolderPath('Startup')
$lnk = Join-Path $startup "$taskName.lnk"
Try-Do {
  if (Test-Path $lnk) {
    Remove-Item -Path $lnk -Force
    Write-Ok ("Removed Startup shortcut: " + $lnk)
  }
}

# 3) Kill possible leftover Python processes (match graph_mcp.py and repo path)
Try-Do {
  $escapedRepo = [regex]::Escape($repo)
  $procs = Get-CimInstance Win32_Process |
    Where-Object { $_.Name -match 'python\.exe' -and $_.CommandLine -match 'graph_mcp\.py' -and $_.CommandLine -match $escapedRepo }
  foreach($p in $procs){
    Try-Do { Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop }
  }
  if ($procs) { Write-Ok (("Killed {0} related Python process(es)") -f $procs.Count) }
}

# 4) Remove graph_mcp entry from client config files (symmetric to scripts/setup_mcp_configs.py)
function Get-McpConfigTargets {
  $userHome = [Environment]::GetFolderPath("UserProfile")
  $appdata = $env:APPDATA
  if (-not $appdata -or $appdata -eq "") {
    $appdata = Join-Path $userHome "AppData\Roaming"
  }
  @(
    @{ Name="Cline"; Path=Join-Path $appdata "Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json" },
    @{ Name="Roo Code"; Path=Join-Path $appdata "Code\User\globalStorage\rooveterinaryinc.roo-cline\settings\mcp_settings.json" },
    @{ Name="Claude"; Path=Join-Path $appdata "Claude\claude_desktop_config.json" },
    @{ Name="Cursor"; Path=Join-Path $userHome ".cursor\mcp.json" },
    @{ Name="Windsurf"; Path=Join-Path $userHome ".codeium\windsurf\mcp_config.json" },
    @{ Name="Claude Code"; Path=Join-Path $userHome ".claude.json" },
    @{ Name="LM Studio"; Path=Join-Path $userHome ".lmstudio\mcp.json" },
    @{ Name="CodeBuddy IDE"; Path=Join-Path $appdata "CodeBuddy\User\globalStorage\tencent.planning-genie\settings\codebuddy_mcp_settings.json" },
    @{ Name="CodeBuddy CLI"; Path=Join-Path $userHome ".codebuddy.json" },
    @{ Name="Trae CN"; Path=Join-Path $appdata "Trae CN\User\mcp.json" }
  )
}

function Sanitize-JsonContent([string]$text) {
  # remove BOM
  if ($text.Length -gt 0 -and [int]$text[0] -eq 0xFEFF) { $text = $text.Substring(1) }
  # remove // and /* */ comments
  $text = [Regex]::Replace($text, '(?m)^\s*//.*$', '')
  $text = [Regex]::Replace($text, '/\*.*?\*/', '', 'Singleline')
  # remove trailing commas before } or ]
  $text = [Regex]::Replace($text, ',\s*([}\]])', '$1')
  return $text
}

function RegexRemove-GraphMcp([string]$text) {
  $changed = $false
  # remove "graph_mcp": {...} entries in any position
  $patterns = @(
    '\s*,\s*"graph_mcp"\s*:\s*\{.*?\}\s*',   # middle or with leading comma
    '"graph_mcp"\s*:\s*\{.*?\}\s*,\s*',      # start with following comma
    '"graph_mcp"\s*:\s*\{.*?\}\s*'           # only entry
  )
  foreach ($pat in $patterns) {
    $newText = [Regex]::Replace($text, $pat, '', 'Singleline')
    if ($newText -ne $text) {
      $text = $newText
      $changed = $true
    }
  }
  return ,@($changed, $text)
}

function Remove-GraphMcp-FromJsonFile([string]$filePath){
  if (!(Test-Path $filePath)) { return $false }
  $raw = Get-Content -Path $filePath -Raw -ErrorAction Stop
  if (-not $raw -or -not $raw.Trim()) { return $false }

  # First attempt: strict JSON
  try {
    $obj = $raw | ConvertFrom-Json -Depth 100
    $changed = $false
    if ($obj.PSObject.Properties.Name -contains "mcpServers") {
      $ms = $obj.mcpServers
      if ($ms -and $ms.PSObject.Properties.Name -contains "graph_mcp") {
        $ms.PSObject.Properties.Remove("graph_mcp") | Out-Null
        $changed = $true
      }
    }
    if ($obj.PSObject.Properties.Name -contains "servers") {
      $sv = $obj.servers
      if ($sv -and $sv.PSObject.Properties.Name -contains "graph_mcp") {
        $sv.PSObject.Properties.Remove("graph_mcp") | Out-Null
        $changed = $true
      }
    }
    if ($changed) {
      $json = $obj | ConvertTo-Json -Depth 50
      Write-FileUtf8NoBom $filePath $json
      Write-Ok ("Removed MCP entry from: " + $filePath)
    }
    return $changed
  } catch {
    # Second attempt: sanitize then parse
    Try-Do { Copy-Item -Path $filePath -Destination ($filePath + ".bak") -Force }
    $san = Sanitize-JsonContent $raw
    try {
      $obj2 = $san | ConvertFrom-Json -Depth 100
      $changed2 = $false
      if ($obj2.PSObject.Properties.Name -contains "mcpServers") {
        $ms2 = $obj2.mcpServers
        if ($ms2 -and $ms2.PSObject.Properties.Name -contains "graph_mcp") {
          $ms2.PSObject.Properties.Remove("graph_mcp") | Out-Null
          $changed2 = $true
        }
      }
      if ($obj2.PSObject.Properties.Name -contains "servers") {
        $sv2 = $obj2.servers
        if ($sv2 -and $sv2.PSObject.Properties.Name -contains "graph_mcp") {
          $sv2.PSObject.Properties.Remove("graph_mcp") | Out-Null
          $changed2 = $true
        }
      }
      if ($changed2) {
        $json2 = $obj2 | ConvertTo-Json -Depth 50
        Write-FileUtf8NoBom $filePath $json2
        Write-Ok ("Removed MCP entry from (sanitized): " + $filePath)
      } else {
        Write-Info ("No 'graph_mcp' entry found in (sanitized): " + $filePath)
      }
      return $changed2
    } catch {
      # Final attempt: regex remove text
      $res = RegexRemove-GraphMcp $raw
      $changed3 = $res[0]
      $text3 = $res[1]
      if ($changed3 -and $text3) {
        Write-FileUtf8NoBom $filePath $text3
        Write-Ok ("Removed MCP entry via text fallback: " + $filePath)
        return $true
      } else {
        Write-Warn ("JSON parse failed and text fallback found nothing: " + $filePath)
        return $false
      }
    }
  }
}

Write-Info "Clean MCP client configs: remove 'graph_mcp'"
$targets = Get-McpConfigTargets
foreach($t in $targets){
  Try-Do { Remove-GraphMcp-FromJsonFile $t.Path | Out-Null }
}

# 5) Optional cleanup of files and virtual environment
function Safe-Remove([string]$p){
  Try-Do {
    if (Test-Path $p) {
      Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction Stop
      Write-Ok ("Deleted: " + $p)
    }
  }
}

if ($Purge -or $RemoveVenv) { Safe-Remove (Join-Path $repo ".venv") }
if ($Purge) {
  Safe-Remove (Join-Path $repo "logs")
  Safe-Remove (Join-Path $repo "output")
  Safe-Remove (Join-Path $repo ".cache")
}

Write-Ok "Uninstall completed. For full cleanup, run: .\uninstall_windows.ps1 -Purge"