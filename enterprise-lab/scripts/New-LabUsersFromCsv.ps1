[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [Parameter(Mandatory)]
    [ValidateScript({ Test-Path -LiteralPath $_ })]
    [string]$CsvPath
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Module -ListAvailable -Name Microsoft.Graph.Users)) {
    throw 'Microsoft.Graph.Users ist nicht installiert. Install-Module Microsoft.Graph -Scope CurrentUser ausführen.'
}

Import-Module Microsoft.Graph.Users

function Get-RandomInitialPassword {
    $bytes = New-Object byte[] 24
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    return ([Convert]::ToBase64String($bytes) + 'aA1!')
}

$requiredColumns = @(
    'DisplayName',
    'GivenName',
    'Surname',
    'UserPrincipalName',
    'Department',
    'JobTitle',
    'UsageLocation'
)

$rows = @(Import-Csv -LiteralPath $CsvPath)
if ($rows.Count -eq 0) {
    throw 'Die CSV-Datei enthält keine Benutzer.'
}

$actualColumns = $rows[0].PSObject.Properties.Name
foreach ($column in $requiredColumns) {
    if ($column -notin $actualColumns) {
        throw "Pflichtspalte '$column' fehlt in der CSV-Datei."
    }
}

foreach ($row in $rows) {
    $upn = [string]$row.UserPrincipalName
    $upn = $upn.Trim()

    if ([string]::IsNullOrWhiteSpace($upn) -or $upn -like '*TENANTNAME*') {
        [pscustomobject]@{
            UserPrincipalName = $upn
            Status            = 'Skipped'
            Reason            = 'UPN fehlt oder TENANTNAME wurde nicht ersetzt.'
            InitialPassword   = $null
        }
        continue
    }

    $escapedUpn = $upn.Replace("'", "''")
    $existingUser = Get-MgUser -Filter "userPrincipalName eq '$escapedUpn'" -Property Id, DisplayName, UserPrincipalName

    if ($existingUser) {
        [pscustomobject]@{
            UserPrincipalName = $upn
            Status            = 'Skipped'
            Reason            = 'Benutzer existiert bereits.'
            InitialPassword   = $null
        }
        continue
    }

    $target = "$($row.DisplayName) <$upn>"
    if ($PSCmdlet.ShouldProcess($target, 'Create Microsoft Entra test user')) {
        $initialPassword = Get-RandomInitialPassword
        $mailNickname = ($upn.Split('@')[0] -replace '[^a-zA-Z0-9._-]', '')

        $body = @{
            accountEnabled    = $true
            displayName       = [string]$row.DisplayName
            givenName         = [string]$row.GivenName
            surname           = [string]$row.Surname
            userPrincipalName = $upn
            mailNickname      = $mailNickname
            department        = [string]$row.Department
            jobTitle          = [string]$row.JobTitle
            usageLocation     = [string]$row.UsageLocation
            passwordProfile   = @{
                forceChangePasswordNextSignIn = $true
                password                      = $initialPassword
            }
        }

        $newUser = New-MgUser -BodyParameter $body

        [pscustomobject]@{
            UserPrincipalName = $newUser.UserPrincipalName
            Status            = 'Created'
            Reason            = 'Test user created successfully.'
            InitialPassword   = $initialPassword
        }
    }
}

Write-Warning 'InitialPassword-Werte sind nur für das Test-Lab gedacht. Nicht in Dateien, Git oder Screenshots speichern.'
