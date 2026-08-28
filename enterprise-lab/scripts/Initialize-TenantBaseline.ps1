[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param()

$ErrorActionPreference = 'Stop'

if (-not (Get-Module -ListAvailable -Name Microsoft.Graph.Groups)) {
    throw 'Microsoft.Graph.Groups ist nicht installiert. Install-Module Microsoft.Graph -Scope CurrentUser ausführen.'
}

Import-Module Microsoft.Graph.Groups

$context = Get-MgContext
if (-not $context) {
    throw 'Keine Microsoft-Graph-Verbindung gefunden. Zuerst ./Connect-EntraLab.ps1 ausführen.'
}

$baselineGroups = @(
    [pscustomobject]@{ DisplayName = 'SG-Dept-IT';         Description = 'NordWerk GmbH – IT department security group' },
    [pscustomobject]@{ DisplayName = 'SG-Dept-HR';         Description = 'NordWerk GmbH – HR department security group' },
    [pscustomobject]@{ DisplayName = 'SG-Dept-Finance';    Description = 'NordWerk GmbH – Finance department security group' },
    [pscustomobject]@{ DisplayName = 'SG-Dept-Sales';      Description = 'NordWerk GmbH – Sales department security group' },
    [pscustomobject]@{ DisplayName = 'SG-Dept-Operations'; Description = 'NordWerk GmbH – Operations department security group' },
    [pscustomobject]@{ DisplayName = 'GRP-CA-Pilot';       Description = 'Pilot group for Conditional Access policies' },
    [pscustomobject]@{ DisplayName = 'GRP-Devices-Pilot';  Description = 'Pilot group for Intune device policies' }
)

$results = foreach ($group in $baselineGroups) {
    $escapedName = $group.DisplayName.Replace("'", "''")
    $existing = @(Get-MgGroup -Filter "displayName eq '$escapedName'" -Property Id, DisplayName, Description)

    if ($existing.Count -gt 0) {
        [pscustomobject]@{
            DisplayName = $group.DisplayName
            Status      = 'Existing'
            ObjectId    = $existing[0].Id
            Action      = 'None'
        }
        continue
    }

    if ($PSCmdlet.ShouldProcess($group.DisplayName, 'Create Microsoft Entra security group')) {
        $mailNickname = ($group.DisplayName.ToLowerInvariant() -replace '[^a-z0-9-]', '-')
        $created = New-MgGroup `
            -DisplayName $group.DisplayName `
            -Description $group.Description `
            -MailEnabled:$false `
            -MailNickname $mailNickname `
            -SecurityEnabled

        [pscustomobject]@{
            DisplayName = $created.DisplayName
            Status      = 'Created'
            ObjectId    = $created.Id
            Action      = 'Created security group'
        }
    }
}

$results | Sort-Object DisplayName
