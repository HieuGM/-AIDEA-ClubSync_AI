"""
Demo Script - ClubSync.AI Intelligent Meeting Scheduler Agent
==============================================================

Script này demo cách sử dụng AI Agent để:
1. Tìm slots tối ưu với constraints phức tạp
2. Tạo poll tự động
3. Phân tích patterns của users
4. Tính xác suất tham dự

Chạy script này sau khi đã có dữ liệu trong database.
"""

from app import create_app
from app.ai.agent import create_agent
from app.models import db, User, UserAvailability, Booking
from datetime import datetime, timedelta
import random


def setup_demo_data():
    """Tạo dữ liệu demo cho việc test Agent"""
    app = create_app()
    
    with app.app_context():
        # Xóa dữ liệu cũ
        print("🗑️  Clearing old demo data...")
        UserAvailability.query.delete()
        Booking.query.delete()
        
        # Lấy danh sách users
        users = User.query.all()
        
        if not users:
            print("❌ No users found! Please create users first.")
            return
        
        print(f"👥 Found {len(users)} users")
        
        # Tạo availability patterns cho users
        print("\n📅 Creating availability patterns...")
        for user in users:
            # Mỗi user có pattern khác nhau
            for day in range(7):  # 7 ngày trong tuần
                # Random 2-3 khung giờ bận mỗi ngày
                busy_slots = random.randint(2, 3)
                
                for _ in range(busy_slots):
                    start_hour = random.randint(7, 18)
                    end_hour = start_hour + random.randint(1, 3)
                    
                    av = UserAvailability(
                        user_id=user.id,
                        day_of_week=day,
                        start_hour=start_hour,
                        end_hour=min(end_hour, 22),
                        is_busy=True,
                        recurring=True
                    )
                    db.session.add(av)
            
            print(f"   ✅ Created patterns for {user.username}")
        
        # Tạo booking history
        print("\n📚 Creating booking history...")
        for user in users[:5]:  # 5 users đầu có lịch sử
            # Tạo 5-15 bookings trong quá khứ
            num_bookings = random.randint(5, 15)
            
            for _ in range(num_bookings):
                days_ago = random.randint(1, 90)
                hour = random.choice([9, 10, 14, 15, 16])  # Giờ phổ biến
                
                start_time = datetime.now() - timedelta(days=days_ago)
                start_time = start_time.replace(hour=hour, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(hours=1)
                
                booking = Booking(
                    title=f"Meeting {random.randint(1, 100)}",
                    description="Demo booking for pattern learning",
                    start_time=start_time,
                    end_time=end_time,
                    user_id=user.id,
                    room_id=random.choice([1, 2]),
                    status='confirmed'
                )
                db.session.add(booking)
            
            print(f"   ✅ Created {num_bookings} bookings for {user.username}")
        
        db.session.commit()
        print("\n✅ Demo data created successfully!\n")


def demo_basic_slot_finding():
    """Demo 1: Tìm slots cơ bản"""
    app = create_app()
    
    with app.app_context():
        print("="*80)
        print("DEMO 1: TÌM SLOTS TỐI ƯU CƠ BẢN")
        print("="*80)
        
        agent = create_agent()
        
        # Tìm 3 slots tốt nhất với objective "balanced"
        slots = agent.find_optimal_slots(
            duration_minutes=60,
            constraints={},
            objective='balanced',
            days_ahead=7,
            top_n=3
        )
        
        print(f"\n✅ Tìm thấy {len(slots)} slots tốt nhất!")
        
        for i, slot in enumerate(slots, 1):
            print(f"\n--- Slot {i} ---")
            print(f"Thời gian: {slot['start_time_str']} - {slot['end_time_str']}")
            print(f"Ngày: {slot['day_name']}")
            print(f"Điểm số: {slot['score_rounded']}")
            print(f"Available: {slot['available_count']} người")
            print(f"Kỳ vọng tham dự: {slot['expected_attendance_rounded']} người")
            print(f"Mentors: {slot['mentor_count']}")


def demo_constraint_solving():
    """Demo 2: Giải ràng buộc phức tạp"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("DEMO 2: GIẢI RÀNG BUỘC ĐA ĐỐI TƯỢNG")
        print("="*80)
        
        agent = create_agent()
        
        # Lấy một vài user IDs để làm constraints
        users = User.query.limit(5).all()
        user_ids = [u.id for u in users]
        
        # Tìm mentors (admins)
        mentors = User.query.filter_by(is_admin=True).all()
        mentor_ids = [m.id for m in mentors] if mentors else []
        
        constraints = {
            'required_members': user_ids[:2],  # 2 thành viên bắt buộc
            'min_attendees': 3,                 # Tối thiểu 3 người
            'time_constraints': {
                'earliest_hour': 9,             # Không sớm hơn 9h
                'latest_hour': 18               # Không muộn hơn 18h
            }
        }
        
        if mentor_ids:
            constraints['required_mentors'] = mentor_ids[:1]  # Cần ít nhất 1 mentor
        
        print("\n📋 Constraints:")
        print(f"   - Required members: {constraints['required_members']}")
        print(f"   - Min attendees: {constraints['min_attendees']}")
        print(f"   - Time range: {constraints['time_constraints']['earliest_hour']}h - {constraints['time_constraints']['latest_hour']}h")
        if mentor_ids:
            print(f"   - Required mentors: {constraints['required_mentors']}")
        
        slots = agent.find_optimal_slots(
            duration_minutes=90,  # Meeting dài 90 phút
            constraints=constraints,
            objective='mentor_priority',
            days_ahead=14,
            top_n=3
        )
        
        if slots:
            print(f"\n✅ Tìm thấy {len(slots)} slots thỏa mãn tất cả constraints!")
            
            for i, slot in enumerate(slots, 1):
                print(f"\n--- Slot {i} ---")
                print(f"Thời gian: {slot['start_time_str']} - {slot['end_time_str']}")
                print(f"Điểm số: {slot['score_rounded']}")
                print(f"Kỳ vọng tham dự: {slot['expected_attendance_rounded']}/{slot['available_count']}")
                
                # Show top 3 users
                print("Top attendees:")
                for user in slot['user_details'][:3]:
                    prob = int(user['attendance_probability'] * 100)
                    mentor_badge = "🎓" if user['is_mentor'] else "👤"
                    print(f"  {mentor_badge} {user['username']} - {prob}% probability")
        else:
            print("\n❌ Không tìm thấy slot nào thỏa mãn constraints!")
            print("💡 Gợi ý: Thử nới lỏng constraints hoặc tăng days_ahead")


def demo_smart_poll():
    """Demo 3: Tạo poll tự động"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("DEMO 3: TẠO POLL TỰ ĐỘNG '1 CHẠM'")
        print("="*80)
        
        agent = create_agent()
        
        users = User.query.limit(4).all()
        user_ids = [u.id for u in users]
        
        poll = agent.create_smart_poll(
            meeting_title="Weekly Team Sync",
            duration_minutes=60,
            constraints={
                'required_members': user_ids[:2],
                'min_attendees': 3
            },
            objectives=['max_attendance', 'balanced', 'mentor_priority']
        )
        
        # Poll summary đã được in bởi agent
        print(f"\n📊 Poll ID: {poll['created_at']}")
        print(f"📝 Title: {poll['title']}")
        print(f"⏱️  Duration: {poll['duration_minutes']} minutes")
        print(f"🎯 Options generated: {len(poll['options'])}")


def demo_pattern_learning():
    """Demo 4: Học patterns của users"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("DEMO 4: HỌC PATTERNS VÀ THÓI QUEN")
        print("="*80)
        
        agent = create_agent()
        agent.get_booking_history()
        
        users = User.query.limit(3).all()
        
        for user in users:
            print(f"\n👤 User: {user.username} ({user.club})")
            
            pattern = agent.learn_user_patterns(user.id)
            
            print(f"   📚 Total bookings: {pattern['total_bookings']}")
            print(f"   ✅ Attendance rate: {pattern['attendance_rate']*100:.0f}%")
            print(f"   ⏰ Time preference: {pattern['time_slot_preference']}")
            
            # Top 3 preferred hours
            if pattern['preferred_hours']:
                sorted_hours = sorted(
                    pattern['preferred_hours'].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:3]
                print(f"   🕐 Preferred hours: {[h for h, _ in sorted_hours]}")
            
            # Top 3 preferred days
            if pattern['preferred_days']:
                day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                sorted_days = sorted(
                    pattern['preferred_days'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                preferred_day_names = [day_names[d] for d, _ in sorted_days]
                print(f"   📅 Preferred days: {preferred_day_names}")


def demo_probability_estimation():
    """Demo 5: Ước lượng xác suất tham dự"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("DEMO 5: ƯỚC LƯỢNG XÁC SUẤT THAM DỰ")
        print("="*80)
        
        agent = create_agent()
        agent.get_booking_history()
        
        # Test với vài time slots khác nhau
        test_slots = [
            datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1),
            datetime.now().replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=2),
            datetime.now().replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=3),
        ]
        
        users = User.query.limit(3).all()
        
        for slot in test_slots:
            print(f"\n⏰ Time slot: {slot.strftime('%Y-%m-%d %H:%M')} ({slot.strftime('%A')})")
            
            for user in users:
                prob = agent.estimate_attendance_probability(user.id, slot)
                prob_percent = int(prob * 100)
                
                # Visual indicator
                bars = '█' * (prob_percent // 10)
                print(f"   {user.username:15s} [{bars:10s}] {prob_percent:3d}%")


def main():
    """Chạy tất cả demos"""
    print("\n" + "🤖"*40)
    print("ClubSync.AI - Intelligent Meeting Scheduler Agent")
    print("Demo Suite")
    print("🤖"*40 + "\n")
    
    # Setup demo data
    setup_demo_data()
    
    # Run demos
    demo_basic_slot_finding()
    demo_constraint_solving()
    demo_smart_poll()
    demo_pattern_learning()
    demo_probability_estimation()
    
    print("\n" + "="*80)
    print("✅ ALL DEMOS COMPLETED!")
    print("="*80 + "\n")
    
    print("💡 Bạn có thể sử dụng API endpoints:")
    print("   POST /api/agent/suggest-slots")
    print("   POST /api/agent/create-poll")
    print("   GET  /api/agent/user-patterns/<user_id>")
    print("   POST /api/agent/attendance-probability")
    print("   POST /api/agent/analyze-constraints")
    print("   GET  /api/agent/health")
    print()


if __name__ == '__main__':
    main()
