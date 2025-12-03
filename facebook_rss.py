#!/usr/bin/env python3
"""
Script tạo RSS Feed từ Facebook - Dùng cho GitHub Actions
FIXED VERSION
"""

import json
import os
import sys
from datetime import datetime, timezone

# ===== FIX IMPORT ERROR =====
try:
    from facebook_scraper import get_posts
    print("✅ Đã import facebook-scraper thành công")
except ImportError as e:
    print(f"❌ Lỗi import: {e}")
    print("📦 Đang cài đặt dependencies...")
    os.system(f"{sys.executable} -m pip install facebook-scraper==0.2.63 lxml html5lib --quiet")
    from facebook_scraper import get_posts

try:
    from feedgen.feed import FeedGenerator
except ImportError:
    os.system(f"{sys.executable} -m pip install feedgen --quiet")
    from feedgen.feed import FeedGenerator

try:
    import pytz
except ImportError:
    os.system(f"{sys.executable} -m pip install pytz --quiet")
    import pytz
# ============================

# Đọc cấu hình
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# ... (phần còn lại giữ nguyên từ dòng này trở đi)
#!/usr/bin/env python3
"""
Script tạo RSS Feed từ Facebook - Dùng cho GitHub Actions
"""

import json
import os
from datetime import datetime, timezone
from facebook_scraper import get_posts
from feedgen.feed import FeedGenerator
import pytz

# Đọc cấu hình
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Múi giờ Việt Nam
vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

def create_rss_for_page(page_config):
    """Tạo RSS feed cho một trang Facebook"""
    print(f"📱 Đang xử lý trang: {page_config['name']} (@{page_config['username']})")
    
    try:
        # Lấy bài viết từ Facebook
        posts = []
        for post in get_posts(
            page_config['username'],
            pages=2,  # Lấy 2 trang đầu
            options={
                "comments": False,
                "reactors": False,
                "progress": False
            }
        ):
            posts.append(post)
            if len(posts) >= page_config['max_posts']:
                break
        
        if not posts:
            print(f"⚠ Không lấy được bài viết từ {page_config['name']}")
            return False
        
        print(f"✅ Đã lấy {len(posts)} bài viết từ {page_config['name']}")
        
        # Tạo RSS feed
        fg = FeedGenerator()
        fg.title(f"{page_config['name']} - Facebook Updates")
        fg.description(f"Bài viết mới nhất từ {page_config['name']} trên Facebook")
        fg.link(href=f"https://facebook.com/{page_config['username']}", rel='alternate')
        fg.language('vi')
        fg.lastBuildDate(datetime.now(timezone.utc))
        
        for post in posts:
            fe = fg.add_entry()
            
            # Tiêu đề (lấy 100 ký tự đầu)
            title = post.get('post_text', '')[:100] or f"Bài viết từ {page_config['name']}"
            fe.title(title)
            
            # Link bài viết
            post_url = post.get('post_url') or f"https://facebook.com/{page_config['username']}"
            fe.link(href=post_url)
            
            # Nội dung
            content = ""
            if post.get('post_text'):
                content += f"<p>{post['post_text']}</p>"
            if post.get('image'):
                content += f'<img src="{post["image"]}" alt="Hình ảnh" style="max-width:100%;">'
            if post.get('video'):
                content += f'<p><a href="{post["video"]}">📹 Xem video</a></p>'
            
            if content:
                fe.content(content, type='CDATA')
            
            # Thời gian đăng (convert sang timezone VN)
            if post.get('time'):
                # Chuyển sang múi giờ VN
                post_time_utc = post['time'].replace(tzinfo=timezone.utc)
                post_time_vn = post_time_utc.astimezone(vietnam_tz)
                fe.pubDate(post_time_vn)
            
            # Thêm một số metadata
            if post.get('likes'):
                fe.description(f"👍 {post['likes']} lượt thích")
        
        # Lưu file RSS
        output_file = f"feeds/{page_config['rss_filename']}"
        fg.rss_file(output_file, pretty=True)
        print(f"✅ Đã lưu RSS feed: {output_file}")
        
        # Tạo file HTML preview đơn giản
        create_html_preview(page_config, posts)
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý {page_config['name']}: {e}")
        return False

