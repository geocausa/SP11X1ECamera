$ErrorActionPreference='Stop'
$root='C:\Users\SurfacePro7\Documents\KDNET\Codex\E004NQ-REAR-PHYSICAL-20260923'
$dest=Join-Path $root 'E004NR-REAR-WM-SCALAR-WHITELIST.json'
if(Test-Path $dest){throw 'E004NR_WHITELIST_ALREADY_EXPORTED'}
$line=[regex]'(?im)^00000000\x60([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]*\r?$'
$chosen=[ordered]@{
 wm_config=0x00
 frame_increment=0x08
 image_geometry=0x0c
 image_cfg1=0x10
 wm_stride=0x14
 packer_config=0x18
 bandwidth_limit=0x1c
 irq_subsample_period=0x30
 irq_subsample_pattern=0x34
 frame_drop_period=0x38
 frame_drop_pattern=0x3c
 metadata_config=0x44
 output_mode_config=0x48
 statistics_ctrl=0x4c
 secondary_ctrl=0x50
 lossy_threshold0=0x54
 lossy_threshold1=0x58
}
$all=[ordered]@{
 schema='sp11-e004nr-rear-oem-Windows-VFE1-output-WM-safe-scalar-v1'
 source='private SP7 KD E004nq original dd /p live phases, only explicitly whitelisted safe configuration dwords'
 exclusions='no image_addr +0x04; no metadata_addr +0x40; no DDR/IOVA/RAM/frame addresses; no image/pixel/thumbnail data'
 phases=@()
}
foreach($p in @('LIVE1','LIVE2')){
 $s=[IO.File]::ReadAllText((Join-Path $root ('E004NQ_'+$p+'.log')),[Text.Encoding]::Unicode)
 $block=@()
 foreach($wm in @(0,1,2,3,11,12,13,14,16,18)){
  $base=[long]0xac71000+0xe00+0x100*$wm;$v=[ordered]@{wm=$wm}
  foreach($key in $chosen.Keys){
   $addr=$base+[long]$chosen[$key];$rounded=$addr-($addr%16)
   $m=[regex]::Match($s,'(?im)^00000000\x60'+('{0:x8}' -f $rounded)+'[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})')
   if(-not $m.Success){throw ('E004NR_REGISTER_MISSING '+$p+' '+$wm+' '+$key)}
   $v[$key]='0x'+$m.Groups[[int](($addr-$rounded)/4)+1].Value.ToLowerInvariant()
  }
  if($v.wm_config -eq '0x00000000'){throw ('E004NR_WM_INACTIVE '+$p+' '+$wm)}
  $block += [pscustomobject]$v
 }
 $all.phases += [pscustomobject]@{phase=$p;write_masters=@($block)}
}
foreach($wm in @(0,1,2,3,11,12,13,14,16,18)){
 $a=@($all.phases[0].write_masters|Where-Object {$_.wm -eq $wm})[0]
 $b=@($all.phases[1].write_masters|Where-Object {$_.wm -eq $wm})[0]
 foreach($key in $chosen.Keys){if($a.$key -ne $b.$key){throw ('E004NR_UNSTABLE_STATIC_CONFIG '+$wm+' '+$key)}}
}
$out=([pscustomobject]$all|ConvertTo-Json -Depth 8)
if($out.Contains('"image_addr":') -or $out.Contains('"metadata_addr":')){throw 'E004NR_PRIVATE_IMAGE_POINTER_LEAK'}
Set-Content -LiteralPath $dest -Value $out -Encoding UTF8
Write-Output ('E004NR_REAR_VFE1_OUTPUT_SAFE_CONFIGURATION_WM0_1_2_3_AND_STATS_BOTH_PHASES_MATCH PASS bytes='+(Get-Item $dest).Length)
foreach($wm in @(0,1,2,3)){$x=$all.phases[0].write_masters[$wm];Write-Output ('WM'+$wm+' frame_increment='+$x.frame_increment+' img_geometry='+$x.image_geometry+' stride='+$x.wm_stride+' image_cfg1='+$x.image_cfg1+' meta_cfg='+$x.metadata_config+' mode='+$x.output_mode_config+' packer='+$x.packer_config)}
