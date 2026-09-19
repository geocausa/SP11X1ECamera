param([Parameter(Mandatory=$true)][string]$LogPath)
$ErrorActionPreference='Stop'
if(!(Test-Path -LiteralPath $LogPath -PathType Leaf)){ throw 'E004GB_KD_DRY_LOG_MISSING' }
$s=[IO.File]::ReadAllText((Resolve-Path -LiteralPath $LogPath).Path)
# WinDbg files can use CRLF; normalize before multiline regex matching.
$s=$s.Replace("`r`n","`n").Replace("`r","`n")
$begin=$s.LastIndexOf('E004GB_DRY_BEGIN',[StringComparison]::Ordinal)
$end=$s.LastIndexOf('E004GB_DRY_END_STAY_BROKEN',[StringComparison]::Ordinal)
if($begin -lt 0 -or $end -lt $begin){ throw 'E004GB_KD_DRY_BEGIN_END_MISSING' }
$chunk=$s.Substring($begin,($end+('E004GB_DRY_END_STAY_BROKEN').Length)-$begin)
$targets=@('ee3e','ee3f','ee40','ee41','ee46','ee4a','ee4b','ee4c','ee4d','ee4e','ee67')
$skips=@('ee3d','ee42','ee45','ee47','ee49','ee4f','ee66','ee68')
foreach($hex in $targets){
    if($chunk -notmatch ('(?m)^E004GB_DRY_TARGET reg='+$hex+'[ ]*$')){
        throw ('E004GB_KD_DRY_EXPECTED_TARGET_MISSING_'+$hex)
    }
    if($chunk -match ('(?m)^E004GB_DRY_SKIP reg='+$hex+'[ ]*$')){
        throw ('E004GB_KD_DRY_TARGET_CLASSIFIED_SKIP_'+$hex)
    }
}
foreach($hex in $skips){
    if($chunk -notmatch ('(?m)^E004GB_DRY_SKIP reg='+$hex+'[ ]*$')){
        throw ('E004GB_KD_DRY_EXPECTED_SKIP_MISSING_'+$hex)
    }
    if($chunk -match ('(?m)^E004GB_DRY_TARGET reg='+$hex+'[ ]*$')){
        throw ('E004GB_KD_DRY_SKIP_CLASSIFIED_TARGET_'+$hex)
    }
}
$hits=[regex]::Matches($chunk,'(?m)^E004GB_DRY_(TARGET|SKIP) reg=([0-9a-f]{4})[ ]*$')
if($hits.Count -ne 19){ throw ('E004GB_KD_DRY_EXPECTED_19_CLASSIFICATIONS_GOT_'+$hits.Count) }
if($chunk -notmatch 'E004GB_DRY_POSTREG raw=1234ee4a reg=ee4a' -or
   $chunk -match 'E004GB_DRY_POSTREG_FAIL'){ throw 'E004GB_KD_DRY_POSTREG_INVALID' }
if($s -match 'E004GB_ARM_BEGIN'){ throw 'E004GB_KD_ALREADY_ARMED_BEFORE_DRY_APPROVAL' }
Write-Output 'E004GB_LIVE_MASM_DRY=PASS TARGETS=11 SKIPS=8 ENABLE_46=TARGET ENABLE_4E=TARGET'
