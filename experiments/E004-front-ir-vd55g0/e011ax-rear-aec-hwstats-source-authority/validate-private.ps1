param([ValidatePattern('^E011AX-[0-9]{8}-[0-9]{4}[A-Z]$')][string]$Identity)
$ErrorActionPreference='Stop'
$p='C:\Users\Geoca\Documents\SP11CameraPrivate\'+$Identity
$b='C:\Users\Geoca\Documents\'+$Identity
$t=Get-Content ($p+'\cdb-observer.raw') -Raw
$holder=Get-Content ($b+'-holder.log') -Raw
function Record([string]$name,[int]$size){$r=[IO.File]::ReadAllBytes($p+'\capture\'+$name+'.bin');if($r.Length-ne$size){throw 'record length mismatch'};return ,$r}
function EqualSpan($left,[int]$lo,$right,[int]$ro,[int]$size){for($i=0;$i-lt$size;$i++){if($left[$lo+$i]-ne$right[$ro+$i]){return $false}};return $true}
function HexValue([string]$s){return [Convert]::ToUInt64($s.Replace('`',''),16)}
function Event([string]$name){return @([regex]::Matches($t,('(?m)^E011AX_'+$name+' ([^\r\n]+)')) | ForEach-Object {$d=@{};foreach($m in [regex]::Matches($_.Groups[1].Value,'([A-Za-z]+)=([0-9a-fA-F`]+)')){$d[$m.Groups[1].Value]=$m.Groups[2].Value};$d})}
$baseMatches=[regex]::Matches($t,'(?m)^E011AX_MODULE_BASE base=([0-9a-fA-F`]+)')
if($baseMatches.Count-ne1){throw 'module base qualification absent'}
$moduleBase=HexValue $baseMatches[0].Groups[1].Value
$prepare=Get-Content ($p+'\PREPARE-SAFE.json') -Raw|ConvertFrom-Json
foreach($code in $prepare.code_ranges){$file=$p+'\capture\CODE_'+$code.name+'.bin';if((Get-Item $file).Length-ne$code.bytes -or (Get-FileHash $file -Algorithm SHA256).Hash.ToLowerInvariant()-ne$code.sha256){throw 'loaded code hash mismatch'}}
$table=Record 'CODE_TABLE' 24;for($i=0;$i-lt3;$i++){if([BitConverter]::ToUInt64($table,$i*8)-$moduleBase-ne$prepare.grid_vtable_first_three_target_rvas[$i]){throw 'loaded grid table mismatch'}}
$init=@(Event 'INIT');$initAfter=@(Event 'INIT_AFTER');$get=@(Event 'GETTER');$getAfter=@(Event 'GETTER_AFTER');$consumer=@(Event 'CONSUMER');$consumerAfter=@(Event 'CONSUMER_AFTER');$callbacks=@(Event 'CALLBACK');$cold=@(Event 'COLD');$coldAfter=@(Event 'COLD_AFTER');$engine=@(Event 'ENGINE_QUERY')
if($init.Count-ne4 -or $get.Count-ne4 -or $consumer.Count-ne4 -or $callbacks.Count-ne1 -or $cold.Count-ne1 -or $engine.Count-ne1){throw 'unexpected event count'}
$initPass=0
foreach($e in $init){
 $n=[int]$e.n;$before=Record ('INIT{0:00}_SELF'-f$n) 48;$after=Record ('INITAFTER{0:00}_SELF'-f$n) 48
 $src=Record ('INIT{0:00}_CACHE'-f$n) 96;$srcAfter=Record ('INITAFTER{0:00}_CACHE'-f$n) 96
 if([BitConverter]::ToUInt64($after,24)-ne(HexValue $e.cache) -or -not(EqualSpan $src 0 $srcAfter 0 96)){throw 'init alias/cache mismatch'}
 $a=@($initAfter|Where-Object {[int]$_.n-eq$n});if($a.Count-ne1 -or $a[0].tidMatch-ne'1' -or $a[0].selfMatch-ne'1' -or $a[0].cacheMatch-ne'1'){throw 'init invocation mismatch'}
 $initPass++
}
$getterPass=0;$initializationJoins=0
foreach($e in $get){
 $n=[int]$e.n;$self=Record ('GETTER{0:00}_SELF'-f$n) 48;$src=Record ('GETTER{0:00}_CACHE'-f$n) 96;$srcAfter=Record ('GETTERAFTER{0:00}_CACHE'-f$n) 96;$out=Record ('GETTERAFTER{0:00}_OUT'-f$n) 92
 if([BitConverter]::ToUInt64($self,0)-$moduleBase-ne0x13381a0 -or [BitConverter]::ToUInt64($self,24)-ne(HexValue $e.cache)){throw 'getter live owner/interface mismatch'}
 if(-not(EqualSpan $src 0 $srcAfter 0 96) -or -not(EqualSpan $src 20 $out 68 12)){throw 'getter weight/copy mismatch'}
 $a=@($getAfter|Where-Object {[int]$_.n-eq$n});if($a.Count-ne1 -or $a[0].tidMatch-ne'1' -or $a[0].outputMatch-ne'1'){throw 'getter invocation mismatch'}
 $joined=@($init|Where-Object {$_.self-eq$e.self -and $_.cache-eq$e.cache})
 if($joined.Count-ne1){throw 'getter/init same-object cache lineage absent'}
 $ni=[int]$joined[0].n;$original=Record ('INIT{0:00}_CACHE'-f$ni) 96
 if(-not(EqualSpan $original 20 $src 20 12)){throw 'weights changed after observed init'}
 $initializationJoins++;$getterPass++
}
$callback=$callbacks[0];if($callback.count-ne'1'){throw 'unsupported descriptor count'}
$query=Record 'CALLBACK01_QUERY' 40;$desc=Record 'CALLBACK01_DESC' 24
if([BitConverter]::ToUInt32($query,0)-ne12 -or [BitConverter]::ToUInt32($query,32)-ne1 -or [BitConverter]::ToUInt64($desc,8)-ne92 -or [BitConverter]::ToUInt32($desc,16)-ne10){throw 'typed primary BG route mismatch'}
$payload=[BitConverter]::ToUInt64($desc,0)
$getter=@($get|Where-Object {(HexValue $_.output)-eq$payload -and $_.tid-eq$callback.tid});if($getter.Count-lt1){throw 'descriptor/getter lineage absent'}
$primary=@($consumer|Where-Object {(HexValue $_.frame)+0x1a8-eq$payload -and $_.tid-eq$callback.tid})
if($primary.Count-ne1){throw 'query/primary frame lineage absent'}
$pn=[int]$primary[0].n;$gn=[int]$getter[-1].n;$primaryFrame=Record ('CONSUMER{0:00}_FRAME'-f$pn) 92;$finalGetter=Record ('GETTERAFTER{0:00}_OUT'-f$gn) 92
if(-not(EqualSpan $primaryFrame 0 $finalGetter 0 92)){throw 'final BG getter/frame block mismatch'}
if((HexValue $cold[0].src)-eq(HexValue $primary[0].stats)){throw 'unexpected source bridge observation; reassess scope'}
$consumerPass=0
foreach($e in $consumer){
 $n=[int]$e.n;$frame=Record ('CONSUMER{0:00}_FRAME'-f$n) 92;$frameAfter=Record ('CONSUMERAFTER{0:00}_FRAME'-f$n) 92;$stats=Record ('CONSUMERAFTER{0:00}_STATS'-f$n) 128
 if(-not(EqualSpan $frame 0 $frameAfter 0 92) -or -not(EqualSpan $frame 68 $stats 48 12)){throw 'primary weight copy mismatch'}
 $a=@($consumerAfter|Where-Object {[int]$_.n-eq$n});if($a.Count-ne1 -or $a[0].tidMatch-ne'1' -or $a[0].frameMatch-ne'1' -or $a[0].statsMatch-ne'1'){throw 'consumer invocation mismatch'}
 $consumerPass++
}
$source=Record 'COLD_SOURCE' 2072;$sourceAfter=Record 'COLD_SOURCE_AFTER' 2072;$retained=Record 'COLD_AFTER' 2072
if($cold[0].bytes-ne'2072' -or $coldAfter.Count-ne1 -or $coldAfter[0].returnedDstMatch-ne'1' -or -not(EqualSpan $source 0 $retained 0 2072) -or -not(EqualSpan $source 0 $sourceAfter 0 2072)){throw 'cold copy mismatch'}
$pn=[int]$primary[0].n;$primaryStats=Record ('CONSUMERAFTER{0:00}_STATS'-f$pn) 128
if(-not(EqualSpan $primaryStats 48 $source 48 12)){throw 'cold/primary weights mismatch'}
$start=[regex]::Matches($holder,'START_BEGIN').Count;$stop=[regex]::Matches($holder,'STOP_PASS valid_4k_handles=(\d+)')
if($start-ne1 -or $stop.Count-ne1 -or -not(Test-Path ($b+'-DONE'))){throw 'single Start/clean Stop incomplete'}
if($t-match'Syntax error|Memory access error|Couldn.t resolve'){throw 'observer error detected'}
$result=[ordered]@{experiment='E011AX';attempt=$Identity;status='PASS_LIVE_BG_CACHE_LINEAGE_AND_COLD_COPY_METADATA_BRIDGE_OPEN';loaded_code_and_interface_qualified=$true;init_cases=$initPass;getter_cases=$getterPass;getter_to_init_same_object_joins=$initializationJoins;primary_consumer_cases=$consumerPass;primary_BG_selector=12;primary_output_type=10;primary_output_bytes=92;descriptor_getter_frame_same_pointer_and_thread=$true;primary_same_output_getter_writes=$getter.Count;last_primary_getter_index=$gn;final_getter_entire_92_byte_block_matches_primary_frame=$true;cold_copy_bytes=2072;cold_copy_and_source_preserved=$true;cold_matches_primary_weight_fields=$true;cold_source_same_pointer_as_primary_statistics=$false;cold_metadata_bridge_closed=$false;camera_starts=$start;valid_4k_frame_handles=[int]$stop[0].Groups[1].Value;cache_weights_already_present_at_grid_init=$true;numeric_initializer_closed=$false;cache_earlier_writer_closed=$false;whole_profile_authority_closed=$false;kernel_debugging=$false;BCD_changes=$false;private_bytes_exported=$false;native_Linux_rear_runtime_allowed=$false}
$qualification=Get-Content ($p+'\LOADED-QUALIFICATION-SAFE.json') -Raw|ConvertFrom-Json
$startTime=[regex]::Match($holder,'(?m)^(\S+) START_BEGIN')
if(-not$startTime.Success -or [DateTime]$qualification.UTC-ge[DateTime]$startTime.Groups[1].Value){throw 'loaded qualification not before Start'}
$result['code_qualification_before_Start_verified']=$true
$result['record_hashes']=@(Get-ChildItem ($p+'\capture') -File|Sort-Object Name|ForEach-Object {[ordered]@{name=$_.Name;bytes=$_.Length;sha256=(Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}})
$result|ConvertTo-Json -Depth 5 | Set-Content ($p+'\VALIDATION-SAFE.json')
$summary=[ordered]@{};foreach($key in $result.Keys){if($key-ne'record_hashes'){$summary[$key]=$result[$key]}};$summary|ConvertTo-Json -Depth 5
