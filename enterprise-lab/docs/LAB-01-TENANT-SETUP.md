# LAB-01 – NordWerk GmbH Tenant Baseline

## Ziel

Eine saubere, reproduzierbare Ausgangsbasis für das EntraFlow Enterprise IT Lab schaffen. Dieses Lab wird ausschließlich mit Testkonten und Testgeräten betrieben.

## 1. Testtenant bereitstellen

Empfohlener Weg: Microsoft Intune 30-Tage-Testversion. Die Registrierung erstellt einen neuen Microsoft-Entra-Tenant und stellt die für das Intune-Lab benötigte Umgebung bereit.

Bei der Registrierung:

- Firmenname: `NordWerk GmbH`
- Land/Region: eigenes tatsächliches Land auswählen
- Tenant-Domain: einen verfügbaren neutralen Lab-Namen verwenden, z. B. `nordwerk-itlab.onmicrosoft.com`
- Das zuerst angelegte Administratorkonto ausschließlich für die Lab-Verwaltung verwenden
- Kennwörter, Tenant-IDs, Client-Secrets und Zertifikate niemals in GitHub speichern

## 2. PowerShell vorbereiten

```powershell
pwsh --version
Install-Module Microsoft.Graph -Scope CurrentUser
```

Repository klonen bzw. aktualisieren:

```bash
git clone https://github.com/haydarkozat/entraflow.git
cd entraflow/enterprise-lab/scripts
```

Microsoft Graph verbinden:

```powershell
./Connect-EntraLab.ps1
```

Verbindung kontrollieren:

```powershell
Get-MgContext | Select-Object TenantId, Account, AuthType, Scopes
```

## 3. Baseline-Gruppen zunächst simulieren

```powershell
./Initialize-TenantBaseline.ps1 -WhatIf
```

Beklenen hedef gruplar:

- `SG-Dept-IT`
- `SG-Dept-HR`
- `SG-Dept-Finance`
- `SG-Dept-Sales`
- `SG-Dept-Operations`
- `GRP-CA-Pilot`
- `GRP-Devices-Pilot`

## 4. Baseline-Gruppen erstellen

`-WhatIf` çıktısını kontrol ettikten sonra:

```powershell
./Initialize-TenantBaseline.ps1
```

İkinci kez çalıştırıldığında mevcut gruplar `Existing` olarak görünmeli ve yinelenen grup oluşturmamalıdır.

## 5. Doğrulama

```powershell
Get-MgGroup -All |
    Where-Object DisplayName -In @(
        'SG-Dept-IT',
        'SG-Dept-HR',
        'SG-Dept-Finance',
        'SG-Dept-Sales',
        'SG-Dept-Operations',
        'GRP-CA-Pilot',
        'GRP-Devices-Pilot'
    ) |
    Select-Object DisplayName, Id |
    Sort-Object DisplayName
```

## 6. Evidence

LAB-01 ancak aşağıdaki kanıtlar üretildikten sonra tamamlanmış sayılır:

1. Intune/Entra yönetim merkezinde tenant genel görünümü – tenant ID gibi hassas olmayan bilgiler gerekirse kısmen redakte edilir.
2. Yedi baseline grubunun Entra ID ekran görüntüsü.
3. `Initialize-TenantBaseline.ps1 -WhatIf` terminal çıktısı.
4. Script gerçek çalıştırıldıktan sonraki terminal çıktısı.
5. İkinci çalıştırmada duplicate oluşmadığını gösteren `Existing` çıktısı.
6. `evidence/LAB-01-baseline.md` dosyasında kısa teknik değerlendirme.

## Güvenlik kararı

LAB-01 aşamasında Conditional Access politikası etkinleştirilmez. Önce pilot gruplar oluşturulur, erişim senaryoları daha sonraki lablarda test/report-only yaklaşımıyla uygulanır. Global Administrator rolü günlük kullanım için hedef rol değildir; mümkün olan sonraki adımlarda daha dar kapsamlı roller kullanılacaktır.
