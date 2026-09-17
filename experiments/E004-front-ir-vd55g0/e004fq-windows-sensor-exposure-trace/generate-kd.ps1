param(
    [Parameter(Mandatory=$true)][string]$AuxBase,
    [Parameter(Mandatory=$true)][string]$Output
)
$ErrorActionPreference='Stop'
if($AuxBase -notmatch '^[0-9a-fA-F]{16}$'){ throw 'aux base must be 16 hex digits' }
$base=[Convert]::ToUInt64($AuxBase,16)
if(($base -shr 48) -ne 0xffff -or ($base % 0x1000) -ne 0){ throw 'invalid kernel module base' }
New-Item -ItemType Directory -Force -Path $Output | Out-Null
$hook='{0:x16}' -f ([UInt64]($base + 0xa350))
$cond='((@w0 >= 0x0200 & @w0 <= 0x0202) | (@w0 >= 0x044c & @w0 <= 0x0451) | (@w0 >= 0x0458 & @w0 <= 0x0459) | (@w0 >= 0x0467 & @w0 <= 0x046e))'
$cmd='.if ('+$cond+') { r @$t0 = @$t0 + 1; .printf "E004FQ_SENSOR_WRITE hit=%u reg=%x data=%x\n", @$t0, @w0, @w1; .if (@$t0 >= 0n128) { bd 0 } }; gc'
$arm=@(
'.echo E004FQ_ARM_BEGIN',
'r @$t0 = 0',
('bp0 '+$hook+' "'+$cmd+'"'),
'bl',
'.echo E004FQ_ARMED_RESUMING',
'g'
) -join "`n"
[IO.File]::WriteAllText((Join-Path $Output 'arm.kd'),$arm+"`n",(New-Object Text.UTF8Encoding($false)))
$cases=@(0x0200,0x0202,0x044b,0x044c,0x044e,0x0451,0x0452,0x0458,0x0459,0x0466,0x0467,0x046e,0x046f)
$dry=New-Object System.Collections.Generic.List[string]
$dry.Add('.echo E004FQ_DRY_BEGIN')
foreach($r in $cases){
  $h=('0x{0:x}' -f $r)
  $c='(('+$h+' >= 0x0200 & '+$h+' <= 0x0202) | ('+$h+' >= 0x044c & '+$h+' <= 0x0451) | ('+$h+' >= 0x0458 & '+$h+' <= 0x0459) | ('+$h+' >= 0x0467 & '+$h+' <= 0x046e))'
  $dry.Add('.if ('+$c+') { .printf "E004FQ_DRY_TARGET reg=%x\n", '+$h+' } .else { .printf "E004FQ_DRY_SKIP reg=%x\n", '+$h+' }')
}
$dry.Add('.echo E004FQ_DRY_END_STAY_BROKEN')
[IO.File]::WriteAllText((Join-Path $Output 'validate.kd'),(($dry -join "`n")+"`n"),(New-Object Text.UTF8Encoding($false)))
Write-Output ("AUX base=0x{0:x16}; hook=0x{1}" -f $base,$hook)
