# E004no Windows-only strict scalar evidence reducer; no pixels or OEM code exported.
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$dest=Join-Path $root 'E004NO-SCALAR-RESULT.json'
if(Test-Path -LiteralPath $dest){throw 'E004NO_SCALAR_ORIGINAL_ALREADY_EXISTS'}
$provider=Get-Content -LiteralPath (Join-Path $root 'E004NO-SCALAR-PROVIDER-PREFLIGHT.json') -Raw | ConvertFrom-Json
if($provider.driver_sha256 -ne '64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c' -or
   $provider.enum_trace_guids_ex_status -ne 0 -or
   @($provider.GUID_alignment_matches).Count -ne 1 -or
   $provider.GUID_alignment_matches[0].alignment -ne 0 -or
   @($provider.GUID_alignment_matches[0].embedded_and_runtime_matches).Count -ne 1 -or
   $provider.GUID_alignment_matches[0].embedded_and_runtime_matches[0] -ne
   '57e95397-c84e-4f53-9473-56207aaa5938 | PE_FILE_OFFSET=289216') {
  throw 'E004NO_CANDIDATE_PROVIDER_FINGERPRINT_MISMATCH'
}
$private=@(Get-ChildItem $root -Filter 'E004NO-rear-video4k-*.json' -File)
if($private.Count -ne 1){throw 'E004NO_ORIGINAL_WINRT_INVOCATION_NOT_UNIQUE'}
$raw=Get-Content -LiteralPath $private[0].FullName -Raw | ConvertFrom-Json
$streams=@($raw.results | Where-Object {$_.group -eq 'Surface Camera Rear' -and $_.stream -eq 'VideoRecord'})
if($streams.Count -ne 1){throw 'E004NO_REAR_RECORD_STREAM_NOT_UNIQUE'}
$s=$streams[0]
$h=@($s.samples)
$good=@($h|Where-Object {$_.software_bitmap -eq $true -and $_.bitmap_format -eq 'Nv12' -and
                             $_.bitmap_width -eq 3840 -and $_.bitmap_height -eq 2160})
if($s.start_status -ne 'Success' -or $s.default_subtype -ne 'NV12' -or
   $s.default_width -ne 3840 -or $s.default_height -ne 2160 -or
   $h.Count -ne 350 -or $good.Count -ne $h.Count -or
   @($h|Where-Object{$null -ne $_.system_time_ticks}).Count -ne 0) {
  throw 'E004NO_REAL_WINRT_CAPTURE_NOT_VERIFIED'
}
$taskName='E004no-Manual-Only-Rear4kProvider-20260923'
if(Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue){
  throw 'E004NO_WINDOWS_CAPTURE_TASK_NOT_UNREGISTERED'
}
if(-not(Test-Path (Join-Path $root 'E004NO-rear4k-driver-etw-single-entry.consumed'))){
  throw 'E004NO_SCRIPT_ENTRY_ATOMIC_MARKER_MISSING'
}
$session='E004NO_QcIsp_Runtime_Guid_Trial_20260923'
if((logman.exe query -ets | Out-String) -match $session){throw 'E004NO_ETW_TRACE_STILL_ACTIVE'}
$etl=Join-Path $root 'E004NO_QcIsp_Runtime_Guid_Trial.etl'
$e=@(Get-WinEvent -Path $etl -Oldest -ErrorAction Stop)
$guid=[guid]'57e95397-c84e-4f53-9473-56207aaa5938'
$own=@($e|Where-Object {$_.ProviderId -eq $guid})
$providerCounts=@($own|Group-Object Id|Sort-Object Name|ForEach-Object{
  [pscustomobject]@{id=[int]$_.Name;count=[int]$_.Count}
})
if($e.Count -ne 12 -or $own.Count -ne 11 -or
  (@($own|Where-Object{$_.Id -eq 61}).Count -ne 8) -or
  (@($own|Where-Object{$_.Id -eq 2}).Count -ne 2) -or
  (@($own|Where-Object{$_.Id -eq 62}).Count -ne 1)) {
  throw 'E004NO_RUNTIME_CANDIDATE_EVENT_ID_COUNTS_CHANGED'
}
$parseErrors=@($own|ForEach-Object{
    [xml]$xml=$_.ToXml()
    [pscustomobject]@{
      processing_code=[int]$xml.Event.ProcessingErrorData.ErrorCode
      opaque_payload_hex_chars=([string]$xml.Event.ProcessingErrorData.EventPayload).Length
      decoded_property_count=@($_.Properties).Count
    }
})
if(@($parseErrors|Where-Object{$_.processing_code -ne 15003 -or
    $_.opaque_payload_hex_chars -lt 10 -or $_.decoded_property_count -ne 0}).Count -ne 0){
  throw 'E004NO_CANDIDATE_EVENT_DECODING_ASSUMPTIONS_CHANGED'
}
$first=$own[0].TimeCreated
$last=$own[-1].TimeCreated
$liveMarker=(Get-Content -LiteralPath (Join-Path $root 'E004NO-REAR4K-LIVE.txt') -Raw)
if($liveMarker -notmatch 'REAR_VIDEORECORD_NV12_3840x2160_LIVE=(\S+)'){
  throw 'E004NO_REAL_REAR4K_LIVE_MARKER_MISSING'
}
$live=[datetimeoffset]::Parse($Matches[1])
$delta=[int][math]::Round(($live-([datetimeoffset]$first)).TotalMilliseconds)
if($delta -lt 0 -or $delta -gt 1000 -or
  ($last-$first).TotalMilliseconds -gt 50 -or
  (@($own|Select-Object -ExpandProperty ProcessId -Unique).Count -ne 1)){
  throw 'E004NO_ETW_CAMERA_STARTUP_TEMPORAL_BOUNDARY_INVALID'
}
# Windows PnP exposed 12 IRQ resources for this ISP device, no WMI MMIO
# resource. This is not evidence that no MMIO exists or that 0x80000000
# KD physical reads are valid.
$dev=Get-CimInstance Win32_PnPEntity | Where-Object {
  $_.PNPDeviceID -like 'ACPI\VEN_QCOM*0C25*'} | Select-Object -First 1
