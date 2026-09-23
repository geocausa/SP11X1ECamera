# E004nn: local-only Windows FrameServer ETW + rear WinRT metadata scalar reducer.
# Reads NO frame pixels. ETL/original WinRT JSON stay on this same SP11 Windows volume.
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$inputFiles=@(Get-ChildItem -LiteralPath $root -Filter 'E004NN-rear-preview-vs-record-*.json' -File)
if ($inputFiles.Count -ne 2) {throw 'E004NN: expected both observed Windows task invocations; do not merge'}
$first=@($inputFiles | Where-Object {$_.Name -eq 'E004NN-rear-preview-vs-record-20260923-212206.json'})
$second=@($inputFiles | Where-Object {$_.Name -eq 'E004NN-rear-preview-vs-record-20260923-212305.json'})
if ($first.Count -ne 1 -or $second.Count -ne 1) {throw 'E004NN: first-traced and second-untraced task identities must be exact'}
$etl=Join-Path $root 'E004NN_FrameServer_RearModes.etl'
$out=Join-Path $root 'E004NN-SCALAR-RESULT.json'
if (-not(Test-Path -LiteralPath $etl) -or (Test-Path -LiteralPath $out)) {throw 'E004NN: ETL missing or scalar report exists'}
if ((logman.exe query -ets | Out-String) -match 'E004NN_FrameServer_RearModes_20260923') {throw 'E004NN trace still active'}
$j=Get-Content -LiteralPath $first[0].FullName -Raw -ErrorAction Stop | ConvertFrom-Json
$j2=Get-Content -LiteralPath $second[0].FullName -Raw -ErrorAction Stop | ConvertFrom-Json
$secondRecords=@($j2.results | Where-Object {$_.group -eq 'Surface Camera Rear' -and $_.stream -in @('VideoPreview','VideoRecord')})
if ($secondRecords.Count -ne 2 -or @($secondRecords | Where-Object {$_.start_status -ne 'Success'}).Count -ne 0) {throw 'E004NN second task metadata was not independently valid'}
if (Get-ScheduledTask -TaskName 'E004nn-OneShot-RearPreviewRecord-20260923' -ErrorAction SilentlyContinue) {throw 'E004NN unintended duplicate-trigger task still registered'}
$records=@($j.results | Where-Object {$_.group -eq 'Surface Camera Rear' -and $_.stream -in @('VideoPreview','VideoRecord')})
if ($records.Count -ne 2 -or @($records.stream | Select-Object -Unique).Count -ne 2) {throw 'E004NN expected rear preview and record only'}
$events=@(Get-WinEvent -Path $etl -Oldest -ErrorAction Stop)
if ($events.Count -lt 2000) {throw 'E004NN FrameServer ETW trace incomplete'}
$firstCreated=[datetimeoffset]::Parse($j.created)
$secondCreated=[datetimeoffset]::Parse($j2.created)
$traceEnd=[datetimeoffset]$events[-1].TimeCreated
if($firstCreated -lt $traceEnd -or $firstCreated -gt $traceEnd.AddSeconds(3) -or
   $secondCreated -lt $traceEnd.AddSeconds(30)) {
  throw 'E004NN original FIRST traced run / SECOND untraced run time boundary not valid'
}
$spec=@(
  [pscustomobject]@{stream='VideoPreview';sid=0;width=1920;height=1080;handles=246},
  [pscustomobject]@{stream='VideoRecord';sid=2;width=3840;height=2160;handles=254}
)
$results=@()
foreach($sp in $spec){
  $r=@($records | Where-Object {$_.stream -eq $sp.stream})[0]
  $handles=@($r.samples)
  if ($r.start_status -ne 'Success' -or $r.default_subtype -ne 'NV12' -or
      [int]$r.default_width -ne $sp.width -or [int]$r.default_height -ne $sp.height -or
      $handles.Count -ne $sp.handles -or $null -ne $r.error) {
    throw ('E004NN WinRT mode/status unexpected: '+$sp.stream)
  }
  $good=@($handles | Where-Object {$_.software_bitmap -eq $true -and
           $_.bitmap_format -eq 'Nv12' -and [int]$_.bitmap_width -eq $sp.width -and
           [int]$_.bitmap_height -eq $sp.height})
  if ($good.Count -ne $handles.Count){throw 'E004NN WinRT bitmap count/geometry invalid'}
  $nulltime=@($handles | Where-Object {$null -eq $_.system_time_ticks}).Count
  if($nulltime -ne $handles.Count){throw 'E004NN source timestamp expectation changed'}
  $f=@($events | Where-Object {$_.Id -eq 8 -and [int]$_.Properties[0].Value -eq $sp.sid})
  $t=@($f | ForEach-Object {[int64]$_.Properties[1].Value})
  if ($t.Count -lt 250 -or @($t | Select-Object -Unique).Count -ne $t.Count) {
    throw ('E004NN FrameServer source sample count/unique timestamps invalid: '+$sp.stream)
  }
  $deltas=@()
  for($ix=1;$ix -lt $t.Count;$ix++){
    $d=[int64]($t[$ix]-$t[$ix-1])
    if($d -le 0 -or $d -lt 330000 -or $d -gt 340000){
      throw ('E004NN FrameServer timestamp gap/regression: '+$sp.stream+' d='+$d)
    }
    $deltas+=$d
  }
  $sorted=@($deltas|Sort-Object)
  $median=[int64]$sorted[[int][Math]::Floor(($sorted.Count-1)/2)]
  $stats=@($events | Where-Object {$_.Id -eq 10 -and [int]$_.Properties[0].Value -eq $sp.sid})
  if ($stats.Count -lt 15 -or @($stats | Where-Object {
      [int64]$_.Properties[6].Value -ne 0 -or
      [int64]$_.Properties[9].Value -ne 333333 -or
      [int64]$_.Properties[10].Value -ne 0 }).Count -ne 0) {
    throw ('E004NN FrameServer statistics missing or drop/failure: '+$sp.stream)
  }
  $last=$stats[-1]
  $lastinput=[int64]$last.Properties[4].Value
  $lastoutput=[int64]$last.Properties[5].Value
  if ($lastinput -lt 250 -or $lastinput -ne $lastoutput) {
    throw ('E004NN FrameServer last input/output mismatch: '+$sp.stream)
  }
  $pinTypes=@($events | Where-Object {$_.Id -eq 52 -and
             [int]$_.Properties[0].Value -eq $sp.sid -and
             [int]$_.Properties[2].Value -eq 2 -and
             ([string]$_.Properties[1].Value) -match ('subtype=NV12,res='+$sp.width+'x'+$sp.height)})
  if ($pinTypes.Count -ne 1){throw ('E004NN DeviceMFT selected mode absent/ambiguous: '+$sp.stream)}
  $media=[string]$pinTypes[0].Properties[1].Value
  if($media -notmatch 'sample_size=(\d+)'){throw 'E004NN DeviceMFT media type sample size missing'}
  $mfSize=[int64]$Matches[1]
  if($media -notmatch 'default_stride=(-?\d+)'){throw 'E004NN DeviceMFT reported stride missing'}
  $mfStride=[int]$Matches[1]
  if($mfSize -lt [int64]($sp.width*$sp.height*3/2) -or $mfStride -ne $sp.width){throw 'E004NN DeviceMFT media type size/stride contradiction'}
  $results+= [pscustomobject][ordered]@{
    stream=$sp.stream
    Windows_WinRT_NV12_app_width=$sp.width
    Windows_WinRT_NV12_app_height=$sp.height
    Windows_WinRT_CPU_bitmap_handles=$handles.Count
    Windows_WinRT_source_timestamps_missing=$nulltime
    Windows_WinRT_polling_elapsed_ms=([int]$handles[-1].elapsed_ms-[int]$handles[0].elapsed_ms)
    Windows_FrameServer_sample_stream_id=$sp.sid
    Windows_FrameServer_distinct_timestamped_client_samples=$t.Count
    Windows_FrameServer_timestamp_monotonic_edges=$deltas.Count
    Windows_FrameServer_timestamp_duplicates_or_regressions=0
    Windows_FrameServer_timestamp_median_positive_delta_100ns=$median
    Windows_FrameServer_timestamp_min_positive_delta_100ns=[int64]$sorted[0]
    Windows_FrameServer_timestamp_max_positive_delta_100ns=[int64]$sorted[-1]
    Windows_FrameServer_expected_interval_100ns=333333
    Windows_FrameServer_capture_statistics_snapshots=$stats.Count
    Windows_FrameServer_capture_statistics_last_input=$lastinput
    Windows_FrameServer_capture_statistics_last_output=$lastoutput
    Windows_FrameServer_capture_statistics_drops=0
    Windows_DeviceMFT_matching_output_pin_selected_once=$true
    Windows_DeviceMFT_output_pin_default_stride_metadata=$mfStride
    Windows_DeviceMFT_output_pin_sample_size_metadata_bytes=$mfSize
    Windows_DeviceMFT_output_pin_sample_size_metadata_is_NOT_VFE0_DMA_layout=$true
  }
}
$fullSensorTypes=@($events| Where-Object {$_.Id -eq 54 -and
  [int]$_.Properties[0].Value -eq 1 -and
  ([string]$_.Properties[1].Value) -match 'subtype=NV12,res=4076x2806' -and
  [int]$_.Properties[2].Value -eq 0})
