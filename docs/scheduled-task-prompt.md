# Prompt cho scheduled task "Tổng hợp công nghệ hằng ngày"

Phần cuối này được thêm vào prompt hiện có (giữ nguyên toàn bộ phần tổng hợp 8 mảng và việc gửi bản tin bằng SendUserMessage). Việc đăng lên website chạy **sau** khi đã gửi bản tin, và nếu lỗi thì không ảnh hưởng đến bản tin gửi cho bạn.

```
Sau khi đã gửi bản tin cho người dùng bằng SendUserMessage, hãy đăng chính bản tin đó lên website:

1. Lập một đối tượng JSON từ bản tin vừa gửi, đúng schema trong README.md của repo:
   - date: ngày hiện tại theo giờ Asia/Bangkok, dạng YYYY-MM-DD; generated_at: thời điểm hiện tại, ISO 8601 UTC.
   - sections: đủ 8 mảng theo đúng thứ tự trên, mỗi mảng có title và items. Mỗi item gồm title, summary, apply (nếu có) và source {title, url} trỏ tới nguồn của chính mục đó.
   - knowledge: {title, body, example (nếu có)} cho mục "Kiến thức nên nhớ hôm nay".
   - sources: toàn bộ nguồn đã dùng.
   - Mọi chuỗi là văn bản thuần: không HTML, không markdown, không đánh dấu **đậm**.
2. Gắn repo bachxuantrann/daily-tech-digest bằng add_repo với access = "push", rồi clone theo lệnh trong kết quả trả về.
3. Ghi JSON vào một tệp tạm nằm ngoài repo, ví dụ /tmp/day.json, rồi chạy trong repo: python3 scripts/publish.py /tmp/day.json
   Nếu script báo lỗi validation, sửa JSON theo thông báo rồi chạy lại.
4. Trong repo: git add data && git commit -m "digest: YYYY-MM-DD" && git push origin main
5. Nếu bất kỳ bước nào ở 2-4 thất bại, đừng dừng cả phiên: gửi thêm một SendUserMessage ngắn nói bước nào lỗi và thông báo lỗi.
```
