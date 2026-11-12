#!/usr/bin/env bash
# ĐT-02 · Dựng máy chủ ứng dụng Ubuntu trong lab (10.10.10.20)
# Vai trò: SSH, Nginx (web), MySQL (CSDL). Chạy với sudo trên VM Ubuntu Server.
# CHỈ dùng trong lab cách ly phục vụ học tập.
set -euo pipefail

# --- 1. Mạng tĩnh (netplan) --------------------------------------------------
cat >/etc/netplan/01-lab.yaml <<'EOF'
network:
  version: 2
  ethernets:
    ens33:
      addresses: [10.10.10.20/24]
      routes:
        - to: default
          via: 10.10.10.1
      nameservers:
        addresses: [10.10.10.10]
EOF
chmod 600 /etc/netplan/01-lab.yaml
netplan apply || true

# --- 2. Cài dịch vụ ----------------------------------------------------------
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y openssh-server nginx mysql-server

# --- 3. Web nội bộ -----------------------------------------------------------
echo "<h1>ABC Corp - App Server (lab)</h1>" >/var/www/html/index.html

# --- 4. Bật dịch vụ ----------------------------------------------------------
systemctl enable --now ssh nginx mysql

echo "Hoàn tất cấu hình Ubuntu Server. Hãy chụp snapshot 'baseline'."
echo "Để mô phỏng 'dịch vụ mới mở trái phép' ở lần quét 2, chạy: sudo apt-get install -y vsftpd && sudo systemctl enable --now vsftpd"
