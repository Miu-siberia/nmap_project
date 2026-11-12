# ĐT-02 · Kiểm toán và lập bản đồ bề mặt tấn công

Công cụ kiểm toán tài sản **phòng thủ** bằng Nmap cho hạ tầng doanh nghiệp giả định,
chạy hoàn toàn trong lab VMware cách ly. Tự động: quét → danh mục tài sản → phát hiện
dịch vụ rủi ro → so sánh giữa các lần quét → cảnh báo thay đổi trái phép.

> ⚠️ Chỉ quét trong lab cách ly tự dựng. KHÔNG nhắm vào hệ thống thật, mạng trường hay Internet.
> Phải có văn bản phạm vi (RoE) được GV duyệt trước khi quét.

## Cấu trúc
```
scope/      · RoE, ot_exclude.txt
commands/   · thư viện lệnh quét chuẩn
lab/        · script dựng VM (Win Server, Ubuntu, IoT)
scripts/    · parser, risk_check, diff, alert, report, run_audit
inventory/  · schema.json, owners.csv, assets.json/csv, diff.json
scans/      · lịch sử XML theo thời gian
docs/       · tài liệu GĐ1–GĐ2, hướng dẫn, nhật ký AI
```

## Yêu cầu
- Kali Linux (hoặc máy có `nmap`, `ndiff`, `python3`).
- Pipeline chỉ dùng thư viện chuẩn Python 3 — không cần cài thêm.

## Quy trình GĐ3
1. Dựng lab theo `lab/README.md`, chụp snapshot baseline.
2. Chạy một chu kỳ:
   ```bash
   bash scripts/run_audit.sh
   ```
3. Mô phỏng shadow IT rồi quét lại để kiểm tra diff:
   ```bash
   # trên Ubuntu: bật thêm FTP
   sudo apt-get install -y vsftpd && sudo systemctl enable --now vsftpd
   bash scripts/run_audit.sh        # lần 2 -> diff phát hiện cổng 21 mới
   ```
4. Tự động hóa định kỳ (cron, ví dụ 20h mỗi ngày):
   ```
   0 20 * * * cd /root/DT02-nmap-audit && bash scripts/run_audit.sh >> scans/cron.log 2>&1
   ```
5. Cảnh báo Telegram (tùy chọn):
   ```bash
   export TELEGRAM_BOT_TOKEN=xxxx TELEGRAM_CHAT_ID=yyyy
   ```

## Chạy từng bước (gỡ lỗi)
```bash
python3 scripts/parser.py -x scans/20261103-2010/*.xml --owners inventory/owners.csv \
    --out-json inventory/assets.json --out-csv inventory/assets.csv
python3 scripts/risk_check.py --in inventory/assets.json --out inventory/assets.json
python3 scripts/diff.py --old inventory/prev.json --new inventory/assets.json --out inventory/diff.json
python3 scripts/report.py --inv inventory/assets.json --diff inventory/diff.json --out report.html
```
