# 🤖 ClubSync.AI - AI Meeting Scheduler

> Hệ thống quản lý phòng họp thông minh với **NVIDIA AI** cho cộng đồng S2B (Pro, Multi, GCC)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![NVIDIA](https://img.shields.io/badge/NVIDIA-Llama--3.1-76B900.svg)](https://www.nvidia.com)

Ứng dụng web quản lý phòng họp với **NVIDIA Llama 3.1** để phân tích và đề xuất khung giờ họp tối ưu dựa trên lịch sử, thói quen người dùng và các ràng buộc phức tạp.

---

## 🚀 Tech Stack

### Backend
- **Python 3.8+** với Flask 2.3.3
- **SQLAlchemy ORM** + SQLite
- **Flask-Login** + bcrypt (Authentication)
- **Flask-WTF** + WTForms (Form validation)

### AI/ML
- **NVIDIA NIM** - Llama 3.1-8b-instruct
- **OpenAI SDK** 1.12.0 (client library)

### Frontend
- **Bootstrap 5** (UI Framework)
- **FullCalendar.js** (Calendar view)
- **Chart.js** (Statistics)

---

## ✨ Tính năng chính

### 📅 Core Features
- **Quản lý phòng họp**: 2 phòng với capacity khác nhau
- **Calendar trực quan**: Xem lịch meeting theo tuần/tháng
- **Multi-club**: Hỗ trợ 3 CLB (Pro, Multi, GCC)
- **Availability**: Đánh dấu thời gian bận/rảnh
- **Dashboard**: Thống kê booking và attendance

### 🤖 AI Smart Scheduler (NVIDIA Llama 3.1)
1. **Tìm slots tối ưu**: AI phân tích và đề xuất Top 3 khung giờ tốt nhất
2. **Pattern Learning**: Học thói quen từ lịch sử booking
3. **Attendance Prediction**: Dự đoán xác suất tham dự
4. **Constraint Solving**: Xử lý ràng buộc phức tạp (members, mentors, time)
5. **Multi-objective**: 4 chế độ tối ưu (balanced, max_attendance, mentor_priority, fairness)
6. **Busy Detection**: Xem chi tiết ai rảnh/bận cho từng slot với lý do cụ thể
7. **Time Validation**: Chỉ đề xuất slots ≥ 2 giờ từ hiện tại

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/HieuGM/-AIDEA-ClubSync_AI.git
cd -AIDEA-ClubSync_AI
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Cấu hình NVIDIA API (.env)
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///clubsync.db

AI_API_KEY=nvapi-your-nvidia-key
AI_MODEL=meta/llama-3.1-8b-instruct
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=4000
```

### 3. Khởi tạo Database
```bash
python
>>> from app import create_app
>>> from app.models import db, Room
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
...     room1 = Room(name='Phòng Lớn', capacity=30)
...     room2 = Room(name='Phòng Nhỏ', capacity=15)
...     db.session.add_all([room1, room2])
...     db.session.commit()
```

### 4. Run
```bash
python run.py
```
→ **http://localhost:5000**

---

## 📁 Cấu trúc Project

```
ClubSync.AI/
├── app/
│   ├── ai/
│   │   └── agent.py              # NVIDIA Llama AI Agent
│   ├── routes/
│   │   ├── main.py               # Home, Dashboard, Calendar
│   │   ├── auth.py               # Login, Register
│   │   ├── booking.py            # Create, Cancel bookings
│   │   ├── api.py                # REST API (events, rooms, stats)
│   │   └── agent_api.py          # AI endpoints (suggest-slots, busy-users)
│   ├── templates/
│   │   ├── smart_scheduler.html  # AI Smart Scheduler UI
│   │   ├── calendar.html
│   │   ├── dashboard.html
│   │   └── auth/, booking/
│   ├── static/css/
│   ├── models.py                 # User, Room, Booking, UserAvailability
│   └── __init__.py
├── config.py                     # NVIDIA API config
├── run.py
├── requirements.txt
└── clubsync.db
```

---

## � Database Schema

### User
- `id`, `username`, `email`, `password_hash`
- `club` (Pro/Multi/GCC)
- `is_admin`, `created_at`

### Room
- `id`, `name`, `capacity`, `description`

### Booking
- `id`, `title`, `description`
- `start_time`, `end_time`
- `user_id` (FK), `room_id` (FK)
- `status` (confirmed/cancelled/pending)

### UserAvailability
- `user_id` (FK), `day_of_week` (0-6)
- `start_hour`, `end_hour`
- `is_busy`, `recurring`

---

## � Roadmap & Future Plans

### ✅ Version 2.0 (Current)
- NVIDIA Llama 3.1 AI Agent
- Smart slot finding với reasoning
- Busy users detection
- Pattern learning & attendance prediction
- Multi-objective optimization

### 🚧 Version 2.1 (Planning)
- [ ] Chatbot tương tác bằng ngôn ngữ tự nhiên
- [ ] Email/SMS notifications
- [ ] Export calendar (iCal, Google Calendar)
- [ ] Advanced analytics dashboard

### 🔮 Future (Long-term)
- [ ] Mobile app (React Native)
- [ ] Video conferencing integration (Zoom, Meet)
- [ ] Multi-language support
- [ ] AI-powered conflict resolution
- [ ] Resource optimization (rooms, equipment)

---

## 📧 Contact

**Project**: [github.com/HieuGM/-AIDEA-ClubSync_AI](https://github.com/HieuGM/-AIDEA-ClubSync_AI)

**Developed for S2B Community** 💙 (Pro 🔴 | Multi 🔵 | GCC 🟢)

*Powered by NVIDIA Llama 3.1* 🤖
