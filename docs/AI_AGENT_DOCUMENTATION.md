# AI Agent Documentation - ClubSync.AI

## 📋 Tổng quan

**MeetingSchedulerAgent** là một AI Agent thông minh được thiết kế để tự động tìm kiếm và đề xuất khung giờ họp tối ưu cho ClubSync.AI. Agent này không chỉ đơn thuần tìm "ai rảnh" mà còn:

- 🧠 **Học thói quen** từ lịch sử booking
- 📊 **Ước lượng xác suất** tham dự của từng user
- 🎯 **Giải ràng buộc đa đối tượng** (thành viên bắt buộc, mentor, ưu tiên...)
- 🏆 **Tối ưu hóa** theo nhiều mục tiêu khác nhau
- 🗳️ **Tạo poll tự động** với 3 khung giờ tốt nhất

## 🎯 Các chức năng chính

### 1. Lấy lịch bận từ tất cả người dùng

```python
agent = create_agent()
availabilities = agent.get_all_user_availability()
```

- Lấy toàn bộ `UserAvailability` từ database
- Xây dựng lưới thời gian chi tiết theo ngày và giờ
- Tính toán users available cho từng time slot

### 2. Học thói quen và ước lượng xác suất

```python
# Học pattern của user
pattern = agent.learn_user_patterns(user_id)

# Ước lượng xác suất tham dự tại slot cụ thể
probability = agent.estimate_attendance_probability(user_id, slot_datetime)

# Tính kỳ vọng số người tham dự
attendance_data = agent.calculate_expected_attendance(user_ids, slot_datetime)
```

**Các yếu tố được học:**
- ⏰ Khung giờ ưa thích (morning/afternoon/evening)
- 📅 Ngày trong tuần thường tham gia
- ✅ Tỷ lệ tham dự (attendance rate)
- 📈 Xác suất theo từng giờ và ngày

### 3. Giải ràng buộc đa đối tượng

Agent hỗ trợ nhiều loại constraints phức tạp:

```python
constraints = {
    # Thành viên bắt buộc phải có mặt
    'required_members': [1, 2, 3],
    
    # Mentor bắt buộc (users có role admin/mentor)
    'required_mentors': [4, 5],
    
    # Số người tối thiểu và tối đa
    'min_attendees': 5,
    'max_attendees': 15,
    
    # Ưu tiên thành viên cụ thể
    'preferred_members': [6, 7],
    
    # Filter theo club
    'club_filter': 'Pro',  # hoặc 'Multi', 'GCC'
    
    # Giới hạn khung giờ
    'time_constraints': {
        'earliest_hour': 9,   # Không sớm hơn 9h
        'latest_hour': 18     # Không muộn hơn 18h
    }
}
```

### 4. Tạo poll "1 chạm"

```python
poll = agent.create_smart_poll(
    meeting_title="Weekly Team Sync",
    duration_minutes=60,
    constraints=constraints,
    objectives=['max_attendance', 'balanced', 'mentor_priority']
)
```

Poll tự động sẽ đề xuất **3 khung giờ tốt nhất** theo 3 mục tiêu khác nhau:
1. **max_attendance**: Tối đa số người tham dự
2. **balanced**: Cân bằng nhiều yếu tố
3. **mentor_priority**: Ưu tiên có mentor

### 5. Tối ưu hóa theo mục tiêu

Agent hỗ trợ nhiều objectives khác nhau:

| Objective | Mô tả | Use case |
|-----------|-------|----------|
| `max_attendance` | Tối đa số người tham dự | Meeting quan trọng cần nhiều người |
| `max_probability` | Tối đa xác suất tham dự | Cần đảm bảo attendance cao |
| `fairness` | Công bằng giữa các thành viên | Tránh thiên vị một nhóm |
| `mentor_priority` | Ưu tiên có mentor | Training, workshop |
| `balanced` | Cân bằng tất cả yếu tố | Default, phù hợp hầu hết trường hợp |

## 🔧 Sử dụng Agent

### Cách 1: Sử dụng trực tiếp trong Python

```python
from app.ai.agent import create_agent
from app.models import db

# Tạo agent instance
agent = create_agent(db.session)

# Tìm top 3 slots tốt nhất
slots = agent.find_optimal_slots(
    duration_minutes=60,
    constraints={
        'required_members': [1, 2],
        'min_attendees': 5
    },
    objective='balanced',
    days_ahead=14,
    top_n=3
)

# Xem kết quả
for slot in slots:
    print(f"Time: {slot['start_time_str']}")
    print(f"Score: {slot['score_rounded']}")
    print(f"Expected attendance: {slot['expected_attendance_rounded']}")
```

