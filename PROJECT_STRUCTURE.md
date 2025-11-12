# 📚 ClubSync.AI - Tài liệu Cấu trúc Dự án

> **Hướng dẫn chi tiết về cấu trúc thư mục và chức năng từng file trong dự án**

---

## 📋 Mục lục

1. [Tổng quan](#-tổng-quan)
2. [Cấu trúc thư mục](#-cấu-trúc-thư-mục)
3. [Core Files (Root level)](#-core-files-root-level)
4. [App Module](#-app-module)
5. [Routes (API Endpoints)](#-routes-api-endpoints)
6. [AI Module](#-ai-module)
7. [Templates (UI)](#-templates-ui)
8. [Database Models](#-database-models)
9. [Configuration](#-configuration)

---

## 🎯 Tổng quan

**ClubSync.AI** là một ứng dụng web Flask quản lý phòng họp thông minh với AI Agent sử dụng **NVIDIA Llama 3.1** để tự động đề xuất khung giờ họp tối ưu.

### Tech Stack
- **Backend**: Python 3.8+ với Flask 2.3.3
- **Database**: SQLite + SQLAlchemy ORM
- **AI**: NVIDIA NIM API (Llama 3.1-8b-instruct)
- **Frontend**: Bootstrap 5, FullCalendar.js, Chart.js
- **Authentication**: Flask-Login + bcrypt

### Kiến trúc
- **MVC Pattern**: Model-View-Controller với Flask Blueprints
- **Factory Pattern**: `create_app()` factory function
- **ORM**: SQLAlchemy cho database abstraction
- **RESTful API**: JSON endpoints cho frontend communication

---

## 📁 Cấu trúc thư mục

```
ClubSync.AI/
├── 📄 run.py                    # Entry point - Khởi chạy Flask server
├── 📄 config.py                 # Configuration - API keys, database URL
├── 📄 requirements.txt          # Dependencies Python
├── 📄 .env                      # Environment variables (API keys)
├── 📄 .gitignore               # Git ignore rules
├── 📄 README.md                # Documentation chính
├── 📄 PROJECT_STRUCTURE.md     # Tài liệu này
│
├── 📂 app/                      # Main application package
│   ├── 📄 __init__.py          # Flask app factory
│   ├── 📄 models.py            # Database models (SQLAlchemy)
│   ├── 📄 forms.py             # WTForms (form validation)
│   │
│   ├── 📂 ai/                  # 🤖 AI Module
│   │   └── 📄 agent.py         # NVIDIA AI Agent - Core intelligence
│   │
│   ├── 📂 routes/              # Flask Blueprints (Controllers)
│   │   ├── 📄 main.py          # Main pages (home, dashboard, calendar)
│   │   ├── 📄 auth.py          # Authentication (login, register, logout)
│   │   ├── 📄 booking.py       # Booking management
│   │   ├── 📄 api.py           # REST API endpoints
│   │   └── 📄 agent_api.py     # AI Agent API endpoints
│   │
│   ├── 📂 templates/           # Jinja2 HTML templates
│   │   ├── 📄 base.html        # Base template layout
│   │   ├── 📄 index.html       # Homepage
│   │   ├── 📄 dashboard.html   # Dashboard với charts
│   │   ├── 📄 calendar.html    # Calendar view (FullCalendar.js)
│   │   ├── 📄 availability.html # Quản lý thời gian bận/rảnh
│   │   ├── 📄 smart_scheduler.html # 🤖 AI Smart Scheduler UI
│   │   ├── 📂 auth/
│   │   │   ├── 📄 login.html
│   │   │   └── 📄 register.html
│   │   └── 📂 booking/
│   │       ├── 📄 create.html  # Form tạo booking
│   │       └── 📄 my_bookings.html # Danh sách bookings của user
│   │
│   └── 📂 static/              # Static files (CSS, JS, images)
│       └── 📂 css/
│           └── 📄 style.css    # Custom CSS styles
│
├── 📂 instance/                # Instance folder (SQLite database)
├── 📂 docs/                    # Additional documentation
└── 📂 __pycache__/             # Python cache files (auto-generated)
```

---

## 📄 Core Files (Root level)

### `run.py` - Application Entry Point
```python
from app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**Chức năng:**
- Import factory function `create_app()`
- Khởi tạo Flask application
- Chạy development server trên port 5000
- Cho phép truy cập từ external (0.0.0.0)

**Cách sử dụng:**
```bash
python run.py
```

---

### `config.py` - Configuration Management
**Chức năng:**
- Load environment variables từ `.env`
- Định nghĩa class `Config` với các settings
- Cấu hình database URI (SQLite)
- NVIDIA API configuration (API key, model, temperature, max_tokens)

**Các biến quan trọng:**
```python
SECRET_KEY              # Flask secret key cho session
SQLALCHEMY_DATABASE_URI # Database connection string
AI_API_KEY             # NVIDIA API key
AI_MODEL               # Model name (meta/llama3-8b-instruct)
AI_TEMPERATURE         # AI creativity (0.0-1.0)
AI_MAX_TOKENS          # Max response length (4000)
```

**File `.env` example:**
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///clubsync.db
AI_API_KEY=nvapi-your-nvidia-key
AI_MODEL=meta/llama-3.1-8b-instruct
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=4000
```

---

### `requirements.txt` - Python Dependencies
**Danh sách packages:**
```
Flask==2.3.3              # Web framework
Flask-SQLAlchemy==3.0.5   # ORM
Flask-Login==0.6.3        # User session management
Flask-WTF==1.2.1          # Form handling
WTForms==3.1.0            # Form validation
Werkzeug==2.3.7           # WSGI utilities
bcrypt==4.0.1             # Password hashing
python-dotenv==1.0.0      # Environment variables
email_validator==2.3.0    # Email validation
openai>=1.30.0            # OpenAI SDK (used for NVIDIA API client)
gunicorn                  # Production WSGI server
```

**Cài đặt:**
```bash
pip install -r requirements.txt
```

---

## 🏗️ App Module

### `app/__init__.py` - Flask Application Factory

**Chức năng:**
1. **Factory Pattern**: Tạo Flask app instance
2. **Load Configuration**: Từ Config class
3. **Initialize Extensions**: Database, Flask-Login
4. **Register Blueprints**: Auth, Main, Booking, API, Agent API
5. **Create Database**: Auto-create tables và default rooms

**Blueprints registered:**
```python
/auth/*           → auth_bp (Authentication)
/*                → main_bp (Main pages)
/booking/*        → booking_bp (Booking management)
/api/*            → api_bp (REST API)
/api/agent/*      → agent_bp (AI Agent API)
```

**User Loader:**
```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

**Auto-create default rooms:**
- Phòng Lớn: 30 người
- Phòng Nhỏ: 15 người

---

### `app/models.py` - Database Models (SQLAlchemy ORM)

**4 Models chính:**

#### 1. **User** - Quản lý người dùng
```python
Columns:
- id (PK)
- username (unique)
- email (unique)
- password_hash (bcrypt)
- club (Pro/Multi/GCC)
- is_admin (boolean)
- created_at (datetime)

Relationships:
- bookings (One-to-Many với Booking)
- availability (One-to-Many với UserAvailability)

Methods:
- set_password(password)     # Hash password với bcrypt
- check_password(password)   # Verify password
```

#### 2. **Room** - Quản lý phòng họp
```python
Columns:
- id (PK)
- name
- capacity (số người)
- description
- created_at

Relationships:
- bookings (One-to-Many với Booking)
```

#### 3. **Booking** - Quản lý lịch đặt phòng
```python
Columns:
- id (PK)
- title
- description
- start_time (datetime)
- end_time (datetime)
- user_id (FK → User)
- room_id (FK → Room)
- status (confirmed/cancelled/pending)
- created_at

Methods:
- to_calendar_event()        # Convert sang format FullCalendar
- _get_color_by_club()       # Màu theo club (Pro=Red, Multi=Teal, GCC=Blue)
```

#### 4. **UserAvailability** - Quản lý thời gian bận/rảnh
```python
Columns:
- id (PK)
- user_id (FK → User)
- day_of_week (0=Monday, 6=Sunday)
- start_hour (0-23)
- end_hour (0-23)
- is_busy (True=bận, False=rảnh)
- recurring (True=lặp hàng tuần)
- created_at

Sử dụng:
- User đánh dấu thời gian bận
- AI Agent dùng data này để tránh đề xuất slot conflict
```

**Cascade Delete:**
- Xóa User → Xóa tất cả Bookings và Availability của user đó
- Xóa Room → Xóa tất cả Bookings của room đó

---

### `app/forms.py` - WTForms Validation

**3 Forms chính:**

#### 1. **LoginForm** - Form đăng nhập
```python
Fields:
- username (StringField, required)
- password (PasswordField, required)
- submit (SubmitField)
```

#### 2. **RegistrationForm** - Form đăng ký
```python
Fields:
- username (Length: 4-20, unique validation)
- email (Email validation, unique)
- club (SelectField: Pro/Multi/GCC)
- password (Length: min 6)
- password2 (EqualTo password)
- submit

Custom Validators:
- validate_username() # Check username đã tồn tại chưa
- validate_email()    # Check email đã được dùng chưa
```

#### 3. **BookingForm** - Form đặt phòng
```python
Fields:
- title (max 200 chars)
- description (TextAreaField)
- room_id (SelectField với coerce=int)
- start_time (DateTimeLocalField)
- end_time (DateTimeLocalField)
- submit

Custom Validators:
- validate_end_time() # Check end_time > start_time
```

---

## 🛣️ Routes (API Endpoints)

### `app/routes/main.py` - Main Pages

**5 Routes chính:**

#### 1. `GET /` - Homepage
```python
@bp.route('/')
def index():
```
- Trang chủ giới thiệu hệ thống
- Render: `index.html`

#### 2. `GET /dashboard` - Dashboard
```python
@bp.route('/dashboard')
@login_required
def dashboard():
```
- Trang tổng quan với thống kê
- Charts: Bookings by club, by room, by time
- Render: `dashboard.html`

#### 3. `GET /calendar` - Calendar View
```python
@bp.route('/calendar')
@login_required
def calendar():
```
- Lịch meetings dạng calendar (FullCalendar.js)
- Hiển thị tất cả bookings với màu theo club
- Render: `calendar.html`

#### 4. `GET /availability` - Availability Management
```python
@bp.route('/availability')
@login_required
def availability():
```
- Quản lý thời gian bận/rảnh
- User đánh dấu recurring busy slots
- Render: `availability.html`

#### 5. `GET /smart-scheduler` - 🤖 AI Smart Scheduler
```python
@bp.route('/smart-scheduler')
@login_required
def smart_scheduler():
```
- UI cho AI Agent tìm slots tối ưu
- Form nhập constraints (duration, min_attendees, etc.)
- Hiển thị results với AI reasoning
- Render: `smart_scheduler.html`

---

### `app/routes/auth.py` - Authentication

**3 Routes:**

#### 1. `GET/POST /auth/login` - Login
```python
@bp.route('/login', methods=['GET', 'POST'])
def login():
```
- Form đăng nhập
- Verify username + password với bcrypt
- Login user với Flask-Login
- Redirect về page trước đó hoặc dashboard

#### 2. `GET/POST /auth/register` - Register
```python
@bp.route('/register', methods=['GET', 'POST'])
def register():
```
- Form đăng ký user mới
- Validate username/email unique
- Hash password với bcrypt
- Tạo User mới trong database

#### 3. `GET /auth/logout` - Logout
```python
@bp.route('/logout')
@login_required
def logout():
```
- Logout user hiện tại
- Redirect về homepage

---

### `app/routes/booking.py` - Booking Management

**3 Routes:**

#### 1. `GET/POST /booking/create` - Create Booking
```python
@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
```
- Form tạo booking mới
- Nhận params `start` và `end` từ URL (từ AI Smart Scheduler)
- Auto-fill thời gian nếu có params
- Validate không conflict với bookings khác
- Tạo Booking record trong database

**Query params support:**
```
/booking/create?start=2025-11-13T14:00&end=2025-11-13T15:00
```

#### 2. `GET /booking/my-bookings` - My Bookings List
```python
@bp.route('/my-bookings')
@login_required
def my_bookings():
```
- Danh sách bookings của current user
- Hiển thị: title, room, thời gian, status
- Nút Cancel cho từng booking

#### 3. `GET /booking/cancel/<id>` - Cancel Booking
```python
@bp.route('/cancel/<int:booking_id>')
@login_required
def cancel(booking_id):
```
- Hủy booking (chỉ owner mới được cancel)
- Update status = 'cancelled'
- Redirect về my-bookings

---

### `app/routes/api.py` - REST API Endpoints

**6 Endpoints JSON:**

#### 1. `GET /api/events` - Get All Events
```python
@bp.route('/events')
@login_required
def get_events():
```
- Trả về tất cả bookings dạng FullCalendar format
- Response: JSON array of events

#### 2. `GET /api/my-events` - Get My Events
```python
@bp.route('/my-events')
@login_required
def get_my_events():
```
- Trả về bookings của current user only

#### 3. `GET /api/rooms` - Get Rooms
```python
@bp.route('/rooms')
@login_required
def get_rooms():
```
- Danh sách phòng họp
- Response: `[{id, name, capacity}, ...]`

#### 4. `GET /api/check-availability` - Check Room Availability
```python
@bp.route('/check-availability')
@login_required
def check_availability():
```
- Check phòng có trống không
- Params: `room_id`, `start_time`, `end_time`
- Response: `{available: true/false, conflicts: [...]}`

#### 5. `GET/POST /api/availability` - Manage User Availability
```python
@bp.route('/availability', methods=['GET', 'POST'])
@login_required
def availability():
```
- **GET**: Lấy availability của current user
- **POST**: Tạo/update availability slots
- Body: `{day_of_week, start_hour, end_hour, is_busy, recurring}`

#### 6. `GET /api/stats` - Get Statistics
```python
@bp.route('/stats')
@login_required
def stats():
```
- Thống kê cho dashboard
- Response:
```json
{
  "total_bookings": 150,
  "bookings_by_club": {"Pro": 50, "Multi": 60, "GCC": 40},
  "bookings_by_room": {"Phòng Lớn": 80, "Phòng Nhỏ": 70},
  "bookings_by_hour": {...}
}
```

---

### `app/routes/agent_api.py` - 🤖 AI Agent API

**6 Endpoints AI-powered:**

#### 1. `POST /api/agent/suggest-slots` - Tìm Slots Tối Ưu ⭐
```python
@bp.route('/suggest-slots', methods=['POST'])
@login_required
def suggest_slots():
```

**Chức năng chính:**
- Sử dụng AI Agent để tìm Top 3 khung giờ tối ưu
- GPT phân tích và chấm điểm từng slot
- Trả về slots với AI reasoning chi tiết

**Request Body:**
```json
{
  "duration_minutes": 60,
  "constraints": {
    "min_attendees": 5,
    "required_members": [1, 2, 3],
    "required_mentors": [10],
    "time_constraints": {
      "earliest_hour": 9,
      "latest_hour": 18,
      "preferred_days": [1, 2, 3]
    }
  },
  "objective": "balanced",
  "days_ahead": 14,
  "top_n": 3
}
```

**Response:**
```json
{
  "success": true,
  "slots": [
    {
      "start_time": "2025-11-13T14:00:00",
      "end_time": "2025-11-13T15:00:00",
      "start_time_str": "2025-11-13 14:00",
      "day_name": "Thứ 4",
      "score": 87.5,
      "available_count": 12,
      "expected_attendance": 9.6,
      "avg_attendance_rate": 80,
      "mentor_count": 2,
      "ai_reasoning": "Có 12 người rảnh bao gồm 2 mentor. Thứ 4 buổi chiều có tỷ lệ tham dự cao trong lịch sử. Đây là khung giờ lý tưởng cho team meeting.",
      "user_details": [...]
    }
  ],
  "total_users": 20,
  "analysis_time": 3.5
}
```

**Objectives:**
- `balanced`: Cân bằng nhiều yếu tố (recommended)
- `max_attendance`: Tối đa người tham dự
- `mentor_priority`: Ưu tiên có mentor
- `fairness`: Công bằng giữa các thành viên

#### 2. `POST /api/agent/busy-users` - Xem Ai Bận 🆕
```python
@bp.route('/busy-users', methods=['POST'])
@login_required
def busy_users():
```

**Chức năng:**
- Chi tiết ai rảnh/bận cho 1 slot cụ thể
- Hiển thị lý do bận (đã đánh dấu busy, định kỳ...)

**Request:**
```json
{
  "slot_datetime": "2025-11-13T14:00:00",
  "duration_minutes": 60
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "slot_start": "2025-11-13 14:00",
    "slot_end": "15:00",
    "total_users": 20,
    "available_count": 12,
    "busy_count": 8,
    "available_users": [
      {
        "id": 1,
        "username": "john_doe",
        "club": "Pro",
        "is_mentor": true,
        "attendance_rate": 0.85
      }
    ],
    "busy_users": [
      {
        "id": 5,
        "username": "jane_smith",
        "club": "Multi",
        "is_mentor": false,
        "reason": "Đã đánh dấu bận 14:00-17:00 (định kỳ)"
      }
    ]
  }
}
```

#### 3. `GET /api/agent/user-patterns/<user_id>` - User Patterns
```python
@bp.route('/user-patterns/<int:user_id>', methods=['GET'])
@login_required
def user_patterns(user_id):
```

**Chức năng:**
- Xem patterns học được từ lịch sử booking của user
- Thời gian ưa thích, ngày trong tuần, attendance rate

**Response:**
```json
{
  "user_id": 1,
  "username": "john_doe",
  "total_bookings": 25,
  "avg_attendance_rate": 0.85,
  "preferred_hours": [14, 15, 16],
  "preferred_days": [1, 2, 3],
  "mentor_presence_boost": 1.2
}
```

#### 4. `POST /api/agent/attendance-probability` - Attendance Prediction
```python
@bp.route('/attendance-probability', methods=['POST'])
@login_required
def attendance_probability():
```

**Chức năng:**
- Dự đoán xác suất tham dự của users cho 1 slot

**Request:**
```json
{
  "user_ids": [1, 2, 3, 4, 5],
  "slot_datetime": "2025-11-13T14:00:00"
}
```

**Response:**
```json
{
  "slot": "2025-11-13 14:00",
  "predictions": [
    {
      "user_id": 1,
      "username": "john_doe",
      "probability": 0.85,
      "factors": {
        "historical_rate": 0.80,
        "time_preference": 0.90,
        "mentor_present": true
      }
    }
  ],
  "expected_attendance": 4.2
}
```

#### 5. `POST /api/agent/analyze-constraints` - Analyze Constraints
```python
@bp.route('/analyze-constraints', methods=['POST'])
@login_required
def analyze_constraints():
```

**Chức năng:**
- Phân tích constraints có khả thi không
- Kiểm tra trước khi chạy find_optimal_slots

**Request:**
```json
{
  "constraints": {
    "min_attendees": 15,
    "required_members": [1, 2, 3, 4, 5]
  },
  "days_ahead": 14
}
```

**Response:**
```json
{
  "feasible": true,
  "warnings": [
    "Min attendees 15 có thể khó đạt được vào cuối tuần"
  ],
  "suggestions": [
    "Giảm min_attendees xuống 10 để tăng khả năng tìm thấy slot"
  ]
}
```

#### 6. `GET /api/agent/health` - Health Check
```python
@bp.route('/health', methods=['GET'])
def health():
```

**Chức năng:**
- Check AI Agent có hoạt động không
- Test connection đến NVIDIA API

**Response:**
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "model": "meta/llama3-8b-instruct",
  "api_key_configured": true
}
```

---

## 🤖 AI Module

### `app/ai/agent.py` - NVIDIA AI Agent

**Class: `MeetingSchedulerAgent`**

Đây là **trái tim của hệ thống AI** - Agent thông minh sử dụng NVIDIA Llama 3.1 để tìm slots tối ưu.

---

#### **Khởi tạo:**
```python
def __init__(self, db_session, api_key=None, model=None):
    self.db = db_session
    self.api_key = api_key or Config.AI_API_KEY
    self.model = model or Config.AI_MODEL
    
    # Initialize NVIDIA client
    self.client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=self.api_key
    )
```

---

#### **17 Methods chính:**

### 1. Data Collection (3 methods)

#### `get_all_user_availability()` → List[UserAvailability]
- Lấy lịch bận của TẤT CẢ users
- Query từ bảng UserAvailability

#### `get_all_users(club_filter=None)` → List[User]
- Lấy danh sách users
- Filter theo club nếu cần

#### `get_booking_history(days_back=90)` → List[Booking]
- Lấy lịch sử bookings
- Mặc định 90 ngày gần nhất
- Dùng để học patterns

---

### 2. Data Analysis (2 methods)

#### `analyze_user_history(user_id)` → Dict
Phân tích lịch sử booking của 1 user:
```python
{
  "total_bookings": 25,
  "attendance_rate": 0.85,
  "preferred_hours": [14, 15, 16],
  "preferred_days": [1, 2, 3],  # Monday, Tuesday, Wednesday
  "avg_duration_minutes": 60
}
```

#### `build_availability_grid(availabilities, days_ahead=14)` → Dict
Build lưới thời gian rảnh của tất cả users:
```python
{
  "2025-11-13 14:00": {
    "available_users": [1, 2, 3, 5, 10],
    "busy_users": [4, 6, 7],
    "mentor_count": 2
  }
}
```

---

### 3. AI-Powered Core (1 method) ⭐⭐⭐

#### `ask_gpt_to_analyze_slots(candidate_slots, constraints, objective)` → List[Dict]

**🚀 CORE FEATURE - GPT ANALYSIS**

Đây là method quan trọng nhất, sử dụng NVIDIA Llama 3.1 để:
1. Nhận danh sách candidate slots (đã lọc qua constraints)
2. Gửi context đầy đủ cho GPT
3. GPT phân tích và chấm điểm từng slot
4. Trả về slots với AI reasoning chi tiết

**Prompt structure:**
```
System: Bạn là AI Meeting Scheduler expert...
User: [Context về users, constraints, slots]
      Analyze và chấm điểm từng slot theo objective: {objective}
      Return JSON với ai_score (0-100) và ai_reasoning
```

**GPT phân tích dựa trên:**
- Số người available
- Mentor presence
- Time preferences từ lịch sử
- Day of week patterns
- Attendance probability
- Fairness distribution

**Output:**
```json
{
  "slots": [
    {
      "slot_index": 0,
      "ai_score": 85,
      "ai_reasoning": "Thứ 4 14:00 có 12 người rảnh bao gồm 2 mentor..."
    }
  ]
}
```

---

### 4. Constraint Checking (1 method)

#### `check_constraints(slot_datetime, duration, available_users, constraints)` → Dict

Kiểm tra slot có thỏa constraints không:
```python
{
  "valid": True,
  "reasons": [],
  "required_members_present": [1, 2, 3],
  "required_mentors_present": [10]
}
```

**Constraints check:**
- `min_attendees`: Số người tối thiểu
- `required_members`: Danh sách user_id bắt buộc
- `required_mentors`: Danh sách mentor_id bắt buộc
- `time_constraints`: earliest_hour, latest_hour, preferred_days

---

### 5. Scoring (1 method)

#### `score_slot(slot_datetime, duration, available_users, constraints, objective)` → float

Chấm điểm slot dựa trên:
1. **Attendance count**: Số người tham dự (weight: 3.0)
2. **Attendance probability**: Xác suất tham dự cao (weight: 2.5)
3. **Fairness**: Công bằng giữa users (weight: 2.0)
4. **Mentor present**: Có mentor không (weight: 2.5)
5. **Required members**: Thành viên bắt buộc (weight: 5.0)
6. **Time preference**: Khung giờ ưa thích (weight: 1.5)
7. **Recency**: Gần với hiện tại (weight: 1.0)
8. **Day preference**: Ngày trong tuần phù hợp (weight: 1.2)

**Objective adjusts weights:**
- `max_attendance`: x2 weight cho attendance_count
- `mentor_priority`: x2 weight cho mentor_present
- `fairness`: x2 weight cho fairness

---

### 6. Main Algorithm (1 method) ⭐⭐⭐

#### `find_optimal_slots(duration_minutes, constraints, objective, days_ahead, top_n)` → List[Dict]

**🎯 MAIN ALGORITHM - Tìm slots tối ưu**

**Pipeline:**
```
1. Load data
   ├─ Get all users
   ├─ Get all availability
   └─ Get booking history

2. Build availability grid
   └─ Matrix thời gian rảnh của tất cả users

3. Generate candidate slots
   ├─ Scan từng giờ trong days_ahead
   ├─ Check continuous availability
   └─ Filter: Chỉ slots ≥ 2 giờ từ hiện tại

4. Check constraints
   └─ Filter slots thỏa min_attendees, required_members, etc.

5. Score slots
   └─ Chấm điểm dựa trên objective

6. 🤖 Ask GPT to analyze
   ├─ Lấy top 20 slots theo score
   ├─ Gửi cho GPT phân tích
   └─ GPT trả về ai_score và ai_reasoning

7. Combine scores
   └─ Final score = (rule_based_score + ai_score) / 2

8. Sort & Return top N
   └─ Enrich với user details, attendance rate, etc.
```

**Key features:**
- ⏰ Time validation: Chỉ đề xuất slots sau ≥ 2 giờ
- 🧠 GPT analysis: Tối đa 20 slots để tránh truncation
- 🎯 Multi-objective: 4 chế độ tối ưu
- 📊 Rich data: Trả về đầy đủ thông tin cho UI

---

### 7. Helper Methods (8 methods)

#### `_is_continuous_slot(grid, start_time, end_time)` → bool
Check slot có liên tục không (không có break giữa chừng)

#### `_get_available_users_for_slot(grid, start_time, end_time)` → Set[int]
Lấy danh sách user_id available cho slot

#### `_enrich_slot_info(slots)` → List[Dict]
Thêm thông tin chi tiết vào slots:
- User details (username, club, is_mentor)
- Attendance rate từ lịch sử
- Day name (Thứ 2, Thứ 3, ...)

#### `get_busy_users_for_slot(slot_datetime, duration)` → Dict
Xem chi tiết ai rảnh/bận cho slot:
```python
{
  "available_users": [...],
  "busy_users": [
    {
      "id": 5,
      "username": "jane",
      "club": "Multi",
      "reason": "Đã đánh dấu bận 14:00-17:00 (định kỳ)"
    }
  ]
}
```

#### `_get_busy_reason(user_id, start_time, end_time)` → str
Tìm lý do user bận (từ UserAvailability)

#### Other helpers:
- `_calculate_attendance_probability()`
- `_calculate_fairness_score()`
- `_is_time_in_preferences()`

---

### 8. Factory Function

#### `create_agent(db_session, api_key, model)` → MeetingSchedulerAgent
Convenience function để tạo agent:
```python
from app.ai.agent import create_agent
agent = create_agent()
slots = agent.find_optimal_slots(...)
```

---

#### **Workflow tổng quát:**

```
User request
    ↓
Frontend (smart_scheduler.html)
    ↓ POST /api/agent/suggest-slots
agent_api.py
    ↓ create_agent()
MeetingSchedulerAgent
    ↓ find_optimal_slots()
    ├─ 1. Load data (users, availability, history)
    ├─ 2. Build grid (thời gian rảnh)
    ├─ 3. Generate candidates (scan khung giờ)
    ├─ 4. Check constraints (filter)
    ├─ 5. Score slots (rule-based)
    ├─ 6. 🤖 Ask GPT (AI analysis)
    ├─ 7. Combine scores
    └─ 8. Return top N slots
    ↓
Response JSON
    ↓
Frontend hiển thị results
```

---

## 🎨 Templates (UI)

### Jinja2 Template Structure

**Base Template:** `base.html`
- Navigation bar với login/logout
- Bootstrap 5 layout
- Flash messages
- Blocks: title, content

**Template inheritance:**
```
base.html (parent)
  ├─ index.html
  ├─ dashboard.html
  ├─ calendar.html
  ├─ availability.html
  ├─ smart_scheduler.html
  ├─ auth/login.html
  ├─ auth/register.html
  ├─ booking/create.html
  └─ booking/my_bookings.html
```

---

### `smart_scheduler.html` - 🤖 AI Smart Scheduler UI

**Layout:**

#### 1. Form tìm kiếm slots
```html
<form id="slotFinderForm">
  <input name="duration" value="60">
  <input name="min_attendees" value="5">
  <input name="days_ahead" value="14">
  <select name="objective">
    <option value="balanced">Cân bằng</option>
    <option value="max_attendance">Nhiều người nhất</option>
    <option value="mentor_priority">Ưu tiên mentor</option>
    <option value="fairness">Công bằng</option>
  </select>
</form>
```

#### 2. Results display
```html
<div id="resultsContainer">
  <!-- For each slot -->
  <div class="slot-card">
    <h5>Thứ 4, 13/11/2025 - 14:00-15:00</h5>
    <p>Điểm: 87.5/100</p>
    <p>12 người rảnh, 2 mentors</p>
    <p><strong>AI:</strong> Thứ 4 buổi chiều có tỷ lệ tham dự cao...</p>
    
    <button onclick="useThisSlot(...)">Chọn slot này</button>
    <button onclick="showBusyUsers(...)">Xem ai bận</button>
  </div>
</div>
```

#### 3. Busy Users Modal 🆕
```html
<div class="modal" id="busyUsersModal">
  <ul class="nav nav-tabs">
    <li>Rảnh (12)</li>
    <li>Bận (8)</li>
  </ul>
  
  <div class="tab-content">
    <!-- Available users -->
    <div class="tab-pane active" id="availableTab">
      <ul>
        <li>john_doe (Pro) - 85% attendance</li>
      </ul>
    </div>
    
    <!-- Busy users with reasons -->
    <div class="tab-pane" id="busyTab">
      <ul>
        <li>jane_smith (Multi) - Đã đánh dấu bận 14:00-17:00 (định kỳ)</li>
      </ul>
    </div>
  </div>
</div>
```

#### 4. JavaScript functions
```javascript
function findOptimalSlots() {
  // POST /api/agent/suggest-slots
  // Display results
}

function useThisSlot(start, end) {
  // Redirect to /booking/create?start=...&end=...
  window.location.href = `/booking/create?start=${start}&end=${end}`;
}

function showBusyUsers(slot_datetime, duration) {
  // POST /api/agent/busy-users
  // Show modal with available/busy users
}
```

---

### `booking/create.html` - Booking Form

**Features:**
- Auto-fill thời gian từ URL params (từ Smart Scheduler)
- Room selection dropdown
- DateTimeLocal inputs cho start/end time
- Form validation

**JavaScript auto-fill:**
```javascript
window.addEventListener('DOMContentLoaded', function() {
  const urlParams = new URLSearchParams(window.location.search);
  const start = urlParams.get('start');
  const end = urlParams.get('end');
  
  if (start) {
    document.getElementById('start_time').value = start;
  }
  if (end) {
    document.getElementById('end_time').value = end;
  }
});
```

---

### `calendar.html` - FullCalendar View

**Features:**
- FullCalendar.js integration
- Fetch events từ `/api/events`
- Color-coded by club (Pro=Red, Multi=Teal, GCC=Blue)
- Click event để xem details
- Drag & drop (nếu implement)

**FullCalendar config:**
```javascript
var calendar = new FullCalendar.Calendar(calendarEl, {
  initialView: 'timeGridWeek',
  events: '/api/events',
  eventClick: function(info) {
    // Show event details
  }
});
```

---

### `dashboard.html` - Dashboard với Charts

**Features:**
- Chart.js charts:
  - Bookings by club (Pie chart)
  - Bookings by room (Bar chart)
  - Bookings by hour (Line chart)
- Statistics cards: Total bookings, Most popular room, etc.

**Data fetch:**
```javascript
fetch('/api/stats')
  .then(response => response.json())
  .then(data => {
    // Render charts với Chart.js
  });
```

---

## 🗄️ Database Models (Chi tiết)

### Relationships Diagram

```
User (1) ──────< (M) Booking (M) >────── (1) Room
 │
 └──────< (M) UserAvailability
```

### Cascade Deletes
- User deleted → Cascade delete Bookings và UserAvailability
- Room deleted → Cascade delete Bookings

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Flask
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///clubsync.db

# NVIDIA AI
AI_API_KEY=nvapi-your-nvidia-api-key
AI_MODEL=meta/llama-3.1-8b-instruct
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=4000
```

### Config Class (config.py)

**Loaded by:**
```python
from config import Config
app.config.from_object(Config)
```

**Available configs:**
- `SECRET_KEY`: Flask secret key
- `SQLALCHEMY_DATABASE_URI`: Database connection
- `AI_API_KEY`: NVIDIA API key
- `AI_MODEL`: Model name
- `AI_TEMPERATURE`: AI creativity (0.0-1.0)
- `AI_MAX_TOKENS`: Max AI response length

---

## 🚀 Deployment Flow

### Development
```bash
1. Clone repo
2. Create venv: python -m venv venv
3. Activate: venv\Scripts\activate
4. Install: pip install -r requirements.txt
5. Configure: Create .env với AI_API_KEY
6. Run: python run.py
7. Access: http://localhost:5000
```

### Production (Example: Render.com)
```bash
1. Push to GitHub
2. Connect Render to GitHub repo
3. Set environment variables in Render dashboard
4. Render auto-detects requirements.txt
5. Render runs: pip install -r requirements.txt
6. Render runs: gunicorn run:app
```

**Important:**
- Use `gunicorn` for production (already in requirements.txt)
- Set `SECRET_KEY` securely
- Configure `AI_API_KEY` in Render environment variables

---

## 📊 Data Flow Summary

### User creates booking manually:
```
User fills form
  → POST /booking/create
  → Validate form
  → Create Booking in DB
  → Redirect to calendar
```

### User uses AI Smart Scheduler:
```
User fills constraints
  → POST /api/agent/suggest-slots
  → create_agent()
  → find_optimal_slots()
    ├─ Load data (users, availability, history)
    ├─ Build grid
    ├─ Generate candidates
    ├─ Check constraints
    ├─ Score slots
    ├─ 🤖 Ask GPT
    └─ Return top 3 slots
  → Display results with AI reasoning
  → User clicks "Chọn slot này"
  → Redirect to /booking/create?start=...&end=...
  → Auto-fill form
  → User submits
  → Create Booking in DB
```

### User views calendar:
```
User accesses /calendar
  → Render calendar.html
  → FullCalendar fetches /api/events
  → Query all Bookings from DB
  → Convert to calendar format
  → Return JSON
  → Display on calendar
```

---

## 🔒 Security

### Authentication
- Flask-Login session management
- bcrypt password hashing
- `@login_required` decorator cho protected routes

### CSRF Protection
- Flask-WTF CSRF tokens
- All forms protected

### SQL Injection Prevention
- SQLAlchemy ORM (parameterized queries)
- No raw SQL queries

---

## 🧪 Testing

### Test Files (if created)
- `test_agent.py`: Test AI Agent functions
- `test_openai.py`: Test NVIDIA API connection
- `quick_test.py`: Quick sanity checks
- `demo_agent.py`: Demo AI Agent capabilities

---

## 📈 Performance Considerations

### AI Agent Optimization
- **Max slots analyzed by GPT**: 20 (để tránh token limit)
- **Max tokens**: 4000 (cấu hình trong .env)
- **Temperature**: 0.7 (balance creativity vs accuracy)

### Database
- SQLite for development (simple, file-based)
- Can migrate to PostgreSQL for production (update DATABASE_URL)

### Caching
- Consider caching AI results (Redis)
- Cache user patterns
- Cache availability grid

---

## 🛠️ Future Enhancements

### Planned Features (from README Roadmap)

**Version 2.1:**
- Chatbot tương tác bằng ngôn ngữ tự nhiên
- Email/SMS notifications
- Export calendar (iCal, Google Calendar)
- Advanced analytics dashboard

**Long-term:**
- Mobile app (React Native)
- Video conferencing integration (Zoom, Meet)
- Multi-language support
- AI-powered conflict resolution
- Resource optimization (rooms, equipment)

---

## 📞 Support & Contact

**GitHub**: [github.com/HieuGM/-AIDEA-ClubSync_AI](https://github.com/HieuGM/-AIDEA-ClubSync_AI)

**Developed for S2B Community** 💙 (Pro 🔴 | Multi 🔵 | GCC 🟢)

*Powered by NVIDIA Llama 3.1* 🤖

---

## 📝 Changelog

### Version 2.0.0 (Current)
- ✅ NVIDIA Llama 3.1 AI Agent
- ✅ Smart slot finding với GPT reasoning
- ✅ Busy users detection
- ✅ Pattern learning & attendance prediction
- ✅ Multi-objective optimization
- ✅ Auto-fill booking form từ AI suggestions
- ✅ Time validation (≥ 2 giờ từ hiện tại)

### Version 1.0.0
- Basic booking system
- Calendar view
- User authentication
- Multi-club support
- Availability management

---

**End of Documentation** 📚
