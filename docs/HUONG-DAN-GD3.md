# Hướng dẫn thực hiện Giai đoạn 3 (Triển khai)

Mục tiêu GĐ3: lab tái lập được từ repo, công cụ chính chạy được, có bằng chứng định lượng (điều kiện cổng G2).

## Bước 1 — Dựng mạng (VMware Virtual Network Editor)
- Tạo VMnet2–5 host-only, tắt DHCP, bỏ "Connect a host virtual adapter".
- Dựng pfSense: 4 card nối 4 VMnet, đặt .1 mỗi dải, không gắn WAN khi quét.
- Kiểm tra định tuyến: từ Kali ping được .10/.20 (vùng Server) và .30 (vùng IoT).

## Bước 2 — Dựng máy ảo
| VM | IP | Việc |
|----|----|------|
| Win Server 2022 | 10.10.10.10 | chạy `lab/win2022-setup.ps1` |
| Ubuntu Server | 10.10.10.20 | chạy `lab/ubuntu-setup.sh` |
| IoT giả lập | 10.10.30.50 | `cd lab/iot && docker compose up -d` |
| Kali | 10.10.99.10 | cài nmap, ndiff, python3 |

Chụp **snapshot "baseline"** mọi VM trước khi quét.

## Bước 3 — Quét lần 1 và sinh inventory
```bash
cd DT02-nmap-audit
bash scripts/run_audit.sh
```
Ghi lại thời gian chạy (in ở cuối) để tính KPI "thời gian 1 chu kỳ".

## Bước 4 — Mô phỏng shadow IT và quét lần 2
```bash
# trên Ubuntu
sudo apt-get install -y vsftpd && sudo systemctl enable --now vsftpd
# trên Kali
bash scripts/run_audit.sh
```
→ `inventory/diff.json` và cảnh báo phải hiện cổng 21 mới mở trên 10.10.10.20.

## Bước 5 — Thu thập bằng chứng cho cổng G2
- [ ] Script dựng lab + `lab/README.md` (lab tái lập được).
- [ ] `scans/<lần-1>/*.xml` và `scans/<lần-2>/*.xml`.
- [ ] `inventory/assets.json` + `assets.csv` (danh mục tài sản).
- [ ] `inventory/diff.json` + ảnh chụp cảnh báo (phát hiện thay đổi).
- [ ] `report.html` của mỗi lần quét.
- [ ] Số liệu KPI: độ phủ, số dịch vụ rủi ro cao, thời gian chu kỳ.

## KPI — cách lấy số liệu
- **Độ phủ** = số IP trong assets.json / số host trong owners.csv × 100%.
- **Dịch vụ rủi ro cao** = số bản ghi `risk = cao` (risk_check in ra khi chạy).
- **Thời gian chu kỳ** = dòng "Xong trong … giây" của `run_audit.sh`.

## Nhật ký AI
Mỗi lần dùng AI, ghi vào `docs/ai-log.md`: mục đích, prompt tóm tắt, dùng vào đâu, cách tự kiểm chứng.