### Cách 2: Sử dụng qua API

#### POST /api/agent/suggest-slots

Tìm slots tối ưu với constraints.

**Request:**
```json
{
    "duration_minutes": 60,
    "constraints": {
        "required_members": [1, 2, 3],
        "min_attendees": 5,
        "time_constraints": {
            "earliest_hour": 9,
            "latest_hour": 18
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
            "start_time": "2025-10-27T14:00:00",
            "start_time_str": "2025-10-27 14:00",
            "day_name": "Thứ 2",
            "score": 85.5,
            "available_count": 12,
            "expected_attendance": 9.3,
            "mentor_count": 2,
            "user_details": [...]
        }
    ],
    "message": "Found 3 optimal slots"
}
```

#### POST /api/agent/create-poll

Tạo poll tự động với 3 slots.

**Request:**
```json
{
    "meeting_title": "Weekly Standup",
    "duration_minutes": 60,
    "constraints": {
        "required_members": [1, 2],
        "min_attendees": 5
    }
}
```

**Response:**
```json
{
    "success": true,
    "poll": {
        "title": "Weekly Standup",
        "options": [
            {
                "start_time_str": "2025-10-27 14:00",
                "objective_type": "max_attendance",
                "expected_attendance": 10.2,
                "user_details": [...]
            },
            ...
        ],
        "recommendation": "💡 Khuyến nghị: 2025-10-27 14:00 (Thứ 2)..."
    }
}
```

#### GET /api/agent/user-patterns/<user_id>

Xem patterns đã học của user.

**Response:**
```json
{
    "success": true,
    "patterns": {
        "total_bookings": 15,
        "attendance_rate": 0.85,
        "time_slot_preference": "afternoon",
        "most_active_day": 2,
        "preferred_hours": {"14": 5, "15": 4, "10": 3},
        "hour_probability": {"14": 0.33, "15": 0.27, ...}
    }
}
```

#### POST /api/agent/attendance-probability

Tính xác suất tham dự tại slot cụ thể.

**Request:**
```json
{
    "user_ids": [1, 2, 3, 4],
    "slot_datetime": "2025-10-27T14:00:00"
}
```

**Response:**
```json
{
    "success": true,
    "probabilities": {
        "1": 0.85,
        "2": 0.72,
        "3": 0.91,
        "4": 0.68
    },
    "expected_count": 3.16
}
```

#### POST /api/agent/analyze-constraints

Phân tích constraints có khả thi không.

**Request:**
```json
{
    "constraints": {
        "required_members": [1, 2, 3],
        "min_attendees": 10
    },
    "days_ahead": 14
}
```

**Response:**
```json
{
    "success": true,
    "feasible": true,
    "analysis": {
        "total_feasible_slots": 25,
        "best_score": 85.5,
        "recommendations": [
            "Limited options available. Consider extending days_ahead."
        ]
    },
    "sample_slots": [...]
}
```

## 🧮 Thuật toán Scoring

Agent sử dụng hệ thống scoring phức tạp với nhiều trọng số:

```python
WEIGHTS = {
    'attendance_count': 3.0,       # Số người tham dự
    'attendance_probability': 2.5, # Xác suất tham dự
    'fairness': 2.0,               # Công bằng
    'mentor_present': 2.5,         # Có mentor
    'required_members': 5.0,       # Thành viên bắt buộc
    'time_preference': 1.5,        # Khung giờ tốt
    'recency': 1.0,                # Gần với hiện tại
    'day_preference': 1.2          # Ngày phù hợp
}
```

**Công thức chấm điểm (simplified):**

```
Score = (expected_attendance × W1) + 
        (avg_probability × W2) + 
        (fairness_score × W3) + 
        (mentor_bonus × W4) + 
        (required_members_bonus × W5) +
        (time_bonus × W6) - 
        (recency_penalty × W7)
```

## 📊 Ví dụ thực tế

### Scenario 1: Weekly Team Meeting

**Yêu cầu:**
- Cần ít nhất 8/10 thành viên
- Phải có ít nhất 1 mentor
- Trong giờ hành chính (9h-18h)
- Thời lượng 90 phút

**Code:**
```python
slots = agent.find_optimal_slots(
    duration_minutes=90,
    constraints={
        'required_members': [1, 2, 3, 4, 5, 6, 7, 8],  # 8 members
        'required_mentors': [9],                        # 1 mentor
        'min_attendees': 8,
        'time_constraints': {
            'earliest_hour': 9,
            'latest_hour': 18
        }
    },
    objective='mentor_priority',
    days_ahead=7,
    top_n=3
)
```

