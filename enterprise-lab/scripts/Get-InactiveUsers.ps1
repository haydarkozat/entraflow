[CmdletBinding()]
param(
    [ValidateRange(1, 3650)]
    [int]$InactiveDays = 30,

    [string]$ExportCsv
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Module -ListAvailable -Name Microsoft.Graph.Users)) {
    throw 'Microsoft.Graph.Users ist nicht installiert.'
}

Import-Module Microsoft.Graph.Users

$cutoff = (Get-Date).ToUniversalTime().AddDays(-$InactiveDays)
$properties = 'Id,DisplayName,UserPrincipalName,AccountEnabled,Department,AssignedLicenses,SignInActivity'
$users = Get-MgUser -All -Property $properties

$report = foreach ($user in $users) {
    $lastSignIn = $null

    if ($user.SignInActivity) {
        if ($user.SignInActivity.LastSuccessfulSignInDateTime) {
            $lastSignIn = [datetimeoffset]$user.SignInActivity.LastSuccessfulSignInDateTime
        }
        elseif ($user.SignInActivity.LastSignInDateTime) {
            $lastSignIn = [datetimeoffset]$user.SignInActivity.LastSignInDateTime
        }
    }

    $isInactive = ($null -eq $lastSignIn) -or ($lastSignIn.UtcDateTime -le $cutoff)
    if (-not $isInactive) {
        continue
    }

    $daysInactive = if ($lastSignIn) {
        [math]::Floor(((Get-Date).ToUniversalTime() - $lastSignIn.UtcDateTime).TotalDays)
    }
    else {
        $null
    }

    [pscustomobject]@{
        DisplayName       = $user.DisplayName
        UserPrincipalName = $user.UserPrincipalName
        Department        = $user.Department
        AccountEnabled    = $user.AccountEnabled
        LastSignIn        = if ($lastSignIn) { $lastSignIn.UtcDateTime } else { 'Never/Unavailable' }
        DaysInactive      = $daysInactive
        LicenseCount      = @($user.AssignedLicenses).Count
    }
}

$report = @($report | Sort-Object DaysInactive -Descending)

if ($ExportCsv) {
    $report | Export-Csv -LiteralPath $ExportCsv -NoTypeInformation -Encoding utf8
}

$report
