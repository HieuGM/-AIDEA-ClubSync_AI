# ClubSync.AI - Hệ thống quản lý phòng họp S2B Community

Ứng dụng web quản lý phòng họp thông minh cho cộng đồng S2B gồm 3 CLB: Pro, Multi, GCC.

## Tính năng chính

- 🗓️ **Lịch trực quan**: Giao diện calendar giống Google Calendar
- 🏢 **Quản lý phòng**: 2 phòng (Lớn: 30 người, Nhỏ: 15 người)
- 👥 **Đa CLB**: Hỗ trợ 3 CLB với màu sắc phân biệt
- ⏰ **Quản lý thời gian**: Đánh dấu thời gian bận và thống kê
- 🔐 **Xác thực**: Đăng nhập/đăng ký bảo mật
- 📊 **Thống kê**: Dashboard với biểu đồ và báo cáo
- 🤖 **AI Agent**: Tự động tìm khung giờ họp tối ưu với AI

## 🤖 AI Agent - Tính năng mới!

ClubSync.AI tích hợp **AI Agent thông minh** để tự động tìm và đề xuất khung giờ họp tối ưu:

### ✨ Khả năng của Agent:
- 🧠 **Học thói quen** từ lịch sử booking của users
- 📊 **Ước lượng xác suất tham dự** dựa trên patterns
- 🎯 **Giải ràng buộc đa đối tượng** (thành viên bắt buộc, mentor, ưu tiên...)
- 🏆 **Tối ưu hóa** theo nhiều mục tiêu (đông người, công bằng, có mentor...)
- 🗳️ **Tạo poll "1 chạm"** với 3 khung giờ tốt nhất tự động

### 🚀 Quick Start với AI Agent:

```python
from app.ai.agent import create_agent

# Tạo agent
agent = create_agent()

# Tìm 3 slots tốt nhất
slots = agent.find_optimal_slots(
    duration_minutes=60,
    constraints={'min_attendees': 5},
    objective='balanced',
    top_n=3
)

# Tạo poll tự động
poll = agent.create_smart_poll(
    meeting_title="Team Meeting",
    duration_minutes=60
)
```

### 📡 API Endpoints cho AI:
- `POST /api/agent/suggest-slots` - Tìm slots tối ưu
- `POST /api/agent/create-poll` - Tạo poll tự động
- `GET /api/agent/user-patterns/<id>` - Xem patterns học được
- `POST /api/agent/attendance-probability` - Tính xác suất tham dự

**Chi tiết:** Xem `docs/AI_AGENT_QUICK_START.md` và `docs/AI_AGENT_DOCUMENTATION.md`

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

### AI Agent API
- `POST /api/agent/suggest-slots` - Tìm slots tối ưu với AI
- `POST /api/agent/create-poll` - Tạo poll tự động "1 chạm"
- `GET /api/agent/user-patterns/<id>` - Xem patterns học được
- `POST /api/agent/attendance-probability` - Tính xác suất tham dự
- `POST /api/agent/analyze-constraints` - Phân tích constraints
- `GET /api/agent/health` - Health check

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
- ✅ **AI Agent thông minh** (ĐÃ HOÀN THÀNH) - Tự động tìm khung giờ họp tối ưu
- ✅ **Học thói quen users** (ĐÃ HOÀN THÀNH) - Pattern learning từ lịch sử
- ✅ **Poll tự động** (ĐÃ HOÀN THÀNH) - Tạo poll "1 chạm" với 3 slots tốt nhất
- 🔮 Chatbot hỗ trợ người dùng
- 🔮 Dự đoán nhu cầu sử dụng phòng
- 🔮 Phân tích conflicts và đề xuất giải pháp

**Demo AI Agent:**
```bash
python demo_agent.py
```

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