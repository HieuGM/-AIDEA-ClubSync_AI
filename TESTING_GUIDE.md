# 🧪 Hướng dẫn Test AI Agent

## Quick Test (5 phút)

### 1. Kiểm tra Agent hoạt động

```bash
# Activate conda environment (nếu chưa)
conda activate clubsync

# Chạy test suite
python test_agent.py
```

**Kết quả mong đợi:** 10/10 tests passed ✅

---

### 2. Chạy Demo

```bash
python demo_agent.py
```

**Kết quả mong đợi:** 
- Setup demo data thành công
- Chạy 5 demos:
  1. ✅ Tìm slots cơ bản
  2. ✅ Giải ràng buộc phức tạp
  3. ✅ Tạo poll tự động
  4. ✅ Học patterns
  5. ✅ Ước lượng xác suất

---

### 3. Test API Endpoints

#### Bước 1: Start Flask app

```bash
python run.py
```

App sẽ chạy tại: http://localhost:5000

#### Bước 2: Test health check

```bash
curl http://localhost:5000/api/agent/health
```

**Kết quả mong đợi:**
```json
{
  "status": "healthy",
  "agent": "MeetingSchedulerAgent",
  "total_users": <số users trong DB>,
  "version": "1.0.0"
}
```

#### Bước 3: Test suggest slots (cần đăng nhập)

**Option A: Dùng Postman/Insomnia**
1. Đăng nhập trước để lấy session cookie
2. POST to `http://localhost:5000/api/agent/suggest-slots`
3. Body (JSON):
```json
{
  "duration_minutes": 60,
  "constraints": {
    "min_attendees": 3
  },
  "objective": "balanced",
  "top_n": 3
}
```

**Option B: Dùng browser console**
1. Đăng nhập vào web app
2. Mở Developer Tools > Console
3. Paste code:
```javascript
fetch('/api/agent/suggest-slots', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    duration_minutes: 60,
    constraints: {min_attendees: 3},
    objective: 'balanced',
    top_n: 3
  })
})
.then(r => r.json())
.then(console.log)
```

---

## Full Test Scenarios

### Scenario 1: Tìm slot cho Weekly Meeting

```python
from app import create_app
from app.ai.agent import create_agent

app = create_app()
with app.app_context():
    agent = create_agent()
    
    slots = agent.find_optimal_slots(
        duration_minutes=60,
        constraints={
            'min_attendees': 5,
            'time_constraints': {
                'earliest_hour': 9,
                'latest_hour': 18
            }
        },
        objective='balanced',
        days_ahead=7,
        top_n=3
    )
    
    for slot in slots:
        print(f"{slot['start_time_str']} - Score: {slot['score_rounded']}")
```

### Scenario 2: Tạo poll với mentor required

```python
poll = agent.create_smart_poll(
    meeting_title="Python Workshop",
    duration_minutes=120,
    constraints={
        'required_mentors': [1],  # User ID của mentor
        'min_attendees': 8
    }
)

print(f"Poll created with {len(poll['options'])} options")
```

### Scenario 3: Check user patterns

```python
from app.models import User

user = User.query.first()
agent.get_booking_history()
pattern = agent.learn_user_patterns(user.id)

print(f"User: {user.username}")
print(f"Total bookings: {pattern['total_bookings']}")
print(f"Attendance rate: {pattern['attendance_rate']:.0%}")
print(f"Preference: {pattern['time_slot_preference']}")
```

---

## Troubleshooting

### ❌ Test failed: No users found

**Giải pháp:**
```bash
# Tạo users mới
python
>>> from app import create_app
>>> from app.models import db, User
>>> app = create_app()
>>> with app.app_context():
...     user = User(username='testuser', email='test@test.com', club='Pro')
...     user.set_password('password')
...     db.session.add(user)
...     db.session.commit()
```

### ❌ No slots found

**Nguyên nhân:** Chưa có availability data

**Giải pháp:** Chạy demo để tạo data:
```bash
python demo_agent.py
```

### ❌ API returns 401 Unauthorized

**Nguyên nhân:** Chưa đăng nhập

**Giải pháp:**
1. Đăng nhập qua web UI
2. Hoặc dùng session cookie từ browser
3. Hoặc test từ browser console (đã đăng nhập)

### ❌ ImportError

**Giải pháp:**
```bash
# Verify trong ClubSync.AI directory
pwd

# Install dependencies nếu thiếu
pip install -r requirements.txt
```

---

## Performance Test

### Test với nhiều users

```python
import time
from app import create_app
from app.ai.agent import create_agent

app = create_app()
with app.app_context():
    agent = create_agent()
    
    # Measure time
    start = time.time()
    
    slots = agent.find_optimal_slots(
        duration_minutes=60,
        days_ahead=14,
        top_n=10
    )
    
    elapsed = time.time() - start
    
    print(f"Found {len(slots)} slots in {elapsed:.2f} seconds")
    # Mong đợi: < 1 giây với ~20 users
```

---

## Checklist Test

- [ ] Test suite pass (10/10)
- [ ] Demo chạy thành công
- [ ] Health check API works
- [ ] Suggest slots API works
- [ ] Create poll API works
- [ ] User patterns đúng
- [ ] Probability estimation hợp lý
- [ ] Constraints được respect
- [ ] Performance < 1s cho 14 ngày

---

## Next Steps

Sau khi test thành công:

1. ✅ Tích hợp vào UI (tạo button "Smart Schedule")
2. ✅ Thêm notifications
3. ✅ Deploy lên production
4. ✅ Monitor performance
5. ✅ Collect user feedback

---

**Happy Testing! 🧪**