def create_html_preview(page_config, posts):
    """Tạo file HTML để preview"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{page_config['name']} - Facebook RSS Preview</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .post {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 8px; }}
            .post img {{ max-width: 100%; height: auto; }}
            .time {{ color: #666; font-size: 0.9em; }}
            .stats {{ color: #1877f2; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>📰 {page_config['name']} - Facebook Updates</h1>
        <p>Preview của RSS Feed - Cập nhật lúc: {datetime.now(vietnam_tz).strftime('%H:%M %d/%m/%Y')}</p>
        <hr>
    """
    
    for post in posts[:5]:  # Chỉ hiển thị 5 bài đầu
        html_content += f"""
        <div class="post">
            <h3>📝 Bài viết</h3>
            <p>{post.get('post_text', '')[:300]}...</p>
        """
        
        if post.get('image'):
            html_content += f'<img src="{post["image"]}" alt="Hình ảnh">'
        
        if post.get('time'):
            post_time = post['time'].strftime('%H:%M %d/%m/%Y')
            html_content += f'<p class="time">⏰ {post_time}</p>'
        
        if post.get('likes'):
            html_content += f'<p class="stats">👍 {post["likes"]} lượt thích</p>'
        
        if post.get('post_url'):
            html_content += f'<p><a href="{post["post_url"]}" target="_blank">🔗 Xem trên Facebook</a></p>'
        
        html_content += '</div>'
    
    html_content += """
        <hr>
        <p>📡 RSS Feed: <a href="[TÊN_FILE_XML]">[TÊN_FILE_XML]</a></p>
        <p>🔄 Tự động cập nhật mỗi giờ</p>
    </body>
    </html>
    """
    
    # Thay thế tên file
    html_content = html_content.replace('[TÊN_FILE_XML]', page_config['rss_filename'])
    
    # Lưu file HTML
    html_file = f"previews/{page_config['rss_filename'].replace('.xml', '.html')}"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Đã tạo preview: {html_file}")

def main():
    """Hàm chính"""
    print("🚀 Bắt đầu tạo RSS feeds từ Facebook")
    print("=" * 50)
    
    # Tạo thư mục nếu chưa có
    os.makedirs("feeds", exist_ok=True)
    os.makedirs("previews", exist_ok=True)
    
    # Xử lý từng trang Facebook
    success_count = 0
    for page in config["facebook_pages"]:
        if create_rss_for_page(page):
            success_count += 1
    
    # Tạo trang index.html
    create_index_page(success_count, len(config["facebook_pages"]))
    
    print("=" * 50)
    print(f"✅ Hoàn thành! Đã xử lý {success_count}/{len(config['facebook_pages'])} trang")
    
    if success_count == 0:
        raise Exception("Không thể lấy dữ liệu từ bất kỳ trang nào!")

def create_index_page(success, total):
    """Tạo trang chủ hiển thị tất cả feeds"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📰 Facebook RSS Feeds</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #1877f2, #00a2ff); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }}
        .feed-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .feed-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .feed-card h3 {{ margin-top: 0; color: #1877f2; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #1877f2; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
        .btn:hover {{ background: #166fe5; }}
        .status {{ padding: 5px 10px; border-radius: 20px; font-size: 0.9em; }}
        .status-success {{ background: #d4edda; color: #155724; }}
        .footer {{ text-align: center; margin-top: 40px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📰 Facebook RSS Feeds</h1>
        <p>Tự động cập nhật bài viết từ Facebook</p>
        <p>🔄 Cập nhật lần cuối: {datetime.now(vietnam_tz).strftime('%H:%M %d/%m/%Y')}</p>
    </div>
    
    <div class="feed-list">
""")
        
        # Thêm từng feed
        for page in config["facebook_pages"]:
            f.write(f"""
        <div class="feed-card">
            <h3>{page['name']}</h3>
            <p>Username: @{page['username']}</p>
            <p>Số bài: {page['max_posts']} bài mới nhất</p>
            <div style="margin-top: 15px;">
                <a href="feeds/{page['rss_filename']}" class="btn">📡 RSS Feed</a>
                <a href="previews/{page['rss_filename'].replace('.xml', '.html')}" class="btn" style="background: #28a745;">👁 Preview</a>
            </div>
        </div>
""")
        
        f.write(f"""
    </div>
    
    <div class="footer">
        <p>📊 Trạng thái: <span class="status status-success">Đang hoạt động ({success}/{total} feeds)</span></p>
        <p>🔄 Tự động cập nhật mỗi {config['update_interval_hours']} giờ</p>
        <p>⚙️ Powered by GitHub Actions & Python</p>
    </div>
</body>
</html>
""")
    
    print("✅ Đã tạo trang chủ: index.html")

if __name__ == "__main__":
    main()
