[CmdletBinding()]
param(
    [string]$ExportCsv
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Module -ListAvailable -Name Microsoft.Graph.DeviceManagement)) {
    throw 'Microsoft.Graph.DeviceManagement ist nicht installiert.'
}

Import-Module Microsoft.Graph.DeviceManagement

$devices = Get-MgDeviceManagementManagedDevice -All

$report = foreach ($device in $devices) {
    $lastSync = if ($device.LastSyncDateTime) {
        [datetimeoffset]$device.LastSyncDateTime
    }
    else {
        $null
    }

    [pscustomobject]@{
        DeviceName        = $device.DeviceName
        UserPrincipalName = $device.UserPrincipalName
        OperatingSystem   = $device.OperatingSystem
        OsVersion         = $device.OsVersion
        ComplianceState   = $device.ComplianceState
        ManagementAgent   = $device.ManagementAgent
        LastSyncDateTime  = if ($lastSync) { $lastSync.UtcDateTime } else { $null }
        DaysSinceSync     = if ($lastSync) {
            [math]::Floor(((Get-Date).ToUniversalTime() - $lastSync.UtcDateTime).TotalDays)
        }
        else {
            $null
        }
        EntraDeviceId     = $device.AzureAdDeviceId
        IntuneDeviceId    = $device.Id
    }
}

$report = @($report | Sort-Object ComplianceState, DeviceName)

if ($ExportCsv) {
    $report | Export-Csv -LiteralPath $ExportCsv -NoTypeInformation -Encoding utf8
}

$report
