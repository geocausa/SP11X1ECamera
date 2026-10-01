param([ValidatePattern('^E011BV-[0-9]{8}-[0-9]{4}[A-Z]$')][string]$Identity,[ValidateSet('Qualify','Final')][string]$Mode='Final')
$ErrorActionPreference='Stop'
$dir=Join-Path $env:USERPROFILE ('Documents\SP11CameraPrivate\'+$Identity)
$cap=Join-Path $dir 'capture'
$m=Get-Content (Join-Path $dir 'PRE-RUNTIME-SAFE.json') -Raw|ConvertFrom-Json
$qualified=@()
foreach($r in $m.ranges){
 $f=Join-Path $cap ('CODE_'+$r.name+'.bin')
 if(-not(Test-Path $f) -or (Get-Item $f).Length-ne$r.bytes){throw ('missing/wrong-size code qualification '+$r.name)}
 $h=(Get-FileHash $f -Algorithm SHA256).Hash.ToLowerInvariant()
 if($h-ne$r.sha256){throw ('loaded source mismatch '+$r.name)}
 $qualified+= [pscustomobject]@{name=$r.name;rva=$r.rva;bytes=$r.bytes;match=$true}
}
$q=[ordered]@{experiment='E011BV';attempt=$Identity;status='PASS_LOADED_RANGES';loaded_ranges=$qualified;range_count=$qualified.Count;qualified_UTC=[DateTimeOffset]::UtcNow.ToString('o');before_Start_required=$true;native_rear_runtime_allowed=$false}
$q|ConvertTo-Json -Depth 8|Set-Content (Join-Path $dir 'LOADED-QUALIFICATION-SAFE.json')
if($Mode-eq'Qualify'){$q|ConvertTo-Json -Depth 8 -Compress;return}
$raw=Get-Content (Join-Path $dir 'cdb-observer.raw') -Raw
$events=@{}
foreach($tag in @('FIRST','SECOND','PUBLISH','PUBLISH_AFTER','WRITE','WRITE_AFTER','READER','READ','READ_AFTER','COLD','COLD_AFTER')){
 $matches=[regex]::Matches($raw,'(?m)^E011BV_'+$tag+' (.+)$')
 if($matches.Count-ne1){throw ('expected one event '+$tag+' got '+$matches.Count)}
 $fields=@{}
 foreach($kv in [regex]::Matches($matches[0].Groups[1].Value,'([A-Za-z][A-Za-z0-9]*)=([0-9a-fA-F`]+)')){$fields[$kv.Groups[1].Value]=$kv.Groups[2].Value.Replace(''+[char]96,'')}
 $events[$tag]=$fields
}
function Hex($event,$key){$v=$events[$event][$key];if(-not$v){throw ('missing event field '+$event+' '+$key)};[Convert]::ToUInt64($v,16)}
function Dec($event,$key){$v=$events[$event][$key];if(-not$v){throw ('missing event field '+$event+' '+$key)};[Convert]::ToUInt64($v,10)}
function Check([bool]$b,[string]$s){if(-not$b){throw $s}}
Check ((Dec 'PUBLISH' 'bytes')-eq2072 -and (Hex 'PUBLISH' 'tag')-eq0x5000001c) 'publication tag/length'
Check ((Dec 'WRITE' 'bytes')-eq2072 -and (Hex 'WRITE' 'tag')-eq0x5000001c) 'write tag/length'
Check ((Hex 'READ' 'tag')-eq0x5000001c -and (Hex 'READER' 'tag')-eq0x5000001c) 'read property'
Check ((Dec 'COLD' 'bytes')-eq2072) 'cold length'
Check ((Hex 'FIRST' 'out')-eq(Hex 'PUBLISH' 'src') -and (Dec 'PUBLISH' 'firstPtrMatch')-eq1 -and (Dec 'PUBLISH' 'firstTidMatch')-eq1) 'first publication lineage'
Check ((Hex 'PUBLISH' 'src')-eq(Hex 'WRITE' 'src') -and (Hex 'PUBLISH' 'tid')-eq(Hex 'WRITE' 'tid')) 'publisher writer lineage'
Check ((Hex 'WRITE' 'store')-eq(Hex 'READ' 'store') -and (Dec 'READ' 'sameStore')-eq1) 'metadata store identity'
Check ((Hex 'READ' 'tid')-eq(Hex 'READER' 'tid') -and (Hex 'READ_AFTER' 'tid')-eq(Hex 'READ' 'tid')) 'reader API call return'
Check ((Hex 'READ_AFTER' 'src')-eq(Hex 'COLD' 'src') -and (Dec 'COLD' 'metadataSrcMatch')-eq1 -and (Dec 'COLD' 'readerTidMatch')-eq1) 'cold source pointer'
Check ((Hex 'COLD_AFTER' 'tid')-eq(Hex 'COLD' 'tid') -and (Dec 'COLD_AFTER' 'returnedDstMatch')-eq1) 'cold return lineage'
Check ((Hex 'WRITE' 'callerRVA')-eq0x5d6ef8 -and (Hex 'READ' 'callerRVA')-eq0x5d54d0) 'actual API callers'
Check ((Hex 'WRITE_AFTER' 'result')-eq0 -and (Hex 'PUBLISH_AFTER' 'result')-eq0) 'original successful write returns'
$sizes=@{FIRST_OUT=2072;SECOND_OUT=2072;PUBLISH_OUT=2072;PUBLISH_NODE=1280;PUBLISH_POOL=720;WRITE_OUT=2072;WRITE_STORE=128;WRITE_STORE_AFTER=128;READER_NODE=1280;READER_POOL=720;READ_STORE=128;READ_OUT=2072;COLD_SOURCE=2072;COLD_BEFORE=2072;COLD_AFTER=2072;COLD_SOURCE_AFTER=2072}
$bytes=@{};foreach($n in $sizes.Keys){$b=[IO.File]::ReadAllBytes((Join-Path $cap ($n+'.bin')));Check ($b.Length-eq$sizes[$n]) ('size '+$n);$bytes[$n]=$b}
$root=[Convert]::ToBase64String($bytes.FIRST_OUT)
foreach($n in @('PUBLISH_OUT','WRITE_OUT','READ_OUT','COLD_SOURCE','COLD_AFTER','COLD_SOURCE_AFTER')){Check ([Convert]::ToBase64String($bytes[$n])-eq$root) ('full payload mismatch '+$n)}
$pubPool=[BitConverter]::ToUInt64($bytes.PUBLISH_NODE,1200)
$readPool=[BitConverter]::ToUInt64($bytes.READER_NODE,1200)
Check ($pubPool-eq$readPool -and $readPool-eq(Hex 'READER' 'pool')) 'actual UsecasePool identity'
$holder=Get-Content (Join-Path $env:USERPROFILE ('Documents\'+$Identity+'-holder.log')) -Raw
Check (([regex]::Matches($holder,'START_BEGIN')).Count-eq1 -and $holder.Contains('START_STATUS=Success') -and $holder.Contains('STOP_PASS') -and $holder.Contains('E011BV_HOLDER_END')) 'bounded camera holder completion'
$h=[regex]::Match($holder,'STOP_PASS valid_4k_handles=(\d+)');Check $h.Success 'handle count';$handles=[int]$h.Groups[1].Value;Check ($handles-ge10) 'insufficient handles'
$out=[ordered]@{experiment='E011BV';attempt=$Identity;status='PASS_BOUNDED_LIVE_COLD_METADATA_JOIN';loaded_code_ranges_match=$qualified.Count;live_events=$events.Count;private_payload_records=$sizes.Count;private_payload_bytes=($sizes.Values|Measure-Object -Sum).Sum;valid_4k_handles=$handles;camera_starts=1;successful_stop=$true;property_ID='0x5000001C';configuration_bytes=2072;first_output_publication_pointer_join=$true;writer_reader_UsecasePool_identity=$true;writer_reader_store_identity=$true;reader_cold_source_pointer_join=$true;full2072_payload_chain_equal=$true;separate_second_configuration_equal=([Convert]::ToBase64String($bytes.SECOND_OUT)-eq$root);original_store_write_read_executed=$true;numeric_source_initialization_closed=$false;actual_tuning_file_profile_identity_closed=$false;native_rear_runtime_allowed=$false;originals_exported=$false;optical_images_saved=$false}
$out|ConvertTo-Json -Depth 8|Set-Content (Join-Path $dir 'VALIDATION-SAFE.json')
$out|ConvertTo-Json -Depth 8 -Compress
