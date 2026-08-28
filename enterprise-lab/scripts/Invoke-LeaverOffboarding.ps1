[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)]
    [string]$UserPrincipalName,

    [switch]$RemoveGroupMemberships
)

$ErrorActionPreference = 'Stop'

$requiredModules = @(
    'Microsoft.Graph.Users',
    'Microsoft.Graph.Users.Actions',
    'Microsoft.Graph.Groups'
)

foreach ($module in $requiredModules) {
    if (-not (Get-Module -ListAvailable -Name $module)) {
        throw "$module ist nicht installiert."
    }
    Import-Module $module
}

$escapedUpn = $UserPrincipalName.Replace("'", "''")
$user = Get-MgUser -Filter "userPrincipalName eq '$escapedUpn'" -Property 'Id,DisplayName,UserPrincipalName,AccountEnabled,AssignedLicenses,LicenseAssignmentStates'

if (-not $user) {
    throw "Benutzer '$UserPrincipalName' wurde nicht gefunden."
}

if (@($user).Count -ne 1) {
    throw "Die Suche nach '$UserPrincipalName' war nicht eindeutig."
}

$results = [System.Collections.Generic.List[object]]::new()

if ($PSCmdlet.ShouldProcess($user.UserPrincipalName, 'Disable Microsoft Entra account')) {
    Update-MgUser -UserId $user.Id -AccountEnabled:$false
    $results.Add([pscustomobject]@{ Action = 'DisableAccount'; Status = 'Completed'; Detail = $user.UserPrincipalName })
}

$directSkuIds = @(
    $user.LicenseAssignmentStates |
        Where-Object { -not $_.AssignedByGroup } |
        Select-Object -ExpandProperty SkuId -Unique
)

if ($directSkuIds.Count -gt 0) {
    if ($PSCmdlet.ShouldProcess($user.UserPrincipalName, "Remove $($directSkuIds.Count) directly assigned license(s)")) {
        Set-MgUserLicense -UserId $user.Id -AddLicenses @() -RemoveLicenses $directSkuIds | Out-Null
        $results.Add([pscustomobject]@{ Action = 'RemoveDirectLicenses'; Status = 'Completed'; Detail = $directSkuIds.Count })
    }
}
else {
    $results.Add([pscustomobject]@{ Action = 'RemoveDirectLicenses'; Status = 'Skipped'; Detail = 'No directly assigned licenses found.' })
}

if ($RemoveGroupMemberships) {
    $memberships = Get-MgUserMemberOf -UserId $user.Id -All

    foreach ($membership in $memberships) {
        $objectType = $membership.AdditionalProperties['@odata.type']
        if ($objectType -ne '#microsoft.graph.group') {
            continue
        }

        if ($PSCmdlet.ShouldProcess($membership.Id, "Remove $($user.UserPrincipalName) from group")) {
            try {
                Remove-MgGroupMemberByRef -GroupId $membership.Id -DirectoryObjectId $user.Id
                $results.Add([pscustomobject]@{ Action = 'RemoveGroupMembership'; Status = 'Completed'; Detail = $membership.Id })
            }
            catch {
                $results.Add([pscustomobject]@{ Action = 'RemoveGroupMembership'; Status = 'Failed'; Detail = $_.Exception.Message })
            }
        }
    }
}
else {
    $results.Add([pscustomobject]@{ Action = 'RemoveGroupMemberships'; Status = 'Skipped'; Detail = 'Use -RemoveGroupMemberships for the lab test.' })
}

[pscustomobject]@{
    UserPrincipalName = $user.UserPrincipalName
    DisplayName       = $user.DisplayName
    ExecutedAt        = Get-Date
    Actions           = @($results)
}
