#!/usr/bin/env bash
# ĐT-02 · run_audit.sh — một chu kỳ kiểm toán tự động (dùng cho cron).
# Quét 4 dải -> parser -> risk_check -> diff với lần trước -> alert -> report.
# Chạy trên Kali 10.10.99.10, trong thư mục gốc repo.
set -uo pipefail
cd "$(dirname "$0")/.."                      # về thư mục gốc repo
TS=$(date +%Y%m%d-%H%M)
export OUTDIR="scans/$TS"
mkdir -p "$OUTDIR" inventory

echo "==== [$TS] Bắt đầu chu kỳ kiểm toán ===="
START=$(date +%s)

# 1. Quét (dùng thư viện lệnh chuẩn)
bash commands/scan-commands.sh discover 10.10.10.0/24
bash commands/scan-commands.sh quick    10.10.10.0/24
bash commands/scan-commands.sh deep     10.10.10.10
bash commands/scan-commands.sh ot       10.10.30.0/24
bash commands/scan-commands.sh smb      10.10.10.0/24
bash commands/scan-commands.sh tls      10.10.10.0/24
bash commands/scan-commands.sh cred     10.10.30.0/24

# 2. Giữ inventory cũ để diff + tính first_seen
[ -f inventory/assets.json ] && cp inventory/assets.json inventory/prev.json

# 3. XML -> inventory
python3 scripts/parser.py -x "$OUTDIR"/*.xml \
    --owners inventory/owners.csv --prev inventory/prev.json \
    --out-json inventory/assets.json --out-csv inventory/assets.csv

# 4. Gán rủi ro
python3 scripts/risk_check.py --in inventory/assets.json --out inventory/assets.json

# 5. Diff + cảnh báo
if [ -f inventory/prev.json ]; then
  python3 scripts/diff.py --old inventory/prev.json --new inventory/assets.json \
      --out inventory/diff.json || python3 scripts/alert.py --diff inventory/diff.json
fi

# 6. Báo cáo HTML
python3 scripts/report.py --inv inventory/assets.json --diff inventory/diff.json \
    --out "$OUTDIR/report.html"

echo "==== Xong trong $(( $(date +%s) - START )) giây. Kết quả: $OUTDIR ===="
