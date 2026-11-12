#!/usr/bin/env python3
"""ĐT-02 · risk_check.py — gán mức rủi ro cho từng dịch vụ trong inventory.

Dựa trên dịch vụ, phiên bản và kết quả NSE để phân loại: cao / trung bình / thấp.
Mục đích PHÒNG THỦ: chỉ ra chỗ cần hardening (đóng cổng, vá, phân vùng).

Ví dụ:
  python3 risk_check.py --in inventory/assets.json --out inventory/assets.json
"""
import argparse, csv, json, re, sys

CSV_FIELDS = ["host", "ip", "mac", "os", "port", "proto", "service",
              "version", "owner", "risk", "risk_reason", "first_seen", "last_seen"]

# Dịch vụ/giao thức cũ hoặc không mã hóa -> rủi ro cao
HIGH_SERVICES = {"telnet", "ftp", "tftp", "rlogin", "rexec", "vnc", "rsh"}
# Chuỗi phiên bản lỗi thời nổi tiếng (mô phỏng trong lab)
OUTDATED = [
    "vsftpd 2.3.4", "ProFTPD 1.3.3", "OpenSSH 4.", "Apache 2.2",
    "UnrealIRCd", "distccd", "Samba 3.", "mysql 5.0",
]


def assess(rec):
    svc = (rec.get("service") or "").lower()
    ver = (rec.get("version") or "")
    scripts = rec.get("scripts", {})
    reasons = []
    level = "thấp"

    # 1. Dịch vụ không mã hóa / cũ
    if svc in HIGH_SERVICES:
        level = "cao"; reasons.append(f"dịch vụ {svc} không an toàn")

    # 2. SMBv1 (smb-protocols output có SMBv1 / NT LM 0.12)
    smb = scripts.get("smb-protocols", "")
    if "SMBv1" in smb or "NT LM 0.12" in smb:
        level = "cao"; reasons.append("SMBv1 còn bật")

    # 3. TLS cũ / cipher yếu (ssl-enum-ciphers)
    tls = scripts.get("ssl-enum-ciphers", "")
    if re.search(r"TLSv1\.0|TLSv1\.1|SSLv3", tls) or "weak" in tls.lower() \
            or re.search(r"\bF\b", tls):  # Nmap chấm điểm F cho cipher yếu
        level = "cao"; reasons.append("TLS/cipher yếu")

    # 4. FTP ẩn danh
    if "Anonymous FTP login allowed" in scripts.get("ftp-anon", ""):
        level = "cao"; reasons.append("FTP cho đăng nhập ẩn danh")

    # 5. Tài khoản web mặc định
    if scripts.get("http-default-accounts", "").strip():
        level = "cao"; reasons.append("tài khoản web mặc định")

    # 6. Phiên bản lỗi thời đã biết
    for pat in OUTDATED:
        if pat.lower() in ver.lower():
            level = "cao"; reasons.append(f"phiên bản lỗi thời ({pat})")
            break

    # 7. Dịch vụ quản trị không TLS -> ít nhất trung bình
    if level == "thấp" and svc in {"http", "rdp", "ms-wbt-server", "mysql", "microsoft-ds"}:
        level = "trung bình"; reasons.append("dịch vụ quản trị/CSDL phơi ra mạng")

    return level, "; ".join(reasons) if reasons else "không phát hiện dấu hiệu rủi ro"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="inventory/assets.json")
    ap.add_argument("--out", default="inventory/assets.json")
    ap.add_argument("--out-csv", default="inventory/assets.csv",
                    help="ghi lại CSV kèm cột risk")
    args = ap.parse_args()

    with open(args.inp, encoding="utf-8") as f:
        recs = json.load(f)

    counts = {"cao": 0, "trung bình": 0, "thấp": 0}
    for r in recs:
        level, reason = assess(r)
        r["risk"] = level
        r["risk_reason"] = reason
        counts[level] += 1

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=2)
    if args.out_csv:
        with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
            w.writeheader()
            for r in recs:
                w.writerow(r)

    print(f"[+] Đánh giá {len(recs)} dịch vụ -> "
          f"cao={counts['cao']}, trung bình={counts['trung bình']}, thấp={counts['thấp']}")
    for r in recs:
        if r["risk"] == "cao":
            print(f"    [CAO] {r['ip']}:{r['port']} {r['service']} — {r['risk_reason']}")


if __name__ == "__main__":
    main()
