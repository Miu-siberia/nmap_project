# Dựng lab trong VMware

## Mạng (Virtual Network Editor)
Tạo 4 VMnet host-only, **tắt DHCP**, bỏ "Connect a host virtual adapter":

| VMnet | Vùng | Dải |
|-------|------|-----|
| VMnet2 | Server | 10.10.10.0/24 |
| VMnet3 | User | 10.10.20.0/24 |
| VMnet4 | IoT/OT | 10.10.30.0/24 |
| VMnet5 | Quản trị | 10.10.99.0/24 |

pfSense có 4 card nối 4 VMnet, đặt .1 mỗi dải, **không gắn WAN** khi quét.

## Máy ảo
| VM | IP | Script |
|----|----|--------|
| Windows Server 2022 | 10.10.10.10 | `win2022-setup.ps1` |
| Ubuntu Server | 10.10.10.20 | `ubuntu-setup.sh` |
| Kali (máy quét) | 10.10.99.10 | cài nmap, python3, ndiff |
| IoT giả lập | 10.10.30.50 | `iot/docker-compose.yml` |

## Thứ tự
1. Dựng pfSense + 4 VMnet, kiểm tra ping giữa các vùng.
2. Chạy script dựng từng VM.
3. **Chụp snapshot "baseline"** mọi VM trước lần quét đầu.
4. Dựng xong → sang `scripts/run_audit.sh` để quét.

> Thiết bị IoT giả lập là host cố ý yếu, chỉ để kiểm toán phát hiện trong lab cách ly.
