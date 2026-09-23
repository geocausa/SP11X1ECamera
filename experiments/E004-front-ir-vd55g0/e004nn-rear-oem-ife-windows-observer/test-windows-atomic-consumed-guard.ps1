# SPDX-License-Identifier: MIT
# No camera, no real consumed marker: isolated temporary dry-run ONLY.
$ErrorActionPreference='Stop'
$dir=Join-Path ([System.IO.Path]::GetTempPath()) (
    'e004nn-atomic-entry-selftest-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $dir -ErrorAction Stop | Out-Null
try {
  $marker=Join-Path $dir 'new-test-only-identity.consumed'
  $helper=Join-Path $PSScriptRoot 'windows-atomic-consumed-guard.ps1'
  if(Test-Path -LiteralPath $marker){throw 'unexpected existing dry-run marker'}
  $first=@(& $helper -MarkerPath $marker)
  if($first.Count -ne 1 -or $first[0] -ne 'WINDOWS_ORACLE_ATOMIC_ENTRY_CONSUMED_PASS' -or
     -not(Test-Path -LiteralPath $marker)){throw 'first atomic entry failed'}
  $bytes=[IO.File]::ReadAllBytes($marker)
  if($bytes.Length -lt 30){throw 'unexpected empty first marker'}
  $secondRejected=$false
  try { & $helper -MarkerPath $marker | Out-Null }
  catch { $secondRejected=($_.Exception.Message -match 'WINDOWS_ORACLE_SINGLE_USE_ENTRY_REJECTED_OR_UNCERTAIN') }
  if(-not $secondRejected){throw 'later scheduled duplicate NOT rejected'}
  $after=[IO.File]::ReadAllBytes($marker)
  if([string]::Join(',',$bytes) -ne [string]::Join(',',$after)){
    throw 'second entry altered existing marker'
  }
  Write-Output 'PASS E004nn Windows future-task atomic CreateNew first-entry and permanent duplicate reject; test temporary marker only'
} finally {
  Remove-Item -LiteralPath $dir -Recurse -Force -ErrorAction SilentlyContinue
}
