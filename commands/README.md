# Thư viện lệnh quét chuẩn

Toàn bộ lệnh chạy trên máy **Kali 10.10.99.10**, chỉ nhắm vào 4 dải mạng trong lab cách ly.
**Không** quét Internet, mạng trường hay máy thật.

| Hàm | Lệnh Nmap tương ứng | Dùng cho |
|-----|---------------------|----------|
| `discover <dải>` | `nmap -sn -PE -PS22,80,443,445 -PA3389` | Tầng 1 — tìm host sống |
| `quick <dải>` | `nmap -sS -T4 --top-ports 1000` | Quét nhanh định kỳ |
| `deep <host>` | `nmap -sS -sV -O -sC -p- -T3` | Quét sâu vùng Server/User |
| `ot <dải>` | `nmap -sT -T2 --max-rate 20 --scan-delay 100ms -sV --version-light -Pn` | Quét AN TOÀN vùng IoT/OT |
| `smb <dải>` | `--script smb-protocols,smb2-security-mode` | Phát hiện SMBv1 |
| `tls <dải>` | `--script ssl-enum-ciphers` | Phát hiện TLS/cipher yếu |
| `cred <dải>` | `--script ftp-anon,http-default-accounts,telnet-encryption` | Dịch vụ dùng mặc định/ẩn danh |
| `diff <cũ> <mới>` | `ndiff` | So sánh 2 lần quét |

## Nguyên tắc an toàn (theo Rules of Engagement)
- Vùng OT dùng `-T2 --max-rate 20`, **không** `-O`, **không** NSE nhóm `intrusive/brute/exploit/dos`.
- Thiết bị nhạy cảm đưa vào `scope/ot_exclude.txt`.
- Quét ngoài giờ sản xuất; dừng ngay nếu thiết bị mất phản hồi.

## Ví dụ một chu kỳ
```bash
export OUTDIR=scans/$(date +%Y%m%d-%H%M)
./scan-commands.sh discover 10.10.10.0/24
./scan-commands.sh deep 10.10.10.10
./scan-commands.sh ot 10.10.30.0/24
./scan-commands.sh smb 10.10.10.0/24
```
