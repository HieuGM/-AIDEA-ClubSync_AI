# AI Agent Quick Start Guide 🚀

## Giới thiệu nhanh

AI Agent này tự động tìm khung giờ họp tối ưu với khả năng:
- 🧠 Học thói quen từ lịch sử
- 📊 Dự đoán xác suất tham dự
- 🎯 Giải ràng buộc phức tạp
- 🗳️ Tạo poll tự động

## Cài đặt nhanh

```bash
# Đã có sẵn trong ClubSync.AI, không cần cài thêm gì!
# Agent nằm trong app/ai/agent.py
```

## Sử dụng cơ bản

### 1. Trong Python code

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

### 2. Qua API (curl)

```bash
# Health check
curl http://localhost:5000/api/agent/health

# Tìm slots
curl -X POST http://localhost:5000/api/agent/suggest-slots \
  -H "Content-Type: application/json" \
  -d '{
    "duration_minutes": 60,
    "constraints": {"min_attendees": 5},
    "objective": "balanced",
    "top_n": 3
  }'

# Tạo poll
curl -X POST http://localhost:5000/api/agent/create-poll \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_title": "Team Meeting",
    "duration_minutes": 60,
    "constraints": {"min_attendees": 5}
  }'
```

### 3. Demo script

```bash
# Chạy demo đầy đủ
python demo_agent.py
```

## Constraints phổ biến

```python
constraints = {
    'required_members': [1, 2, 3],      # User IDs bắt buộc
    'required_mentors': [4],            # Mentor IDs bắt buộc
    'min_attendees': 5,                 # Tối thiểu 5 người
    'max_attendees': 15,                # Tối đa 15 người
    'club_filter': 'Pro',               # Chỉ CLB Pro
    'time_constraints': {
        'earliest_hour': 9,             # Không sớm hơn 9h
        'latest_hour': 18               # Không muộn hơn 18h
    }
}
```

## Objectives (Mục tiêu)

| Objective | Khi nào dùng |
|-----------|--------------|
| `balanced` | **Default** - Cân bằng tất cả yếu tố |
| `max_attendance` | Cần nhiều người nhất có thể |
| `max_probability` | Cần đảm bảo attendance cao |
| `fairness` | Công bằng giữa các thành viên |
| `mentor_priority` | Training/Workshop cần mentor |

## API Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/api/agent/suggest-slots` | POST | Tìm slots tối ưu |
| `/api/agent/create-poll` | POST | Tạo poll tự động |
| `/api/agent/user-patterns/<id>` | GET | Xem patterns của user |
| `/api/agent/attendance-probability` | POST | Tính xác suất tham dự |
| `/api/agent/analyze-constraints` | POST | Phân tích constraints |
| `/api/agent/health` | GET | Health check |

## Ví dụ đầy đủ

```python
from app import create_app
from app.ai.agent import create_agent

app = create_app()

with app.app_context():
    agent = create_agent()
    
    # Scenario: Weekly team sync
    # - Cần ít nhất 8 người
    # - Phải có 1 mentor
    # - Trong giờ hành chính
    # - 90 phút
    
    slots = agent.find_optimal_slots(
        duration_minutes=90,
        constraints={
            'min_attendees': 8,
            'required_mentors': [1],  # User ID của mentor
            'time_constraints': {
                'earliest_hour': 9,
                'latest_hour': 18
            }
        },
        objective='mentor_priority',
        days_ahead=7,
        top_n=3
    )
    
    # In kết quả
    for i, slot in enumerate(slots, 1):
        print(f"\n🎯 Option {i}:")
        print(f"   Time: {slot['start_time_str']}")
        print(f"   Score: {slot['score_rounded']}")
        print(f"   Expected: {slot['expected_attendance_rounded']} people")
        print(f"   Mentors: {slot['mentor_count']}")
```

## Troubleshooting

### ❌ Không tìm thấy slot nào

**Giải pháp:**
1. Nới lỏng constraints (giảm `min_attendees`)
2. Tăng `days_ahead` (xét nhiều ngày hơn)
3. Thay đổi `objective`
4. Kiểm tra availability data đã đủ chưa

### ❌ Expected attendance quá thấp

**Giải pháp:**
1. Kiểm tra booking history đã đủ chưa (cần ít nhất vài bookings)
2. Verify availability data đúng chưa
3. Thử objective `max_probability`

### ❌ API trả về 500 error

**Giải pháp:**
1. Check database có data chưa
2. Verify constraints format đúng
3. Xem logs để debug

## Documentation đầy đủ

Xem file `docs/AI_AGENT_DOCUMENTATION.md` để hiểu chi tiết về:
- Thuật toán
- Architecture
- Scoring mechanism
- Advanced usage
- API specs

## Support

Có vấn đề? Check:
1. `demo_agent.py` - Ví dụ đầy đủ
2. `docs/AI_AGENT_DOCUMENTATION.md` - Docs chi tiết
3. `app/ai/agent.py` - Source code với comments

---

**Made with ❤️ for ClubSync.AI**
