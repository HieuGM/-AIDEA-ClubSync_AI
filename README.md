# ClubSync.AI - Hệ thống quản lý phòng họp S2B Community

Ứng dụng web quản lý phòng họp thông minh cho cộng đồng S2B gồm 3 CLB: Pro, Multi, GCC.

## Tính năng chính

- 🗓️ **Lịch trực quan**: Giao diện calendar giống Google Calendar
- 🏢 **Quản lý phòng**: 2 phòng (Lớn: 30 người, Nhỏ: 15 người)
- 👥 **Đa CLB**: Hỗ trợ 3 CLB với màu sắc phân biệt
- ⏰ **Quản lý thời gian**: Đánh dấu thời gian bận và thống kê
- 🔐 **Xác thực**: Đăng nhập/đăng ký bảo mật
- 📊 **Thống kê**: Dashboard với biểu đồ và báo cáo

## Công nghệ sử dụng

- **Backend**: Python Flask
- **Database**: SQLite với SQLAlchemy ORM
- **Frontend**: Bootstrap 5, FullCalendar.js, Chart.js
- **Authentication**: Flask-Login với bcrypt
- **Forms**: Flask-WTF

## Cài đặt và chạy

### 1. Clone repository
```bash
git clone <repository-url>
cd ClubSync.AI
```

### 2. Tạo virtual environment
```bash
python -m venv venv
```

### 3. Kích hoạt virtual environment
**Windows:**
```bash
venv\\Scripts\\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 5. Tạo file .env
```bash
copy .env.example .env
```
Chỉnh sửa file `.env` với thông tin cấu hình của bạn.

### 6. Chạy ứng dụng
```bash
python run.py
```

Ứng dụng sẽ chạy tại: http://localhost:5000

## Cấu trúc dự án

```
ClubSync.AI/
├── app/
│   ├── __init__.py          # Khởi tạo Flask app
│   ├── models.py            # Database models
│   ├── forms.py             # WTF Forms
│   ├── routes/              # Route blueprints
│   │   ├── auth.py          # Authentication routes
│   │   ├── main.py          # Main routes
│   │   ├── booking.py       # Booking management
│   │   └── api.py           # API endpoints
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── calendar.html
│   │   ├── dashboard.html
│   │   ├── availability.html
│   │   ├── auth/
│   │   └── booking/
│   └── static/              # Static files
│       ├── css/
│       └── js/
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## API Endpoints

### Authentication
- `POST /auth/login` - Đăng nhập
- `POST /auth/register` - Đăng ký
- `GET /auth/logout` - Đăng xuất

### Booking
- `GET /booking/create` - Form đặt phòng
- `POST /booking/create` - Tạo booking mới
- `GET /booking/my-bookings` - Lịch của user
- `GET /booking/cancel/<id>` - Hủy booking

### API
- `GET /api/events` - Lấy tất cả events
- `GET /api/my-events` - Events của user hiện tại
- `GET /api/rooms` - Danh sách phòng
- `GET /api/check-availability` - Kiểm tra phòng trống
- `GET/POST /api/availability` - Quản lý thời gian bận
- `GET /api/stats` - Thống kê

## Database Schema

### User
- `id`: Primary key
- `username`: Tên đăng nhập (unique)
- `email`: Email (unique)
- `password_hash`: Mật khẩu đã hash
- `club`: CLB (Pro/Multi/GCC)
- `is_admin`: Quyền admin
- `created_at`: Thời gian tạo

### Room
- `id`: Primary key
- `name`: Tên phòng
- `capacity`: Sức chứa
- `description`: Mô tả

### Booking
- `id`: Primary key
- `title`: Tiêu đề
- `description`: Mô tả
- `start_time`: Thời gian bắt đầu
- `end_time`: Thời gian kết thúc
- `user_id`: Foreign key đến User
- `room_id`: Foreign key đến Room
- `status`: Trạng thái (confirmed/cancelled/pending)

### UserAvailability
- `id`: Primary key
- `user_id`: Foreign key đến User
- `day_of_week`: Thứ trong tuần (0-6)
- `start_hour`: Giờ bắt đầu (0-23)
- `end_hour`: Giờ kết thúc (0-23)
- `is_busy`: Có bận không
- `recurring`: Lặp lại hàng tuần

## Tích hợp AI (Tương lai)

Ứng dụng được thiết kế sẵn để tích hợp AI với các tính năng:
- Gợi ý thời gian đặt phòng tối ưu
- Phân tích pattern sử dụng phòng
- Chatbot hỗ trợ người dùng
- Dự đoán nhu cầu sử dụng phòng

## Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Liên hệ

- **Email**: your-email@example.com
- **Project Link**: [https://github.com/your-username/ClubSync.AI](https://github.com/your-username/ClubSync.AI)

---

*Được phát triển cho S2B Community - Pro, Multi, GCC*