### Scenario 2: Quick Sync (Công bằng)

**Yêu cầu:**
- Meeting ngắn 30 phút
- Ưu tiên công bằng (không thiên vị nhóm nào)
- Chỉ xét CLB Pro

**Code:**
```python
slots = agent.find_optimal_slots(
    duration_minutes=30,
    constraints={
        'club_filter': 'Pro',
        'min_attendees': 3
    },
    objective='fairness',
    days_ahead=3,
    top_n=5
)
```

### Scenario 3: Poll tự động cho Workshop

**Code:**
```python
poll = agent.create_smart_poll(
    meeting_title="Python Workshop",
    duration_minutes=120,
    constraints={
        'required_mentors': [1],  # Phải có mentor
        'min_attendees': 10,
        'time_constraints': {
            'earliest_hour': 13,  # Buổi chiều
            'latest_hour': 18
        }
    },
    objectives=['mentor_priority', 'max_attendance', 'balanced']
)
```

## 🔍 Chi tiết kỹ thuật

### Pattern Learning Algorithm

1. **Data Collection**: Thu thập lịch sử booking của user
2. **Feature Extraction**: Trích xuất features:
   - Hour distribution (phân bố giờ)
   - Day distribution (phân bố ngày)
   - Attendance rate (tỷ lệ tham dự)
3. **Probability Calculation**: Tính xác suất theo Bayes
4. **Categorization**: Phân loại preference (morning/afternoon/evening)

### Constraint Satisfaction

Agent sử dụng **CSP (Constraint Satisfaction Problem)** approach:

1. **Variable**: Time slots
2. **Domain**: Tất cả khung giờ khả thi trong khoảng days_ahead
3. **Constraints**: Required members, mentors, time range, etc.
4. **Solution**: Slots thỏa mãn tất cả constraints
5. **Optimization**: Chấm điểm và xếp hạng

### Complexity Analysis

- **Time slots**: O(days × hours) = O(14 × 15) = 210 slots/2 weeks
- **Users**: O(n) users
- **Constraints check**: O(1) per constraint
- **Total**: O(days × hours × users × constraints)

Với 14 ngày, 15 giờ/ngày, 20 users, 5 constraints:
→ ~21,000 operations (rất nhanh!)

## 🚀 Tips & Best Practices

### 1. Tối ưu performance

```python
# Cache agent instance nếu gọi nhiều lần
agent = create_agent()
agent.get_booking_history()  # Load history 1 lần

# Sau đó gọi nhiều lần
slots1 = agent.find_optimal_slots(...)
slots2 = agent.find_optimal_slots(...)
```

### 2. Xử lý khi không tìm thấy slot

```python
slots = agent.find_optimal_slots(...)

if not slots:
    # Thử nới lỏng constraints
    relaxed_constraints = constraints.copy()
    relaxed_constraints['min_attendees'] -= 2
    
    slots = agent.find_optimal_slots(
        constraints=relaxed_constraints,
        days_ahead=21  # Tăng số ngày
    )
```

### 3. Kết hợp nhiều objectives

```python
# Tạo poll với 3 objectives khác nhau
poll = agent.create_smart_poll(
    meeting_title="Important Meeting",
    objectives=[
        'max_attendance',      # Option 1: Đông người
        'mentor_priority',     # Option 2: Có mentor
        'fairness'             # Option 3: Công bằng
    ]
)
```

### 4. Custom scoring weights

Nếu cần customize, có thể modify weights trong `agent.py`:

```python
# Trong agent.py
WEIGHTS = {
    'attendance_count': 5.0,  # Tăng weight cho attendance
    'mentor_present': 1.0,    # Giảm weight cho mentor
    ...
}
```

## 📝 Tóm tắt

**MeetingSchedulerAgent** là một AI Agent mạnh mẽ với khả năng:

✅ Học thói quen từ lịch sử  
✅ Ước lượng xác suất tham dự chính xác  
✅ Giải ràng buộc phức tạp với nhiều đối tượng  
✅ Tối ưu hóa theo nhiều mục tiêu  
✅ Tạo poll tự động "1 chạm"  
✅ API đầy đủ và dễ sử dụng  

Agent này không chỉ tìm "ai rảnh" mà thực sự hiểu và dự đoán behavior của users, tạo ra các đề xuất thông minh và khả thi!

## 🎓 Học thêm

- Đọc code trong `app/ai/agent.py` để hiểu chi tiết thuật toán
- Chạy `python demo_agent.py` để xem demo đầy đủ
- Xem API docs trong `app/routes/agent_api.py`
- Test thử các scenarios khác nhau

---

**Happy Scheduling! 🚀**
