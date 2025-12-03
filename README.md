# 📰 Facebook RSS Feed Generator

Tự động tạo RSS feeds từ các trang Facebook công khai, sử dụng GitHub Actions.

## 🌐 Live Feeds

Sau khi cài đặt, feeds của bạn sẽ có tại:
- **Trang chủ:** `https://[username].github.io/[repo-name]`
- **RSS Feed:** `https://[username].github.io/[repo-name]/feeds/[ten-feed].xml`

## ⚙️ Cấu hình

Chỉnh sửa file `config.json`:

```json
{
    "facebook_pages": [
        {
            "name": "Tên hiển thị",
            "username": "username-facebook",
            "max_posts": 10,
            "rss_filename": "output.xml"
        }
    ],
    "update_interval_hours": 1
}
```

## 🔧 Cài đặt

1. Fork repository này
2. Sửa file `config.json` với trang Facebook bạn muốn
3. Repository sẽ tự động chạy mỗi giờ

## 📡 Sử dụng RSS Feed

Thêm feed vào WordPress/RSS reader:
```
https://[username].github.io/[repo-name]/feeds/[ten-file].xml
```

## 🛠 Công nghệ

- Python + facebook-scraper
- GitHub Actions (chạy tự động)
- GitHub Pages (hosting miễn phí)
