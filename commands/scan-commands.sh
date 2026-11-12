#!/usr/bin/env bash
# ============================================================================
# ĐT-02 · Thư viện lệnh quét chuẩn (chạy trên Kali 10.10.99.10)
# Chỉ dùng trong lab VMware cách ly. KHÔNG quét Internet / mạng trường / máy thật.
# Cách dùng:  source scan-commands.sh   rồi gọi từng hàm, ví dụ:  scan_deep 10.10.10.10
# Hoặc chạy trực tiếp:  ./scan-commands.sh discover 10.10.10.0/24
# ============================================================================
set -euo pipefail

OUTDIR="${OUTDIR:-$(pwd)/scans/$(date +%Y%m%d-%H%M)}"
OT_EXCLUDE="${OT_EXCLUDE:-$(dirname "$0")/../scope/ot_exclude.txt}"
mkdir -p "$OUTDIR"

# --- Tầng 1: Khám phá host (cả 4 dải) -----------------------------------------
scan_discover() {  # $1 = dải, ví dụ 10.10.10.0/24
  nmap -sn -PE -PS22,80,443,445 -PA3389 "$1" -oA "$OUTDIR/discover_${1//\//_}"
}

# --- Quét nhanh định kỳ (top 1000 cổng) ---------------------------------------
scan_quick() {     # $1 = dải hoặc host
  nmap -sS -T4 --top-ports 1000 "$1" -oA "$OUTDIR/quick_${1//\//_}"
}

# --- Quét sâu (Server/User): cổng đầy đủ + dịch vụ + OS + NSE mặc định ---------
scan_deep() {      # $1 = host
  nmap -sS -sV -O -sC -p- -T3 "$1" -oA "$OUTDIR/deep_${1//\//_}"
}

# --- Quét AN TOÀN cho vùng IoT/OT (nhẹ nhàng, có loại trừ) ---------------------
scan_ot_safe() {   # $1 = dải OT, ví dụ 10.10.30.0/24
  local exc=()
  [ -f "$OT_EXCLUDE" ] && exc=(--excludefile "$OT_EXCLUDE")
  nmap -sT -T2 --max-rate 20 --scan-delay 100ms \
       -sV --version-light -Pn \
       "${exc[@]}" "$1" -oA "$OUTDIR/ot_${1//\//_}"
}

# --- NSE chọn lọc: phát hiện dịch vụ yếu (nhóm an toàn theo RoE) ---------------
scan_weak_smb() {  nmap -p445 --script smb-protocols,smb2-security-mode "$1" -oA "$OUTDIR/smb_${1//\//_}"; }
scan_weak_tls() {  nmap -p443,465,993,995,8443 --script ssl-enum-ciphers "$1" -oA "$OUTDIR/tls_${1//\//_}"; }
scan_weak_cred() { nmap -p21,23,80,8080 --script ftp-anon,http-default-accounts,telnet-encryption "$1" -oA "$OUTDIR/cred_${1//\//_}"; }

# --- So sánh 2 lần quét -------------------------------------------------------
scan_diff() {      # $1 = xml cũ, $2 = xml mới
  ndiff "$1" "$2"
}

# --- Chạy trực tiếp từ dòng lệnh ----------------------------------------------
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  cmd="${1:-}"; shift || true
  case "$cmd" in
    discover)  scan_discover "$@";;
    quick)     scan_quick "$@";;
    deep)      scan_deep "$@";;
    ot)        scan_ot_safe "$@";;
    smb)       scan_weak_smb "$@";;
    tls)       scan_weak_tls "$@";;
    cred)      scan_weak_cred "$@";;
    diff)      scan_diff "$@";;
    *) echo "Dùng: $0 {discover|quick|deep|ot|smb|tls|cred|diff} <đối số>"; exit 1;;
  esac
  echo "Kết quả lưu tại: $OUTDIR"
fi
