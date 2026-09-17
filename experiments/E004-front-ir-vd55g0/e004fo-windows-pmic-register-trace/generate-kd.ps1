param(
    [Parameter(Mandatory=$true)][string]$PmicBase,
    [Parameter(Mandatory=$true)][string]$Output
)
$ErrorActionPreference='Stop'
if($PmicBase -notmatch '^[0-9a-fA-F]{16}$'){ throw 'pmic base must be 16 hex digits' }
$base=[Convert]::ToUInt64($PmicBase,16)
if(($base -shr 48) -ne 0xffff -or ($base % 0x1000) -ne 0){ throw 'invalid kernel module base' }
New-Item -ItemType Directory -Force -Path $Output | Out-Null
$preHook='{0:x16}' -f ([UInt64]($base + 0x23af8))
$postHook='{0:x16}' -f ([UInt64]($base + 0x23bec))
$pre='.if (((@w24 >= 0xee3e && @w24 <= 0xee41) || (@w24 >= 0xee4a && @w24 <= 0xee4d) || @w24 == 0xee67)) { r @$t0 = @$t0 + 1; .printf \"E004FO_PRE hit=%u reg=%x mask=%x read_rc=%x\\n\", @$t0, @w24, @w23, @w0; db @x21 L1; db @sp+0x10 L1; .if (@$t0 >= 0n64) { bd 0 } }; gc'
$post='.if (((@w24 >= 0xee3e && @w24 <= 0xee41) || (@w24 >= 0xee4a && @w24 <= 0xee4d) || @w24 == 0xee67)) { r @$t1 = @$t1 + 1; .printf \"E004FO_POST hit=%u reg=%x mask=%x write_rc=%x\\n\", @$t1, @w24, @w23, @w0; db @x21 L1; .if (@$t1 >= 0n64) { bd 1 } }; gc'
$arm=@(
'.echo E004FO_ARM_BEGIN',
'r @$t0 = 0',
'r @$t1 = 0',
('bp0 '+$preHook+' "'+$pre+'"'),
('bp1 '+$postHook+' "'+$post+'"'),
'bl',
'.echo E004FO_ARMED_RESUMING',
'g'
) -join "`n"
[IO.File]::WriteAllText((Join-Path $Output 'arm.kd'),$arm+"`n",(New-Object Text.UTF8Encoding($false)))
$cases=0xee3e,0xee41,0xee4a,0xee4d,0xee67,0xee42,0xee68
$dry=New-Object System.Collections.Generic.List[string]
$dry.Add('.echo E004FO_DRY_BEGIN'); $dry.Add('r @$t0 = 0'); $dry.Add('r @$t1 = 0')
foreach($r in $cases){
    $h=('{0:x}' -f $r)
    $cond='((0x'+$h+' >= 0xee3e && 0x'+$h+' <= 0xee41) || (0x'+$h+' >= 0xee4a && 0x'+$h+' <= 0xee4d) || 0x'+$h+' == 0xee67)'
    $dry.Add('.if ('+$cond+') { .printf "E004FO_DRY_TARGET reg=%x\n", 0x'+$h+'; db 0x'+('{0:x16}' -f $base)+' L1 } .else { .printf "E004FO_DRY_SKIP reg=%x\n", 0x'+$h+' }')
}
$dry.Add('.echo E004FO_DRY_END_RESUMING'); $dry.Add('g')
[IO.File]::WriteAllText((Join-Path $Output 'validate.kd'),(($dry -join "`n")+"`n"),(New-Object Text.UTF8Encoding($false)))
Write-Output ("PMIC base=0x{0:x16}; hooks=0x{1},0x{2}" -f $base,$preHook,$postHook)
