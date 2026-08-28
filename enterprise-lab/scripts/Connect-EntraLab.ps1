[CmdletBinding()]
param(
    [ValidateSet('Delegated', 'AppOnly')]
    [string]$Mode = 'Delegated',

    [string]$TenantId,
    [string]$ClientId,
    [string]$CertificateThumbprint,

    [string[]]$Scopes = @(
        'User.ReadWrite.All',
        'Group.ReadWrite.All',
        'Organization.Read.All',
        'AuditLog.Read.All',
        'DeviceManagementManagedDevices.Read.All',
        'DeviceManagementConfiguration.Read.All'
    )
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Module -ListAvailable -Name Microsoft.Graph.Authentication)) {
    throw 'Microsoft.Graph ist nicht installiert. Install-Module Microsoft.Graph -Scope CurrentUser ausführen.'
}

Import-Module Microsoft.Graph.Authentication

if ($Mode -eq 'Delegated') {
    Connect-MgGraph -Scopes $Scopes -ContextScope Process -NoWelcome
}
else {
    foreach ($requiredValue in @{
        TenantId              = $TenantId
        ClientId              = $ClientId
        CertificateThumbprint = $CertificateThumbprint
    }.GetEnumerator()) {
        if ([string]::IsNullOrWhiteSpace([string]$requiredValue.Value)) {
            throw "Für AppOnly fehlt der Parameter -$($requiredValue.Key)."
        }
    }

    $connectionParameters = @{
        TenantId              = $TenantId
        ClientId              = $ClientId
        CertificateThumbprint = $CertificateThumbprint
        ContextScope          = 'Process'
        NoWelcome             = $true
    }

    Connect-MgGraph @connectionParameters
}

$context = Get-MgContext

[pscustomobject]@{
    Mode        = $Mode
    TenantId    = $context.TenantId
    ClientId    = $context.ClientId
    Account     = $context.Account
    AuthType    = $context.AuthType
    Scopes      = ($context.Scopes -join ', ')
    ConnectedAt = Get-Date
}