$proxyFullTypes=@($events|Where-Object {$_.Id -eq 2 -and
  [int]$_.Properties[0].Value -eq 1 -and
  ([string]$_.Properties[1].Value) -match '\(3736,2802\)'})
if($fullSensorTypes.Count -lt 1 -or $proxyFullTypes.Count -ne 1){
  throw 'E004NN auxiliary full-size DeviceMFT/FSProxy format observation missing'
}
$unexpectedDrops=@($events|Where-Object {$_.Id -eq 23}).Count
if($unexpectedDrops -ne 0){throw 'E004NN FrameServer explicit dropped-frame events present'}
$drivers=@(Get-CimInstance Win32_SystemDriver | Where-Object {$_.Name -in @('CameraRearSensor','qcCameraMipiCsi','qcCameraPlatform','qcISP')} | Sort-Object Name | Select-Object Name,State,Started)
if($drivers.Count -ne 4 -or @($drivers|Where-Object {$_.State -ne 'Running' -or $_.Started -ne $true}).Count -ne 0){throw 'E004NN installed rear camera drivers not running'}
# The single Scheduled Task fired TWICE: immediate Start-ScheduledTask followed
# by its future Once trigger. It has been unregistered; first ETL covers only
# the first 21:22:06 invocation, while 21:23:05 is an untraced distinct run.
# Prior read of TaskScheduler LastTaskResult=0 was retained in session audit.
$record=[ordered]@{
  schema='sp11-e004nn-rear-preview-4k-record-frameserver-scalar-v1'
  experiment='E004nn'
  actual_machine='SP11_Windows_11_ARM64'
  sensor='OV13858'
  board='MSHW0491'
  original_windows_user_task_consumed_once=$false
  windows_user_task_invocations_observed=2
  windows_duplicate_scheduled_trigger_detected=$true
  windows_duplicate_scheduled_task_unregistered=$true
  first_traced_winrt_metadata_file='E004NN-rear-preview-vs-record-20260923-212206.json'
  second_untraced_winrt_metadata_file='E004NN-rear-preview-vs-record-20260923-212305.json'
  windows_original_task_last_observed_exit_code_before_unregistration=0
  windows_frame_server_ETW_covers_first_task_invocation_only=$true
  Windows_first_traced_user_run_json_created=$j.created
  Windows_second_untraced_user_run_json_created=$j2.created
  Windows_traced_ETW_last_event_time=$events[-1].TimeCreated.ToString('o')
  Windows_ETW_first_run_vs_second_run_monotonic_timing_boundary_verified=$true
  original_windows_ETL_is_private_on_same_SP11=$true
  Original_Windows_ETW_FrameServer_provider_guid='9e22a3ed-7b32-4b99-b6c2-21dd6ace01e1'
  Original_Windows_ETW_event_count=$events.Count
  Windows_second_untraced_invocation_completed_rear_preview_and_record=$true
  Windows_ETW_second_run_wall_clock_markers_overwrote_first_run_markers=$true
  Windows_ETW_first_and_second_invocations_never_merged=$true
  Windows_FrameServer_10_statistics_per_mode=$true
  Windows_FrameServer_23_explicit_drop_events=$unexpectedDrops
  Windows_DeviceMFT_configured_auxiliary_input_pin_1_NV12_4076x2806_count=$fullSensorTypes.Count
  Windows_DeviceMFT_auxiliary_full_sensor_pin_1_shown_active=$false
  Windows_FSProxy_configured_auxiliary_output_pin_1_NV12_3736x2802_count=$proxyFullTypes.Count
  Windows_device_MFT_media_type_sample_size_is_not_native_ISP_DMA_contract=$true
  Windows_rear_observed_streams=$results
  Windows_camera_drivers=$drivers
  Windows_rear_hardware_IFE_core_assignment_confirmed=$false
  Windows_rear_native_VFE0_FULL_WM_DMA_output_geometry_confirmed=$false
  Windows_rear_4k_softwarebitmap_equals_native_hardware_4k_surface_proven=$false
  Windows_rear_sensor_hardware_frame_ids_measured=$false
  Windows_high_quality_photo_mode_tested=$false
  SP7_broken_lower_LCD_excluded_from_image_quality_claims=$true
  SP7_LCD_remains_always_on=$true
  optical_pixels_images_RAW_thumbnails_or_hashes_exported=$false
  Windows_firmware_tuning_or_proprietary_driver_copied_into_repo=$false
  Linux_rear_native_hardware_ISP_4k_frame_proven=$false
}
[pscustomobject]$record | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $out -Encoding UTF8
$verify=Get-Content -LiteralPath $out -Raw | ConvertFrom-Json
if(@($verify.Windows_rear_observed_streams).Count -ne 2){throw 'E004NN scalar result writeback failed'}
Write-Output ('E004NN_SCALAR_REDUCER_PASS ETW_EVENTS='+$events.Count+' FRAMESTREAM0='+$results[0].Windows_FrameServer_distinct_timestamped_client_samples+' FRAMESTREAM2='+$results[1].Windows_FrameServer_distinct_timestamped_client_samples+' ZERO_REPORTED_DROP=YES HW_VFE0_UNPROVEN=YES')
