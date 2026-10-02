param([ValidatePattern('^E011BX-[0-9]{8}-[0-9]{4}[A-Z]$')][string]$Identity)
$ErrorActionPreference='Stop'
$dir=Join-Path $env:USERPROFILE ('Documents\SP11CameraPrivate\'+$Identity)
$cap=Join-Path $dir 'capture'
$m=Get-Content (Join-Path $dir 'PRE-RUNTIME-SAFE.json') -Raw|ConvertFrom-Json
$raw=(Get-Content (Join-Path $dir 'cdb-observer.raw') -Raw).Replace(''+[char]96,'')
if($raw -match 'Syntax error|Malformed|Numeric expression missing|Couldn.t resolve|Unable to|Command file execution failed'){throw 'observer diagnostics'}
$match=[regex]::Matches($raw,'(?m)^E011BX_MODULE_BASE base=([0-9a-fA-F]+)')
if($match.Count-ne1){throw 'module-base event count'}
$base=[Convert]::ToUInt64($match[0].Groups[1].Value,16)
foreach($r in $m.ranges){
 $f=Join-Path $cap ('CODE_'+$r.name+'.bin')
 if(-not(Test-Path $f) -or (Get-Item $f).Length-ne$r.bytes){throw ('missing/wrong-size code '+$r.name)}
 if((Get-FileHash $f -Algorithm SHA256).Hash.ToLowerInvariant()-ne$r.sha256){throw ('loaded source mismatch '+$r.name)}
}
foreach($r in $m.tables){
 $bytes=[IO.File]::ReadAllBytes((Join-Path $cap ('TABLE_'+$r.name+'.bin')))
 if($bytes.Length-ne8*$r.target_rvas.Count){throw 'table size'}
 for($i=0;$i-lt$r.target_rvas.Count;$i++){
  if(([BitConverter]::ToUInt64($bytes,8*$i)-$base)-ne$r.target_rvas[$i]){throw 'loaded vtable target'}
 }
}
$out=[ordered]@{experiment='E011BX';identity=$Identity;status='PASS_LOADED_RANGES_AND_TABLE';
 loaded_code_ranges=$m.ranges.Count;loaded_tables=$m.tables.Count;
 qualified_UTC=[DateTimeOffset]::UtcNow.ToString('o');before_Start=$true;native_rear_runtime_allowed=$false}
$path=Join-Path $dir 'LOADED-QUALIFICATION-SAFE.json'
$stream=[IO.File]::Open($path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try{$bytes=[Text.Encoding]::UTF8.GetBytes(($out|ConvertTo-Json -Depth 8));$stream.Write($bytes,0,$bytes.Length)}finally{$stream.Dispose()}
$out|ConvertTo-Json -Depth 8 -Compress
