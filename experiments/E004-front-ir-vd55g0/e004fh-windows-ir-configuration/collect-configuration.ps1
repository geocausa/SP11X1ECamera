# E004fh: read-only Windows IR configuration collection.
# Does not open a camera, flash interface, device handle, or debugger.
$ErrorActionPreference = 'Stop'
$directory = 'C:\SP11Camera\E004fh'
$output = Join-Path $directory 'configuration.json'
if (Test-Path $output) { throw 'E004fh output already exists; audit before reuse.' }
New-Item -ItemType Directory -Force -Path $directory | Out-Null
$devices = @(Get-PnpDevice -PresentOnly | Where-Object {
    $_.InstanceId -like 'ACPI\QCOM0C27*' -or
    $_.FriendlyName -match 'Power Management PMIC|Power Management PML|PMIC GLINK'
})
$keys = @('DEVPKEY_Device_DriverInfPath', 'DEVPKEY_Device_DriverVersion',
          'DEVPKEY_Device_Service', 'DEVPKEY_Device_Parent',
          'DEVPKEY_Device_LocationPaths', 'DEVPKEY_Device_HardwareIds')
$rows = @()
foreach ($device in $devices) {
    $properties = @{}
    foreach ($key in $keys) {
        try {
            $p = Get-PnpDeviceProperty -InstanceId $device.InstanceId -KeyName $key
            $properties[$key] = $p.Data
        } catch { $properties[$key] = $null }
    }
    $values = @()
    if ($device.InstanceId -like 'ACPI\QCOM0C27*') {
        $root = 'Registry::HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\' + $device.InstanceId
        $regkeys = @((Get-Item -LiteralPath $root))
        $regkeys += @(Get-ChildItem -LiteralPath $root -Recurse -ErrorAction SilentlyContinue)
        foreach ($key in $regkeys) {
            foreach ($name in $key.GetValueNames()) {
                if ($name -match '^(IrLedCurrentMilliampere|.*Flash.*|.*Strobe.*|.*Timeout.*|.*Duty.*)$') {
                    $values += [ordered]@{
                        key = $key.Name; name = $name
                        kind = $key.GetValueKind($name).ToString()
                        value = $key.GetValue($name)
                    }
                }
            }
        }
    }
    $rows += [ordered]@{
        instance_id = $device.InstanceId
        name = $device.FriendlyName
        status = $device.Status
        properties = $properties
        illumination_configuration = $values
    }
}
$hashes = @()
foreach ($name in @('qccamflash8380.sys', 'qcpmic8380.sys', 'qcpmicapps8380.sys',
                    'qcpmicglink8380.sys', 'qcpmicgpio8380.sys')) {
    $path = Join-Path "$env:SystemRoot\System32\drivers" $name
    if (Test-Path -LiteralPath $path) {
        $hashes += [ordered]@{ name = $name; sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLower() }
    }
}
$os = Get-CimInstance Win32_OperatingSystem
$result = [ordered]@{
    experiment = 'E004fh'
    collected_utc = [DateTime]::UtcNow.ToString('o')
    os_build = $os.BuildNumber
    last_boot_utc = $os.LastBootUpTime.ToUniversalTime().ToString('o')
    method = 'Read-only PnP, selected registry values and installed-file hashes'
    camera_opened = $false
    flash_commands_sent = $false
    current_is_live_measurement = $false
    devices = $rows
    installed_driver_hashes = $hashes
}
$result | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $output -Encoding UTF8
Get-Content -LiteralPath $output -Raw
