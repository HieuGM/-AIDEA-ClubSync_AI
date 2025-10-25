"""
Simple Test Suite cho AI Agent
Chạy: python test_agent.py
"""

import sys
from datetime import datetime, timedelta


def test_import():
    """Test 1: Import agent module"""
    print("\n🧪 Test 1: Import agent module")
    try:
        from app.ai.agent import create_agent, MeetingSchedulerAgent
        print("   ✅ PASSED - Agent module imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        return False


def test_agent_creation():
    """Test 2: Tạo agent instance"""
    print("\n🧪 Test 2: Create agent instance")
    try:
        from app import create_app
        from app.ai.agent import create_agent
        
        app = create_app()
        with app.app_context():
            agent = create_agent()
            print(f"   ✅ PASSED - Agent created: {type(agent).__name__}")
            return True
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        return False


def test_get_users():
    """Test 3: Lấy danh sách users"""
    print("\n🧪 Test 3: Get all users")
    try:
        from app import create_app
        from app.ai.agent import create_agent
        
        app = create_app()
        with app.app_context():
            agent = create_agent()
            users = agent.get_all_users()
            print(f"   ✅ PASSED - Found {len(users)} users")
            return True
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        return False


def test_get_availability():
    """Test 4: Lấy availability data"""
    print("\n🧪 Test 4: Get availability data")
    try:
        from app import create_app
        from app.ai.agent import create_agent
        
        app = create_app()
        with app.app_context():
            agent = create_agent()
            availabilities = agent.get_all_user_availability()
            print(f"   ✅ PASSED - Found {len(availabilities)} availability records")
            return True
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        return False


def test_booking_history():
    """Test 5: Lấy booking history"""
    print("\n🧪 Test 5: Get booking history")
    try:
        from app import create_app
        from app.ai.agent import create_agent
        
        app = create_app()
        with app.app_context():
            agent = create_agent()
            bookings = agent.get_booking_history(days_back=30)
            print(f"   ✅ PASSED - Found {len(bookings)} bookings in last 30 days")
            return True
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        return False


def test_pattern_learning():
    """Test 6: Học pattern của user"""
    print("\n🧪 Test 6: Learn user patterns")
    try:
        from app import create_app
        from app.ai.agent import create_agent
        from app.models import User
        
        app = create_app()
        with app.app_context():
            agent = create_agent()
            agent.get_booking_history()
            
            user = User.query.first()
            if user:
                pattern = agent.learn_user_patterns(user.id)
                print(f"   ✅ PASSED - Learned pattern for user {user.username}")
                print(f"      - Total bookings: {pattern['total_bookings']}")
                print(f"      - Attendance rate: {pattern['attendance_rate']:.2f}")
                print(f"      - Time preference: {pattern['time_slot_preference']}")
                return True
            else:
                print("   ⚠️  WARNING - No users found to test")
                return True
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        return False


def test_probability_estimation():
    """Test 7: Ước lượng xác suất tham dự"""
    print("\n🧪 Test 7: Estimate attendance probability")
    try:
        from app import create_app
        from app.ai.agent import create_agent
        from app.models import User
        
        app = create_app()
        with app.app_context():
            agent = create_agent()
            agent.get_booking_history()
            
            user = User.query.first()
            if user:
                # Test với slot ngày mai lúc 14h
                tomorrow_2pm = datetime.now().replace(hour=14, minute=0) + timedelta(days=1)
                prob = agent.estimate_attendance_probability(user.id, tomorrow_2pm)
                print(f"   ✅ PASSED - Probability for {user.username}: {prob:.2f}")
                return True
            else:
                print("   ⚠️  WARNING - No users found to test")
                return True
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        return False


def test_find_slots_basic():
    """Test 8: Tìm slots cơ bản (không constraints)"""
    print("\n🧪 Test 8: Find basic slots")
    try:
        from app import create_app
        from app.ai.agent import create_agent
        
        app = create_app()
        with app.app_context():
            agent = create_agent()
            
            slots = agent.find_optimal_slots(
                duration_minutes=60,
                constraints={},
                objective='balanced',
                days_ahead=7,
                top_n=3
            )
            
            print(f"   ✅ PASSED - Found {len(slots)} optimal slots")
            
            if slots:
                best = slots[0]
                print(f"      Best slot: {best['start_time_str']}")
                print(f"      Score: {best['score_rounded']}")
                print(f"      Expected attendance: {best['expected_attendance_rounded']}")
            
            return True
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        return False


def test_find_slots_with_constraints():
    """Test 9: Tìm slots với constraints"""
    print("\n🧪 Test 9: Find slots with constraints")
    try:
        from app import create_app
        from app.ai.agent import create_agent
        from app.models import User
        
        app = create_app()
        with app.app_context():
            agent = create_agent()
            
            # Get some users for constraints
            users = User.query.limit(2).all()
            user_ids = [u.id for u in users]
            
            constraints = {
                'min_attendees': 2,
                'time_constraints': {
                    'earliest_hour': 9,
                    'latest_hour': 18
                }
            }
            
            if user_ids:
                constraints['required_members'] = user_ids
            
            slots = agent.find_optimal_slots(
                duration_minutes=60,
                constraints=constraints,
                objective='balanced',
                days_ahead=7,
                top_n=3
            )
            
            print(f"   ✅ PASSED - Found {len(slots)} slots with constraints")
            return True
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        return False


def test_create_poll():
    """Test 10: Tạo poll tự động"""
    print("\n🧪 Test 10: Create smart poll")
    try:
        from app import create_app
        from app.ai.agent import create_agent
        
        app = create_app()
        with app.app_context():
            agent = create_agent()
            
            poll = agent.create_smart_poll(
                meeting_title="Test Meeting",
                duration_minutes=60,
                constraints={'min_attendees': 2}
            )
            
            print(f"   ✅ PASSED - Poll created with {len(poll['options'])} options")
            print(f"      Title: {poll['title']}")
            
            return True
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        return False


def run_all_tests():
    """Chạy tất cả tests"""
    print("="*70)
    print("🤖 ClubSync.AI - AI Agent Test Suite")
    print("="*70)
    
    tests = [
        test_import,
        test_agent_creation,
        test_get_users,
        test_get_availability,
        test_booking_history,
        test_pattern_learning,
        test_probability_estimation,
        test_find_slots_basic,
        test_find_slots_with_constraints,
        test_create_poll
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ UNEXPECTED ERROR - {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"📊 Test Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*70)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED! Agent is ready to use! 🎉")
        return 0
    else:
        print(f"⚠️  {failed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
