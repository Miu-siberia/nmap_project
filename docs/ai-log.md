# Nhật ký sử dụng AI (Phụ lục)

Trợ lý AI: Claude (Anthropic). Mọi lệnh và script đều được chạy lại trong lab để kiểm chứng.

| Ngày | Mục đích | Nội dung hỏi (tóm tắt) | Kết quả dùng vào đâu | Cách tự kiểm chứng |
|------|----------|------------------------|----------------------|--------------------|
| 24/10/2026 | Lập kế hoạch đồ án | Đưa đề ĐT-02, xin lộ trình 3 tuần và mô hình lab trên VMware | Kế hoạch đồ án | Đối chiếu từng mục với yêu cầu 5 giai đoạn của đề |
| 24–31/10/2026 | Phân tích và thiết kế | Xin gợi ý văn bản phạm vi, chiến lược quét phân tầng, lược đồ inventory | Tài liệu GĐ1, GĐ2 | Tự đọc lại, chỉnh theo lab thực tế (VMnet12–15) |
| 07/11/2026 | Học lệnh Nmap | Hỏi ý nghĩa các tham số -sn, -PS, -Pn, -sV, -oX, NSE | Thư viện lệnh commands/ | Chạy từng lệnh trong lab, so kết quả với tài liệu Nmap |
| 10–11/11/2026 | Xử lý sự cố lab | Hỏi cách gán cổng pfSense, sửa card Alpine, netplan Ubuntu, xung đột IP .1 | Cấu hình pfSense, .vmx, route | Kiểm tra bằng ping và nmap thực tế trước và sau khi sửa |
| 10–11/11/2026 | Viết pipeline | Xin khung script parser, risk_check, diff, alert, report, run_audit | Thư mục scripts/ | Đọc lại code, chạy với XML thật, đối chiếu diff.py với ndiff |
| 12/11/2026 | Demo và đọc kết quả | Gửi ảnh kết quả, hỏi cách giải thích cổng 9389 và banner Kerberos | Mục hạn chế trong báo cáo | Quét lại bằng đúng lệnh lần 1 để xác nhận nguyên nhân |
| 12–13/11/2026 | Soạn tài liệu | Nhờ trình bày báo cáo và slide từ số liệu, ảnh thật | Tài liệu GĐ3–GĐ5, báo cáo cuối, slide | Soát từng số liệu với ảnh chụp màn hình gốc |
