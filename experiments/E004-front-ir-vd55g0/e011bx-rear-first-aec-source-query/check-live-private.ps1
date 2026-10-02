$ErrorActionPreference='Stop'
$id='E011BX-20261002-0030A';$d=Join-Path $env:USERPROFILE ('Documents\SP11CameraPrivate\'+$id);$cap=Join-Path $d 'capture'
function Check($b,$s){if(-not$b){throw $s}}
function Equal($a,$b){[Convert]::ToBase64String($a)-eq[Convert]::ToBase64String($b)}
function Bytes($n){[IO.File]::ReadAllBytes((Join-Path $cap ($n+'.bin')))}
function Slice($b,$at,$n){[byte[]]$b[$at..($at+$n-1)]}
$raw=(Get-Content (Join-Path $d 'cdb-observer.raw') -Raw).Replace(''+[char]96,'')
Check ($raw-notmatch 'Syntax error|Malformed|Numeric expression missing|Couldn.t resolve|Unable to|Command file execution failed') 'observer diagnostics'
$events=@{}
foreach($tag in @('NAMED','INIT','INITAFTER','ENVELOPE','QUERY','QUERYAFTER','GETTER','GETTERAFTER','FIRST','FIRSTAFTER','PUBLISH')){
 $rows=[regex]::Matches($raw,'(?m)^E011BX_'+$tag+' (.+)$');$items=@()
 foreach($row in $rows){$item=@{};foreach($kv in [regex]::Matches($row.Groups[1].Value,'([A-Za-z][A-Za-z0-9]*)=([0-9a-fA-F]+)')){$item[$kv.Groups[1].Value]=$kv.Groups[2].Value};$items+=$item}
 $events[$tag]=$items
}
function Hex($e,$k){[Convert]::ToUInt64($e[$k],16)}
function Dec($e,$k){[Convert]::ToUInt64($e[$k],10)}
foreach($tag in @('NAMED','INIT','INITAFTER')){Check ($events[$tag].Count-eq4) ('event count '+$tag)}
foreach($tag in @('QUERY','QUERYAFTER','GETTER','GETTERAFTER')){Check ($events[$tag].Count-eq2) ('event count '+$tag)}
foreach($tag in @('ENVELOPE','FIRST','FIRSTAFTER','PUBLISH')){Check ($events[$tag].Count-eq1) ('event count '+$tag)}
$first=$events.FIRST[0];$after=$events.FIRSTAFTER[0];$pub=$events.PUBLISH[0]
Check ((Hex $first 'out')-eq(Hex $after 'out') -and (Hex $after 'out')-eq(Hex $pub 'src')) 'first publication pointer'
Check ((Hex $first 'tid')-eq(Hex $after 'tid') -and (Hex $after 'tid')-eq(Hex $pub 'tid')) 'first thread'
Check ((Hex $pub 'tag')-eq0x5000001c -and (Dec $pub 'bytes')-eq2072) 'publication type/size'
$frame=Bytes 'FRAME';$frameAfter=Bytes 'FRAME_AFTER';$stats=Bytes 'FRAME_STATS';$output=Bytes 'FIRST_OUT';$published=Bytes 'PUBLISH_OUT'
Check ($frame.Length-eq1880 -and (Equal $frame $frameAfter)) 'source frame unchanged'
Check ($stats.Length-eq92 -and (Equal $stats (Slice $frame 424 92))) 'first stats region'
Check ($output.Length-eq2072 -and (Equal $output $published)) 'first publication full bytes'
Check (Equal (Slice $output 48 12) (Slice $stats 68 12)) 'primary source conversion'
$expected=Get-Content (Join-Path $d 'SOURCE-EXPECTED.private.json') -Raw|ConvertFrom-Json
$metaMatches=0
for($i=1;$i-le4;$i++){
 $n='{0:D2}' -f $i;$obj=Bytes ('NAMED'+$n+'_OBJECT');$arr=Bytes ('NAMED'+$n+'_ARRAY')
 Check ($obj.Length-eq384 -and $arr.Length-eq480) 'named source sizes'
 $matched=$false
 foreach($candidate in $expected){
  $pass=$true
  foreach($f in $candidate.fields.PSObject.Properties){
   [byte[]]$want=for($j=0;$j-lt$f.Value.Length;$j+=2){[Convert]::ToByte($f.Value.Substring($j,2),16)}
   if(-not(Equal (Slice $obj ([int]$f.Name) $want.Length) $want)){$pass=$false}
  }
  if($pass){$matched=$true}
 }
 Check $matched 'typed source metadata';$metaMatches++
}
for($i=1;$i-le2;$i++){
 $n='{0:D2}' -f $i;$q=$events.QUERY[$i-1];$qa=$events.QUERYAFTER[$i-1];$g=$events.GETTER[$i-1];$ga=$events.GETTERAFTER[$i-1]
 Check ((Dec $q 'selector')-eq@(12,20)[$i-1]) 'both primary selectors'
 Check ((Dec $q 'type')-eq@(10,21)[$i-1] -and (Dec $qa 'type')-eq@(10,21)[$i-1]) 'typed result'
 Check ((Dec $q 'allocated')-eq92 -and (Dec $qa 'written')-eq92 -and (Hex $qa 'status')-eq0 -and (Hex $ga 'result')-eq1) 'complete successful returns'
 Check ((Hex $q 'callbackRVA')-eq0x372e40) 'actual direct callback'
 Check ((Hex $q 'out')-eq(Hex $qa 'out') -and (Hex $qa 'out')-eq(Hex $g 'out') -and (Hex $g 'out')-eq(Hex $first 'frame')+424) 'primary query frame pointer'
 $cache=Bytes ('GETTER'+$n+'_CACHE');$cacheAfter=Bytes ('GETTERAFTER'+$n+'_CACHE');$produced=Bytes ('QUERYAFTER'+$n+'_OUT');$got=Bytes ('GETTERAFTER'+$n+'_OUT')
 Check ($cache.Length-eq120 -and (Equal $cache $cacheAfter)) 'source cache unchanged'
 Check ((Equal $produced $got) -and (Equal $produced $stats)) 'full typed result frame equality'
 Check (Equal (Slice $cache 20 12) (Slice $produced 68 12)) 'getter cache weights'
}
$log=Get-Content (Join-Path $env:USERPROFILE ('Documents\'+$id+'-holder.log')) -Raw
Check (([regex]::Matches($log,'START_BEGIN')).Count-eq1 -and $log.Contains('START_STATUS=Success') -and $log.Contains('STOP_PASS') -and $log.Contains('E011BX_HOLDER_END')) 'one Start/Stop completion'
$handles=[int]([regex]::Match($log,'STOP_PASS valid_4k_handles=(\d+)').Groups[1].Value);Check ($handles-ge10) 'handle count'
$o=[ordered]@{experiment='E011BX';attempt=$id;status='PASS_WINDOWS_BOUNDED_TYPED_QUERY_FIRST_FRAME_CHECK';named_source_metadata_matches=$metaMatches;full_typed_queries=2;getter_returns=2;written_bytes_each=92;first_payload_bytes=2072;valid_4k_handles=$handles;camera_Starts=1;observer_diagnostics=0;independent_Linux_full_validation_pending=$true;actual_opened_filename_closed=$false;native_rear_runtime_allowed=$false}
$o|ConvertTo-Json -Depth 8|Set-Content (Join-Path $d 'WINDOWS-VALIDATION-SAFE.json')
$o|ConvertTo-Json -Depth 8 -Compress
