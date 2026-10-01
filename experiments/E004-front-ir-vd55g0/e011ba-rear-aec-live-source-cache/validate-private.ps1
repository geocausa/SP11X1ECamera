param([ValidatePattern('^E011BA-[0-9]{8}-[0-9]{4}[A-Z]$')][string]$Identity,[switch]$QualificationOnly)
$ErrorActionPreference='Stop'
$p='C:\Users\Geoca\Documents\SP11CameraPrivate\'+$Identity
$b='C:\Users\Geoca\Documents\'+$Identity
$t=Get-Content ($p+'\cdb-observer.raw') -Raw
function Ptr([string]$s){[Convert]::ToUInt64($s.Replace([string][char]96,''),16)}
function Record([string]$name,[int]$size){$r=[IO.File]::ReadAllBytes($p+'\capture\'+$name+'.bin');if($r.Length-ne$size){throw 'record length mismatch'};return ,$r}
function Eq($l,$r){if($l.Length-ne$r.Length){return $false};for($i=0;$i-lt$l.Length;$i++){if($l[$i]-ne$r[$i]){return $false}};return $true}
function Events([string]$name){@([regex]::Matches($t,('(?m)^E011BA_'+$name+' ([^\r\n]+)'))|ForEach-Object{$d=@{};foreach($m in [regex]::Matches($_.Groups[1].Value,'([A-Za-z]+)=([0-9a-fA-F\x60]+)')){$d[$m.Groups[1].Value]=$m.Groups[2].Value};$d})}
$e=@(Events 'MODULE_BASE');if($e.Count-ne1){throw 'module base absent'};$mb=Ptr $e[0].base
$prep=Get-Content ($p+'\PREPARE-SAFE.json') -Raw|ConvertFrom-Json
foreach($code in $prep.code_ranges){$f=$p+'\capture\CODE_'+$code.name+'.bin';if((Get-Item $f).Length-ne$code.bytes -or (Get-FileHash $f -Algorithm SHA256).Hash.ToLowerInvariant()-ne$code.sha256){throw ('loaded code mismatch '+$code.name)}}
foreach($tab in $prep.tables){$r=Record ('TABLE_'+$tab.name) (8*$tab.target_rvas.Count);for($i=0;$i-lt$tab.target_rvas.Count;$i++){if([BitConverter]::ToUInt64($r,8*$i)-$mb-ne$tab.target_rvas[$i]){throw 'loaded table mismatch'}}}
if($t-match'Syntax error|Memory access error|Couldn.t resolve|E011BA_AUTHORITY_FAIL'){throw 'observer diagnostic'}
if($QualificationOnly){
 $q=[ordered]@{experiment='E011BA';identity=$Identity;status='PASS_LOADED_CODE_STATIC_TABLES';UTC=[DateTime]::UtcNow.ToString('o');loaded_code_ranges=$prep.code_ranges.Count;loaded_tables=$prep.tables.Count;private_bytes_exported=$false}
 $q|ConvertTo-Json|Set-Content ($p+'\LOADED-QUALIFICATION-SAFE.json');$q|ConvertTo-Json;return
}
$name=@(Events 'NAME');$ret=@(Events 'NAMERET');$store=@(Events 'NAMESTORE');$cfg=@(Events 'CONFIG');$cr=@(Events 'CONFIGRET');$init=@(Events 'INIT');$ia=@(Events 'INITAFTER')
if($name.Count-lt1 -or $name.Count-gt4 -or $ret.Count-ne$name.Count -or $store.Count-ne$name.Count -or $cfg.Count-lt1 -or $cfg.Count-gt4 -or $cr.Count-ne$cfg.Count -or $init.Count-lt1 -or $init.Count-gt4 -or $ia.Count-ne$init.Count){throw 'event counts outside scope'}
foreach($e in $name){
 $n=[int]$e.n;$r=$ret[$n-1];$s=$store[$n-1]
 $text=Record ('NAME{0:00}_TEXT'-f$n) 32
 if([Text.Encoding]::ASCII.GetString($text).Split([char]0)[0]-ne'aecxhwstatsconfig'){throw 'actual named source mismatch'}
 if($r.tidMatch-ne'1' -or $r.bankMatch-ne'1' -or $s.tidMatch-ne'1' -or $s.bankMatch-ne'1' -or $s.payloadMatch-ne'1' -or (Ptr $r.object)+0x120-ne(Ptr $r.payload) -or $r.payload-ne$s.payload){throw 'lookup return/store join mismatch'}
 $obj=Record ('NAMERET{0:00}_OBJECT'-f$n) 384;$pay=Record ('NAMERET{0:00}_PAYLOAD'-f$n) 96;$after=Record ('NAMESTORE{0:00}_PAYLOAD'-f$n) 96
 if(-not(Eq $pay $after) -or -not(Eq $obj[288..383] $pay) -or [BitConverter]::ToUInt64($pay,56)-ne(Ptr $s.cache)){throw 'payload/cache changed at store'}
 $holder=Record ('NAMESTORE{0:00}_HOLDER'-f$n) 8;if([BitConverter]::ToUInt64($holder,0)-ne(Ptr $s.payload)){throw 'holder mismatch'}
}
foreach($e in $cfg){
 $n=[int]$e.n;$r=$cr[$n-1]
 if((Ptr $e.bank)-ne(Ptr $e.core)+8 -or (Ptr $e.target)-$mb-ne0x3a8730 -or (Ptr $e.publicSlot)-$mb-ne0x3a8730 -or (Ptr $e.coreSlot)-$mb-ne0x3af540 -or (Ptr $e.bankSlot)-$mb-ne0x3aebb0 -or (Ptr $e.coreTable)-$mb-ne0x1338428 -or (Ptr $e.bankTable)-$mb-ne0x13383b8){throw 'actual interface authority mismatch'}
 if($r.tidMatch-ne'1' -or $r.dataMatch-ne'1' -or $r.payloadMatch-ne'1' -or $r.bank-ne$e.bank -or $r.payload-ne$e.named){throw 'dispatch return mismatch'}
 $joined=@($store|Where-Object{$_.bank-eq$e.bank -and $_.payload-eq$r.payload -and $_.cache-eq$r.cache})
 if($joined.Count-lt1){throw 'no named lookup ownership join'}
 $ni=[int]$joined[-1].n
 $pay=Record ('CONFIGRET{0:00}_PAYLOAD'-f$n) 96;$data=Record ('CONFIGRET{0:00}_DATA'-f$n) 248
 if([BitConverter]::ToUInt64($data,240)-ne(Ptr $r.payload) -or [BitConverter]::ToUInt64($pay,56)-ne(Ptr $r.cache)){throw 'returned fields mismatch'}
 $grid=Record ('CONFIGRET{0:00}_GRID'-f$n) 120;$original=Record ('NAMERET{0:00}_GRID'-f$ni) 120
 if(-not(Eq $grid[20..31] $original[20..31])){throw 'selected weights changed'}
}
$elementOffsets=@();$firstGridJoins=0
foreach($e in $init){
 $n=[int]$e.n;$r=$ia[$n-1]
 if((Ptr $e.table)-$mb-ne0x13381a0 -or $r.tidMatch-ne'1' -or $r.selfMatch-ne'1' -or $r.cacheMatch-ne'1'){throw 'grid authority/retention mismatch'}
 $joined=@($cr|Where-Object{$d=[decimal](Ptr $e.cache)-[decimal](Ptr $_.cache);$d-ge0 -and $d-lt480 -and ($d%120)-eq0});if($joined.Count-lt1){throw 'no Configure-array-to-Init element join'}
 $offset=[int]([decimal](Ptr $e.cache)-[decimal](Ptr $joined[-1].cache));$elementOffsets+=$offset
 $ci=[int]$joined[-1].n
 $cache=Record ('INIT{0:00}_CACHE'-f$n) 120;$after=Record ('INITAFTER{0:00}_CACHE'-f$n) 120;$obj=Record ('INITAFTER{0:00}_SELF'-f$n) 48
 $cg=Record ('CONFIGRET{0:00}_GRID'-f$ci) 120
 if(-not(Eq $cache $after) -or [BitConverter]::ToUInt64($obj,24)-ne(Ptr $e.cache) ){throw 'cache retained bytes mismatch'}
 if($offset-eq0){if(-not(Eq $cache[20..31] $cg[20..31])){throw 'first grid weights mismatch'};$firstGridJoins++}
}
if($firstGridJoins-lt1){throw 'no first-grid join'}
$holder=Get-Content ($b+'-holder.log') -Raw
$starts=[regex]::Matches($holder,'START_BEGIN').Count;$stops=[regex]::Matches($holder,'STOP_PASS valid_4k_handles=(\d+)')
if($starts-ne1 -or $stops.Count-ne1 -or -not(Test-Path ($b+'-DONE'))){throw 'single Start/Stop incomplete'}
$q=Get-Content ($p+'\LOADED-QUALIFICATION-SAFE.json') -Raw|ConvertFrom-Json
$stamp=[regex]::Match($holder,'(?m)^(\S+) START_BEGIN')
if(-not$stamp.Success -or [DateTime]$q.UTC-ge[DateTime]$stamp.Groups[1].Value){throw 'qualification must precede Start'}
$result=[ordered]@{experiment='E011BA';identity=$Identity;status='PASS_LIVE_NAMED_PAYLOAD_CONFIG_GRID_CACHE_JOIN';named_lookup_cases=$name.Count;Configure_cases=$cfg.Count;grid_Init_cases=$init.Count;actual_callback_tables_qualified_before_dispatch=$true;loaded_code_and_static_tables_qualified_before_Start=$true;named_module_object_payload_bank_store_join=$true;Configure_returned_data_to_named_payload_join=$true;Configure_array_to_grid_Init_retained_pointer_join=$true;first_grid_Config_Init_weight_joins=$firstGridJoins;grid_Init_array_element_byte_offsets=$elementOffsets;other_grid_numeric_source_mapping_closed=$false;cache_120_bytes_preserved_through_Init=$true;selected_weight_bytes=12;camera_starts=$starts;valid_4k_frame_handles=[int]$stops[0].Groups[1].Value;independent_tuning_weights_comparison='PENDING_LINUX_RECHECK';exact_loaded_tuning_filename_closed=$false;full_profile_materialization_closed=$false;cold_metadata_bridge_closed=$false;native_rear_runtime_allowed=$false;private_bytes_exported=$false}
$result.record_hashes=@(Get-ChildItem ($p+'\capture') -File|Sort-Object Name|ForEach-Object{[ordered]@{name=$_.Name;bytes=$_.Length;sha256=(Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}})
$result|ConvertTo-Json -Depth 5|Set-Content ($p+'\VALIDATION-SAFE.json')
$s=[ordered]@{};foreach($k in $result.Keys){if($k-ne'record_hashes'){$s[$k]=$result[$k]}};$s|ConvertTo-Json -Depth 5
