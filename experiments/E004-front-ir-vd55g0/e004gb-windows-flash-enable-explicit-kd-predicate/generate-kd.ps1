param(
    [Parameter(Mandatory=$true)][string]$PmicBase,
    [Parameter(Mandatory=$true)][string]$Output
)
$ErrorActionPreference='Stop'
if($PmicBase -notmatch '^[0-9a-fA-F]{16}$'){ throw 'pmic base must be 16 hex digits' }
$base=[Convert]::ToUInt64($PmicBase,16)
if(($base -shr 48) -ne 0xffff -or ($base % 0x1000) -ne 0){ throw 'invalid kernel module base' }
$targets=@(0xee3e,0xee3f,0xee40,0xee41,0xee46,0xee4a,0xee4b,0xee4c,0xee4d,0xee4e,0xee67)
function Get-ExactPredicate([string]$reg) {
    return '('+(($targets|ForEach-Object{'('+$reg+' == 0x'+('{0:x4}' -f $_)+')'}) -join ' | ')+')'
}
New-Item -ItemType Directory -Force -Path $Output | Out-Null
$preHook='{0:x16}' -f ([UInt64]($base + 0x23af8))
$postHook='{0:x16}' -f ([UInt64]($base + 0x23bec))
$preTest=Get-ExactPredicate '@w24'
$postTest=Get-ExactPredicate '(@w27 & 0xffff)'
$pre='.if ('+$preTest+') { r @$t0 = @$t0 + 1; .printf \"E004GB_PRE hit=%u reg=%x mask=%x read_rc=%x\n\", @$t0, @w24, @w23, @w0; db @sp+0x18 L1; db @sp+0x10 L1; .if (@$t0 >= 0n128) { bd 0 } }; gc'
$post='.if ('+$postTest+') { r @$t1 = @$t1 + 1; .printf \"E004GB_POST hit=%u reg=%x mask=%x write_rc=%x\n\", @$t1, (@w27 & 0xffff), @w23, @w0; db @x21 L1; .if (@$t1 >= 0n128) { bd 1 } }; gc'
$arm=@(
'.echo E004GB_ARM_BEGIN',
'r @$t0 = 0',
'r @$t1 = 0',
('bp0 '+$preHook+' "'+$pre+'"'),
('bp1 '+$postHook+' "'+$post+'"'),
'bl',
'.echo E004GB_ARMED_STAY_BROKEN'
) -join [Environment]::NewLine
[IO.File]::WriteAllText((Join-Path $Output 'arm.kd'),$arm+[Environment]::NewLine,(New-Object Text.UTF8Encoding($false)))
$cases=@(0xee3e,0xee3f,0xee40,0xee41,0xee3d,0xee42,0xee45,0xee46,0xee47,0xee49,0xee4a,0xee4b,0xee4c,0xee4d,0xee4e,0xee4f,0xee66,0xee67,0xee68)
$dry=New-Object System.Collections.Generic.List[string]
$dry.Add('.echo E004GB_DRY_BEGIN')
$dry.Add('r @$t0 = 0')
$dry.Add('r @$t1 = 0')
foreach($r in $cases){
    $h=('{0:x4}' -f $r)
    $cond=Get-ExactPredicate ('0x'+$h)
    $dry.Add('.if ('+$cond+') { .printf "E004GB_DRY_TARGET reg=%x\n", 0x'+$h+' } .else { .printf "E004GB_DRY_SKIP reg=%x\n", 0x'+$h+' }')
}
$dry.Add('r @$t2 = 0x1234ee4a')
$dry.Add('.if (((@$t2 & 0xffff) == 0xee4a)) { .printf "E004GB_DRY_POSTREG raw=%x reg=%x\n", @$t2, (@$t2 & 0xffff) } .else { .echo E004GB_DRY_POSTREG_FAIL }')
$dry.Add('.echo E004GB_DRY_END_STAY_BROKEN')
[IO.File]::WriteAllText((Join-Path $Output 'validate.kd'),(($dry -join [Environment]::NewLine)+[Environment]::NewLine),(New-Object Text.UTF8Encoding($false)))
Write-Output ("E004GB_PMIC_BASE=0x{0:x16} HOOKS=0x{1},0x{2}" -f $base,$preHook,$postHook)
