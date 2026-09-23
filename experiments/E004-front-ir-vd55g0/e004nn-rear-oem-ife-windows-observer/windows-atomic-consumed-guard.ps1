# SPDX-License-Identifier: MIT
# E004nn FUTURE Windows camera oracle script-ENTRY safety helper, NOT used in
# the historical two-invocation E004nn capture. Call BEFORE camera access:
# & "$PSScriptRoot\windows-atomic-consumed-guard.ps1" -MarkerPath (Join-Path $PSScriptRoot 'E004np-UNIQUE-CONSUMED.marker')
# Never delete a real experiment marker to "retry" a consumed original.
param([Parameter(Mandatory=$true)][ValidateNotNullOrEmpty()][string]$MarkerPath)
$ErrorActionPreference='Stop'
$directory=Split-Path -Parent $MarkerPath
if([string]::IsNullOrWhiteSpace($directory) -or
   -not [System.IO.Directory]::Exists($directory)) {
  throw 'WINDOWS_ORACLE_ATOMIC_CONSUMED_MARKER_PARENT_MISSING'
}
$stream=$null
try {
  # CreateNew is atomic. Opening an existing marker FAILS CLOSED even when
  # the previous process has exited and no file handle remains open.
  $stream=[System.IO.File]::Open($MarkerPath,
            [System.IO.FileMode]::CreateNew,
            [System.IO.FileAccess]::Write,
            [System.IO.FileShare]::None)
  $bytes=[System.Text.Encoding]::UTF8.GetBytes(
      ('WINDOWS_ORACLE_SCRIPT_ENTRY_CONSUMED_UTC='+[DateTimeOffset]::UtcNow.ToString('o')+[Environment]::NewLine))
  $stream.Write($bytes,0,$bytes.Length)
  $stream.Flush($true)
} catch {
  # Fail closed for an existing file, unknown file permissions, or partial
  # write/durability failure. Never truncate, retry or delete a marker.
  throw 'WINDOWS_ORACLE_SINGLE_USE_ENTRY_REJECTED_OR_UNCERTAIN'
} finally {
  if($null -ne $stream){$stream.Dispose()}
}
Write-Output 'WINDOWS_ORACLE_ATOMIC_ENTRY_CONSUMED_PASS'
