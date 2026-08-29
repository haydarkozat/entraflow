[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [Parameter(Mandatory)]
    [ValidateScript({ Test-Path -LiteralPath $_ })]
    [string]$CsvPath
)

$ErrorActionPreference = 'Stop'

foreach ($moduleName in @('Microsoft.Graph.Users', 'Microsoft.Graph.Groups')) {
    if (-not (Get-Module -ListAvailable -Name $moduleName)) {
        throw "Required module '$moduleName' is not installed. Install-Module Microsoft.Graph -Scope CurrentUser"
    }
}

Import-Module Microsoft.Graph.Users
Import-Module Microsoft.Graph.Groups

$context = Get-MgContext
if (-not $context) {
    throw 'No Microsoft Graph session found. Connect first.'
}

$rows = @(Import-Csv -LiteralPath $CsvPath)
if ($rows.Count -eq 0) {
    throw 'CSV contains no users.'
}

$results = foreach ($row in $rows) {
    $upn = [string]$row.UserPrincipalName
    $department = [string]$row.Department

    if ([string]::IsNullOrWhiteSpace($upn) -or [string]::IsNullOrWhiteSpace($department)) {
        [pscustomobject]@{
            UserPrincipalName = $upn
            Department        = $department
            Group             = $null
            Status            = 'Skipped'
            Reason            = 'Missing UPN or Department.'
        }
        continue
    }

    $groupName = "SG-Dept-$department"
    $escapedUpn = $upn.Replace("'", "''")
    $escapedGroup = $groupName.Replace("'", "''")

    $user = Get-MgUser -Filter "userPrincipalName eq '$escapedUpn'" -Property Id, UserPrincipalName
    if (-not $user) {
        [pscustomobject]@{
            UserPrincipalName = $upn
            Department        = $department
            Group             = $groupName
            Status            = 'Skipped'
            Reason            = 'User not found.'
        }
        continue
    }

    $group = Get-MgGroup -Filter "displayName eq '$escapedGroup'" -Property Id, DisplayName
    if (-not $group) {
        [pscustomobject]@{
            UserPrincipalName = $upn
            Department        = $department
            Group             = $groupName
            Status            = 'Skipped'
            Reason            = 'Department group not found.'
        }
        continue
    }

    $memberIds = @(Get-MgGroupMember -GroupId $group.Id -All | ForEach-Object { $_.Id })
    if ($user.Id -in $memberIds) {
        [pscustomobject]@{
            UserPrincipalName = $upn
            Department        = $department
            Group             = $groupName
            Status            = 'Existing'
            Reason            = 'Membership already exists.'
        }
        continue
    }

    $target = "$upn -> $groupName"
    if ($PSCmdlet.ShouldProcess($target, 'Add Microsoft Entra group membership')) {
        New-MgGroupMemberByRef -GroupId $group.Id -BodyParameter @{
            '@odata.id' = "https://graph.microsoft.com/v1.0/directoryObjects/$($user.Id)"
        }

        [pscustomobject]@{
            UserPrincipalName = $upn
            Department        = $department
            Group             = $groupName
            Status            = 'Added'
            Reason            = 'Department membership assigned.'
        }
    }
}

$results | Sort-Object Group, UserPrincipalName
