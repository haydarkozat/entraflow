[CmdletBinding()]
param(
    [string]$ExportDirectory
)

$ErrorActionPreference = 'Stop'

$requiredModules = @(
    'Microsoft.Graph.Identity.DirectoryManagement',
    'Microsoft.Graph.Users'
)

foreach ($module in $requiredModules) {
    if (-not (Get-Module -ListAvailable -Name $module)) {
        throw "$module ist nicht installiert."
    }
    Import-Module $module
}

$skuSummary = foreach ($sku in (Get-MgSubscribedSku -All)) {
    $enabledUnits = [int]$sku.PrepaidUnits.Enabled
    $consumedUnits = [int]$sku.ConsumedUnits

    [pscustomobject]@{
        SkuPartNumber = $sku.SkuPartNumber
        SkuId         = $sku.SkuId
        EnabledUnits  = $enabledUnits
        ConsumedUnits = $consumedUnits
        Available     = [math]::Max(0, ($enabledUnits - $consumedUnits))
        UtilizationPc = if ($enabledUnits -gt 0) {
            [math]::Round(($consumedUnits / $enabledUnits) * 100, 1)
        }
        else {
            0
        }
    }
}

$users = Get-MgUser -All -Property 'Id,DisplayName,UserPrincipalName,AccountEnabled,AssignedLicenses,Department'
$disabledLicensedUsers = foreach ($user in $users) {
    $licenseCount = @($user.AssignedLicenses).Count

    if (($user.AccountEnabled -eq $false) -and ($licenseCount -gt 0)) {
        [pscustomobject]@{
            DisplayName       = $user.DisplayName
            UserPrincipalName = $user.UserPrincipalName
            Department        = $user.Department
            AccountEnabled    = $user.AccountEnabled
            LicenseCount      = $licenseCount
        }
    }
}

if ($ExportDirectory) {
    if (-not (Test-Path -LiteralPath $ExportDirectory)) {
        New-Item -ItemType Directory -Path $ExportDirectory | Out-Null
    }

    $skuSummary | Export-Csv -LiteralPath (Join-Path $ExportDirectory 'license-capacity.csv') -NoTypeInformation -Encoding utf8
    $disabledLicensedUsers | Export-Csv -LiteralPath (Join-Path $ExportDirectory 'disabled-licensed-users.csv') -NoTypeInformation -Encoding utf8
}

[pscustomobject]@{
    GeneratedAt           = Get-Date
    SkuSummary            = @($skuSummary)
    DisabledLicensedUsers = @($disabledLicensedUsers)
    PotentialReviewCount  = @($disabledLicensedUsers).Count
}
