<#
  ĐT-02 · Dựng máy chủ Windows Server 2022 trong lab (10.10.10.10)
  Vai trò: AD DS, file share (SMB), IIS, RDP — máy chủ hạ tầng doanh nghiệp.
  Chạy trong PowerShell (Run as Administrator) trên VM Win Server 2022.
  CHỈ dùng trong lab cách ly phục vụ học tập.
#>

# --- 1. Mạng tĩnh ------------------------------------------------------------
$If = (Get-NetAdapter | Where-Object Status -eq 'Up')[0].Name
New-NetIPAddress -InterfaceAlias $If -IPAddress 10.10.10.10 -PrefixLength 24 -DefaultGateway 10.10.10.1 -ErrorAction SilentlyContinue
Set-DnsClientServerAddress -InterfaceAlias $If -ServerAddresses 127.0.0.1

# --- 2. Vai trò máy chủ ------------------------------------------------------
Install-WindowsFeature AD-Domain-Services, DNS, Web-Server, FS-FileServer -IncludeManagementTools

# --- 3. Nâng cấp lên Domain Controller (lab: N7QTM.local) --------------------
# Chạy một lần; máy sẽ khởi động lại.
Import-Module ADDSDeployment
# Install-ADDSForest -DomainName "N7QTM.local" -InstallDns -Force   # bỏ comment khi dựng AD

# --- 4. File share qua SMB ---------------------------------------------------
New-Item -Path "C:\Shares\Data" -ItemType Directory -Force | Out-Null
New-SmbShare -Name "Data" -Path "C:\Shares\Data" -FullAccess "Everyone" -ErrorAction SilentlyContinue

# --- 5. Web nội bộ (IIS) -----------------------------------------------------
"<h1>ABC Corp - Internal Portal (lab)</h1>" | Out-File "C:\inetpub\wwwroot\index.html" -Encoding utf8

# --- 6. Bật RDP --------------------------------------------------------------
Set-ItemProperty 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name "fDenyTSConnections" -Value 0
Enable-NetFirewallRule -DisplayGroup "Remote Desktop"

# --- 7. (Chủ ý để mô phỏng hệ thống cũ) Bật SMBv1 để kiểm toán phát hiện ------
#   LƯU Ý: chỉ bật trong lab để script risk_check phát hiện và khuyến nghị tắt.
Enable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart -ErrorAction SilentlyContinue

Write-Host "Hoàn tất cấu hình Win Server 2022. Hãy chụp snapshot 'baseline'."
