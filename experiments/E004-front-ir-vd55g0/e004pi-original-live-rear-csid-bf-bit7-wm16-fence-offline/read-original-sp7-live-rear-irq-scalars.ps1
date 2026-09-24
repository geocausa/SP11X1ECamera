# E004pi read-only same-SP11 original Windows rear4K snapshot scalar verifier.
# Invoke on SP7 with: $env:E004NQ_ORIGINAL_LOG_ROOT='<private E004nq directory>'; & .\read-original-sp7-live-rear-irq-scalars.ps1
# Emits ONLY selected safe register/status scalars, booleans and source-file SHA.
# NO original private log content, physical/DMA addresses, or optical pixels exported.
$ErrorActionPreference='Stop'
$SourceRoot=$env:E004NQ_ORIGINAL_LOG_ROOT
if([string]::IsNullOrWhiteSpace($SourceRoot) -or -not(Test-Path -LiteralPath $SourceRoot -PathType Container)){
  throw 'E004PI_ORIGINAL_LOG_ROOT_REQUIRED'
}
$hashes=@{
 LIVE1='4dde22d019d006151633916583e88d19bd50f65b059c35c1978defc7929b268c'
 LIVE2='fea13ae844c949bb722d74fbb2b5c48510178c055550b9d31268a351257986f9'
}
$addrPrefix='00000000'+[char]96
function Get-Region {
 param([string]$Raw,[string]$Phase,[string]$Region)
 $b='===E004NQ_'+$Phase+'_'+$Region+'_BEGIN==='
 $e='===E004NQ_'+$Phase+'_'+$Region+'_END==='
 $i=$Raw.IndexOf($b,[StringComparison]::Ordinal)
 $j=$Raw.IndexOf($e,[StringComparison]::Ordinal)
 if($i -lt 0 -or $j -lt ($i+$b.Length)){throw 'E004PI_MISSING_EXPECTED_REGION'}
 $body=$Raw.Substring($i+$b.Length,$j-$i-$b.Length)
 $rows=@($body -split '\r?\n' | Where-Object {$_ -match '^00000000'})
 $expected=if($Region -eq 'CSID1'){2048}else{4096}
 if($rows.Count -ne $expected/4){throw 'E004PI_INCOMPLETE_OR_DUPLICATE_PHYSICAL_REGION'}
 $first=@($rows[0] -split '\s+'|Where-Object {$_ -ne ''})
 if($first.Count -ne 5 -or -not $first[0].StartsWith($addrPrefix)){throw 'E004PI_BAD_FIRST_ROW'}
 $base=[Convert]::ToUInt64($first[0].Substring($addrPrefix.Length),16)
 if(($base -band 0xfff) -ne 0){throw 'E004PI_BAD_REGION_ALIGNMENT'}
 return [pscustomobject]@{body=$body;base=$base}
}
function Get-Scalar {
 param($Region,[int]$Offset)
 if($Offset -lt 0 -or ($Offset -band 3) -ne 0 -or $Offset -ge 0x2000){
   throw 'E004PI_BAD_REGISTER_OFFSET'
 }
 $aligned=$Offset -band (-bnot 15)
 $target=$addrPrefix+('{0:x8}' -f ($Region.base+[uint64]$aligned))
 $rows=@($Region.body -split '\r?\n' | Where-Object {($_ -split '\s+')[0] -eq $target})
 if($rows.Count -ne 1){throw 'E004PI_EXPECT_ONE_REGISTER_ROW'}
 $parts=@($rows[0] -split '\s+'|Where-Object {$_ -ne ''})
 if($parts.Count -ne 5){throw 'E004PI_BAD_REGISTER_ROW_WORD_COUNT'}
 return [Convert]::ToUInt32($parts[1+[int](($Offset -band 15)/4)],16)
}
$answers=@()
foreach($phase in @('LIVE1','LIVE2')){
 $path=Join-Path $SourceRoot ('E004NQ_'+$phase+'.log')
 if(-not(Test-Path -LiteralPath $path -PathType Leaf)){throw 'E004PI_MISSING_PRIVATE_ORIGINAL_LOG'}
 $hash=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
 if($hash -cne $hashes[$phase]){throw 'E004PI_ORIGINAL_LOG_SHA_CHANGED'}
 $raw=[IO.File]::ReadAllText($path,[Text.Encoding]::Unicode)
 if(-not $raw.Contains('Closing open log file')){throw 'E004PI_ORIGINAL_LOG_INCOMPLETE'}
 $csid=Get-Region -Raw $raw -Phase $phase -Region 'CSID1'
 $vfe=Get-Region -Raw $raw -Phase $phase -Region 'VFE1'
 $buf=Get-Scalar $csid 0x8c; $mask=Get-Scalar $csid 0x90
 $wcfg=Get-Scalar $vfe 0x1e00
 $answer=[ordered]@{
   phase=$phase
   original_same_SP11_private_Windows_phase_log_sha256=$hash
   evidence_kind='existing_original_Windows_live_rear4k_PHYSICAL_REGISTER_SNAPSHOT_NOT_IRQ_FRAME_TRACE'
   csid1_buf_done_status=('0x{0:x8}' -f [uint64]$buf)
   csid1_buf_done_mask=('0x{0:x8}' -f [uint64]$mask)
   csid1_buf_done_status_bit7_set=[bool](($buf -band 128) -ne 0)
   csid1_buf_done_mask_bit7_enabled=[bool](($mask -band 128) -ne 0)
   csid1_buf_done_clear_register_readback=('0x{0:x8}' -f [uint64](Get-Scalar $csid 0x94))
   csid1_ipp_status=('0x{0:x8}' -f [uint64](Get-Scalar $csid 0xac))
   vfe1_top_status0=('0x{0:x8}' -f [uint64](Get-Scalar $vfe 0x44))
   vfe1_top_status1=('0x{0:x8}' -f [uint64](Get-Scalar $vfe 0x48))
   vfe1_bus_status0=('0x{0:x8}' -f [uint64](Get-Scalar $vfe 0xc28))
   vfe1_bus_status1=('0x{0:x8}' -f [uint64](Get-Scalar $vfe 0xc2c))
   vfe1_bus_mask0=('0x{0:x8}' -f [uint64](Get-Scalar $vfe 0xc18))
   vfe1_bus_mask1=('0x{0:x8}' -f [uint64](Get-Scalar $vfe 0xc1c))
   vfe1_wm16_cfg0=('0x{0:x8}' -f [uint64]$wcfg)
   vfe1_wm16_enabled=[bool](($wcfg -band 1) -ne 0)
   vfe1_wm16_addr_status0_nonzero=[bool]((Get-Scalar $vfe 0x1e70) -ne 0)
   original_live_BF_event0x0f_observed=$false
   independent_same_generation_VFE1_WM16_DMA_IOMMU_retirement_observed=$false
 }
 $answers += [pscustomobject]$answer
}
$answers|ConvertTo-Json -Depth 4 -Compress