if(-not $dev -or $dev.Status -ne 'OK'){throw 'E004NO_ISP_PNP_DEVICE_NOT_OK'}
$assigned=@(Get-CimAssociatedInstance -InputObject $dev -Association Win32_PnPAllocatedResource -ErrorAction Stop)
if($assigned.Count -ne 12 -or
   @($assigned|Where-Object{$_.CimClass.CimClassName -ne 'Win32_IRQResource'}).Count -ne 0){
  throw 'E004NO_PNP_WMI_RESOURCE_SHAPE_CHANGED'
}
$scalar=[ordered]@{
  experiment='E004no'
  status='PASS_REAL_WIN_REAR4K_QCISP_PE_MATCHED_REGISTERED_GUID_HAS_11_UNDECODED_STARTUP_EVENTS'
  same_SP11_Windows_11_OEM_rear='OV13858_MSHW0491'
  selected_ISP_driver_SHA256=$provider.driver_sha256
  driver_embedded_live_ETW_candidate_GUID=$guid.ToString('D')
  embedded_ETW_GUID_PE_file_offset_from_readonly_byte_scan=289216
  EnumerateTraceGuidsEx_returned_bytes=$provider.enum_trace_guids_ex_returned_bytes
  Windows_live_GUID_and_exact_installed_PE_bytes_matched=$true
  Windows_manifest_provider_for_candidate_found=$false
  live_ETW_session_single_guid_start_and_stop_succeeded=$true
  original_trace_stays_private_same_SP11=$true
  raw_trace_file_bytes=(Get-Item $etl).Length
  ETW_total_events=$e.Count
  candidate_ETW_events=$own.Count
  candidate_ETW_event_ids=$providerCounts
  candidate_ETW_first_event=$first.ToString('o')
  candidate_ETW_last_event=$last.ToString('o')
  candidate_ETW_event_process_context_id_is_NOT_hardware_IFE_core=$true
  candidate_ETW_processing_error_code=15003
  candidate_ETW_event_payloads_present_but_UNDECODED=$true
  candidate_ETW_event_payload_hex_minimum_length=(@($parseErrors.opaque_payload_hex_chars|Measure-Object -Minimum)[0].Minimum)
  candidate_ETW_event_payload_hex_maximum_length=(@($parseErrors.opaque_payload_hex_chars|Measure-Object -Maximum)[0].Maximum)
  candidate_ETW_first_event_ms_before_WinRT_rear4k_live_marker=$delta
  candidate_ETW_burst_duration_ms=([int][math]::Round(($last-$first).TotalMilliseconds))
  candidate_ETW_event_fields_decoded_as_ISP_resources=$false
  private_OEM_PDB_public_Microsoft_symbol_server_HEAD_status='HTTP_404'
  task_has_no_future_trigger_and_is_unregistered=$true
  one_original_script_entry_permanent_atomic_consume_marker=$true
  original_WinRT_rear_record_NV12_width=3840
  original_WinRT_rear_record_NV12_height=2160
  original_WinRT_software_bitmap_handle_count=$h.Count
  original_WinRT_source_timestamps_missing=$h.Count
  original_WinRT_session_frame_ids_not_proven=$true
  Windows_PnP_qcISP_associated_IRQ_resource_count=$assigned.Count
  Windows_PnP_associated_MMIO_memory_resources_via_WMI=0
  Windows_PnP_associated_WMI_MMIO_absence_means_no_MMIO=$false
  Windows_KD_driver_object_extension_read_fails_ObpInfoMaskToOffset=$true
  Windows_prior_KD_direct_camera_MMIO_uniform_80000000_is_validated=$false
  active_rear_CSID0_IPP_selected_IFE_core_proven=$false
  active_rear_VFE0_FULL_WM_DMA_output_geometry_proven=$false
  rear_Linux_native_hardware_ISP_4K_frame_proven=$false
  original_driver_firmware_ETL_images_pixels_or_metadata_transcript_exported=$false
}
[pscustomobject]$scalar|ConvertTo-Json -Depth 9|Set-Content -LiteralPath $dest -Encoding UTF8
$j=Get-Content -LiteralPath $dest -Raw|ConvertFrom-Json
if($j.candidate_ETW_events -ne 11 -or $j.active_rear_VFE0_FULL_WM_DMA_output_geometry_proven -ne $false){
  throw 'E004NO_SCALAR_EVIDENCE_WRITEBACK_FAILED'
}
Write-Output 'E004NO_DRIVER_GUID_PE_MATCHED_LIVE_ETW_STARTUP_EVENTS_11_UNDECODED_AND_SAFE_SINGLE_CAPTURE_PASS'
