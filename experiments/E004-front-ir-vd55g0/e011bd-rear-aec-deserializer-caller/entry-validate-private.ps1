param([ValidatePattern('^E011BD-[0-9]{8}-[0-9]{4}[A-Z]$')][string]$Identity)
$ErrorActionPreference='Stop'
$p='C:\Users\Geoca\Documents\SP11CameraPrivate\'+$Identity
$t=Get-Content ($p+'\cdb-observer.raw') -Raw
function Ptr([string]$s){[Convert]::ToUInt64($s.Replace([string][char]96,''),16)}
function Rec([string]$name,[int]$size){$r=[IO.File]::ReadAllBytes($p+'\capture\'+$name+'.bin');if($r.Length-ne$size){throw 'entry record size mismatch'};return ,$r}
function Events([string]$name){@([regex]::Matches($t,('(?m)^E011BD_'+$name+' ([^\r\n]+)'))|ForEach-Object{$d=@{};foreach($m in [regex]::Matches($_.Groups[1].Value,'([A-Za-z]+)=([0-9a-fA-F\x60]+)')){$d[$m.Groups[1].Value]=$m.Groups[2].Value};$d})}
$mb=Ptr (@(Events 'MODULE_BASE')[0].base)
$allEntries=@(Events 'ENTRY')
$entries=@($allEntries|Where-Object{$lv=if($_.lr){Ptr $_.lr}else{0};$lv-ge$mb -and $lv-lt$mb+0x1a00000})
if($entries.Count-lt1 -or $entries.Count-gt4){throw 'entry count outside scope'}
if($t-match'Syntax error|Memory access error|Couldn.t resolve|(?m)^E011BD_(CHILD_)?AUTHORITY_FAIL\s*$'){throw 'entry observer diagnostic'}
$one=0;$nonzero=0;$callers=@()
foreach($e in $entries){
 $n=[int]$e.n
 $obj=Rec ('ENTRY{0:00}_OBJECT'-f$n) 384
 $slot=Rec ('ENTRY{0:00}_SLOT'-f$n) 8
 $reader=Rec ('ENTRY{0:00}_READER'-f$n) 224
 $context=Rec ('ENTRY{0:00}_CONTEXT'-f$n) 64
 $root=Rec ('ENTRY{0:00}_ROOT'-f$n) 48
 $child=Rec ('ENTRY{0:00}_CHILD'-f$n) 224
 $grid=Rec ('ENTRY{0:00}_GRID'-f$n) 404
 if((Ptr $e.table)-$mb-ne0x1335598 -or (Ptr $e.slot)-$mb-ne0x123cc0 -or [BitConverter]::ToUInt64($obj,0)-$mb-ne0x1335598 -or [BitConverter]::ToUInt64($slot,0)-$mb-ne0x123cc0){throw 'entry instance slot mismatch'}
 if([BitConverter]::ToUInt32($reader,200)-ne48 -or [BitConverter]::ToUInt32($child,200)-ne404 -or [BitConverter]::ToUInt64($reader,0)-ne[BitConverter]::ToUInt64($child,0)){throw 'entry reader context mismatch'}
 if([BitConverter]::ToUInt32($root,24)-ne4 -or [BitConverter]::ToUInt32($root,28)-gt[BitConverter]::ToUInt32($context,24)){throw 'entry child bounds mismatch'}
 $a=[UInt64]::Parse($e.alignment)
 if($a-eq1){$one++};if($a-gt0){$nonzero++}
 $caller=[decimal](Ptr $e.lr)-[decimal]$mb
 if($caller-ge0x1080 -and $caller-lt0x1a00000){$null=Rec ('ENTRY{0:00}_CALLER'-f$n) 192;$callers+=('0x{0:x}'-f[UInt64]$caller)}
}
$result=[ordered]@{experiment='E011BD';identity=$Identity;status='PASS_LIVE_ORIGINAL_DESERIALIZER_ENTRY';entry_cases=$entries.Count;rejected_partial_entry_records=($allEntries.Count-$entries.Count);alignment_one_cases=$one;nonzero_alignment_cases=$nonzero;instance_slot_qualified_before_reader_use=$true;root_count_child_bounds_and_reader_context_match=$true;caller_return_RVAs=$callers;caller_source_alignment_policy_closed=$false;exact_loaded_tuning_filename_closed=$false;full_profile_materialization_closed=$false;native_rear_runtime_allowed=$false;private_bytes_exported=$false}
$result.record_hashes=@(Get-ChildItem ($p+'\capture') -File|Sort-Object Name|ForEach-Object{[ordered]@{name=$_.Name;bytes=$_.Length;sha256=(Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}})
$result|ConvertTo-Json -Depth 5|Set-Content ($p+'\ENTRY-SAFE.json')
$s=[ordered]@{};foreach($k in $result.Keys){if($k-ne'record_hashes'){$s[$k]=$result[$k]}};$s|ConvertTo-Json -Depth 5
