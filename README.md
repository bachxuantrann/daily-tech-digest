# Bản tin công nghệ hằng ngày

Website tĩnh hiển thị bản tin do scheduled task trong Claude tổng hợp mỗi sáng. Không có backend và không có bước build: `index.html` đọc các tệp JSON trong `data/`.

## Cấu trúc

```
index.html              trang web (HTML + CSS + JS trong một tệp)
data/index.json         danh sách ngày có bản tin (mới nhất trước) kèm tóm tắt từng ngày
data/YYYY-MM-DD.json    nội dung bản tin của từng ngày
scripts/publish.py      kiểm tra một tệp JSON và ghi vào data/
docs/                   prompt mẫu cho scheduled task
```

## Luồng dữ liệu

1. Scheduled task chạy lúc 08:21 (giờ Việt Nam), tổng hợp bản tin và gửi cho bạn như trước.
2. Cùng lần chạy đó, task ghi bản tin thành JSON, chạy `python3 scripts/publish.py <tệp>`, rồi `git commit` và `git push`.
3. Cloudflare Pages (hoặc GitHub Pages) thấy commit mới và tự deploy lại, thường trong 1-2 phút.

`publish.py` từ chối tệp sai schema, nên một lần chạy lỗi không làm hỏng site: dữ liệu cũ vẫn giữ nguyên.

## Triển khai

**Cloudflare Pages** (dùng được cả với repo private): Workers & Pages → Create → Pages → Connect to Git → chọn repo. Framework preset: None. Build command: để trống. Build output directory: `/`.

**GitHub Pages** (repo phải public với tài khoản miễn phí): Settings → Pages → Source: Deploy from a branch → Branch `main`, thư mục `/ (root)`.

## Schema của `data/YYYY-MM-DD.json`

```json
{
  "date": "2026-10-18",
  "generated_at": "2026-10-18T01:22:00Z",
  "summary": "Bắt buộc: 1-2 câu nêu điểm đáng chú ý nhất ngày hôm đó (dưới 300 ký tự). Hiện ở đầu trang và trong trang lưu trữ.",
  "sections": [
    {
      "title": "Backend",
      "items": [
        {
          "title": "Tiêu đề mục",
          "summary": "1-2 câu giải thích.",
          "apply": "Tuỳ chọn: gợi ý áp dụng.",
          "source": { "title": "Tên bài", "url": "https://..." },
          "published": "Tuỳ chọn: ngày đăng gốc, 2026-09-12 hoặc 2026-09",
          "kind": "Tuỳ chọn: \"tin\" (tin mới) hoặc \"bài đọc\" (bài cũ nhưng đáng đọc, hiện nhãn riêng)"
        }
      ]
    }
  ],
  "knowledge": {
    "title": "Tên khái niệm",
    "body": "Đoạn 1.\n\nĐoạn 2.",
    "example": "Tuỳ chọn: ví dụ ngắn, hiển thị dạng code."
  },
  "sources": [{ "title": "Tên bài", "url": "https://..." }]
}
```

`generated_at` luôn do `publish.py` ghi lại theo đồng hồ hệ thống, giá trị trong tệp đầu vào bị bỏ qua (mô hình không có đồng hồ nên hay đoán sai giờ).

Mọi chuỗi là văn bản thuần. Trang luôn hiển thị bằng `textContent` và chỉ mở link `http(s)`, nên nội dung lấy từ web không thể chèn script vào trang.

## Lưu trữ theo ngày

Mỗi ngày là một tệp `data/YYYY-MM-DD.json` và không bao giờ bị xoá. Trên site, cột trái liệt kê 10 ngày gần nhất, còn trang **Tất cả bản tin** (`#luu-tru`) liệt kê mọi ngày kèm tóm tắt và có ô tìm theo từ khoá. Mỗi ngày có địa chỉ riêng dạng `…/#2026-10-17`.

Nếu `data/index.json` bị lệch so với các tệp ngày (ví dụ sau khi sửa tay), chạy `python3 scripts/publish.py --reindex` để dựng lại.

## Thử cục bộ

```
python3 -m http.server 8000
```

Mở http://localhost:8000. Mở trực tiếp bằng `file://` sẽ không chạy vì trình duyệt chặn `fetch`.
