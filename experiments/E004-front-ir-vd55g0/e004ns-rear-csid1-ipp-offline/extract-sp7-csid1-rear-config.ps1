# SPDX-License-Identifier: MIT
# E004ns: SP7-only E004nq original KD physical logs -> whitelisted CSID1 scalar
# register configuration, LIVE1/LIVE2. No optical bytes or raw logs transferred.
$ErrorActionPreference='Stop'
$root='C:\Users\SurfacePro7\Documents\KDNET\Codex\E004NQ-REAR-PHYSICAL-20260923'
$dst=Join-Path $root 'E004NS-CSID1-REAR-CONFIG-SCALAR.json'
if(Test-Path -LiteralPath $dst){throw 'E004NS_PRIVATE_REDUCER_ALREADY_CONSUMED'}
$offsets=[ordered]@{
 top_irq_mask=0x80
 buffer_done_irq_mask=0x90
 rx_irq_mask=0xa0
 ipp_irq_mask=0xb0
 rx_cfg0=0x200
 rx_cfg1=0x204
 ipp_cfg0=0x300
 ipp_ctrl=0x304
 ipp_cfg1=0x310
 ipp_parity_zero0=0x324
 ipp_parity_zero1=0x330
 ipp_epoch_irq_cfg=0x334
 ipp_epoch0_subsample=0x338
 ipp_epoch1_subsample=0x33c
 ipp_hcrop=0x35c
 ipp_vcrop=0x360
 ipp_pix_drop_pattern=0x364
 ipp_pix_drop_period=0x368
 ipp_line_drop_pattern=0x36c
 ipp_line_drop_period=0x370
 ipp_frame_drop_pattern=0x374
 ipp_frame_drop_period=0x378
 ipp_irq_subsample_pattern=0x37c
 ipp_irq_subsample_period=0x380
 ipp_format_measure_cfg0=0x384
 ipp_format_measure_cfg1=0x388
}
$pattern='(?im)^00000000\x60([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})'
function Reg([string]$text,[long]$address){
 $line=$address-($address%16)
 $m=[regex]::Match($text,'(?im)^00000000\x60'+('{0:x8}' -f $line)+'[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})')
 if(-not $m.Success){throw ('E004NS_MISSING_REGISTER_0x'+('{0:x8}' -f $address))}
 return '0x'+$m.Groups[[int](($address-$line)/4)+1].Value.ToLowerInvariant()
}
$phases=@()
foreach($phase in @('LIVE1','LIVE2')){
 $p=Join-Path $root ('E004NQ_'+$phase+'.log')
 $raw=[IO.File]::ReadAllText($p,[Text.Encoding]::Unicode)
 if(-not $raw.Contains('===E004NQ_'+$phase+'_CSID1_END===')){throw ('E004NS_UNVERIFIED_SOURCE_PHASE '+$phase)}
 $o=[ordered]@{phase=$phase;csid0_wrapper_config=Reg $raw 0xacb6000;csid1_wrapper_config=Reg $raw 0xacb6004;csid0_ipp_cfg0=Reg $raw 0xacb7300;csid1=[ordered]@{}}
 foreach($key in $offsets.Keys){$o.csid1[$key]=Reg $raw (0xacb9000+[long]$offsets[$key])}
 $phases += [pscustomobject]$o
}
# These are unchanging configuration registers over the TWO real Windows rear
# recording windows; no live status/counter/packet/address registers included.
if(($phases[0]|ConvertTo-Json -Depth 5) -ne ($phases[1]|ConvertTo-Json -Depth 5).Replace('"LIVE2"','"LIVE1"')){
 throw 'E004NS_REAR_CSID1_CONFIG_NOT_STABLE_ACROSS_TWO_LIVE_PASSES'
}
$a=$phases[0]
if($a.csid0_wrapper_config -ne '0x00000001' -or
   $a.csid1_wrapper_config -ne '0x00000101' -or
   $a.csid0_ipp_cfg0 -ne '0x00000000' -or
   $a.csid1.rx_cfg0 -ne '0x10232103' -or
   $a.csid1.rx_cfg1 -ne '0x00000001' -or
   $a.csid1.ipp_cfg0 -ne '0x802b2000' -or
   $a.csid1.ipp_cfg1 -ne '0x00007241' -or
   $a.csid1.ipp_hcrop -ne '0x0fdf0000' -or
   $a.csid1.ipp_vcrop -ne '0x08ed0000' -or
   $a.csid1.ipp_format_measure_cfg1 -ne '0x08ee0fe0'){
 throw 'E004NS_REAR_HARDWARE_CSID1_IDENTITY_MISMATCH'
}
$r=[ordered]@{
 schema='sp11-e004ns-windows-rear-csid1-ipp-whitelisted-config-scalar-v1'
 origin='same-SP11 E004nq rear VideoRecord 3840x2160; private SP7 KD dd /p two live phases'
 register_origin='CSID1 base0x0acb9000; wrapper base0x0acb6000; read-only CONFIGURATION fields only'
 correction='0x388 is IPP_FORMAT_MEASURE_CFG1 (configured expected dimensions), NOT an independently observed hardware frame counter'
 original_sp7_KD_raw_windows_remain_private=$true
 no_optical_pixels_image_DMA_pointers_or_RAM_exported=$true
 phases=@($phases)
}
[pscustomobject]$r|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $dst -Encoding UTF8
Write-Output ('E004NS_CSID1_TWO_WINDOWS_LIVE_PASSES_CONFIG_MATCH_PASS fields='+$offsets.Count+' bytes='+(Get-Item $dst).Length)
foreach($key in $offsets.Keys){Write-Output ($key+'='+$a.csid1[$key])}
