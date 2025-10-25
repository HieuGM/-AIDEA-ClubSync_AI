"""
ClubSync.AI - Intelligent Meeting Scheduler Agent
==================================================
AI Agent tự động tìm kiếm và đề xuất khung giờ họp tối ưu với các tính năng:
- Học thói quen và lịch sử tham dự của user
- Giải ràng buộc đa đối tượng (thành viên bắt buộc, mentor, ưu tiên...)
- Tính toán xác suất tham dự dựa trên lịch sử
- Đề xuất 3 slot tốt nhất theo mục tiêu (đông người, công bằng, có mentor...)
"""

from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional
import math

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

WORKING_HOURS = {'start': 7, 'end': 22}  # 7h sáng - 10h tối
DAYS_OF_WEEK = 7  # 0=Monday, 6=Sunday

# Trọng số cho các yếu tố scoring
WEIGHTS = {
    'attendance_count': 3.0,      # Số người tham dự
    'attendance_probability': 2.5, # Xác suất tham dự cao
    'fairness': 2.0,              # Công bằng giữa các user
    'mentor_present': 2.5,        # Có mentor
    'required_members': 5.0,      # Thành viên bắt buộc
    'time_preference': 1.5,       # Khung giờ ưa thích
    'recency': 1.0,               # Gần với hiện tại
    'day_preference': 1.2         # Ngày trong tuần phù hợp
}


# ============================================================================
# CORE AGENT CLASS
# ============================================================================

class MeetingSchedulerAgent:
    """
    AI Agent thông minh cho việc tìm kiếm và đề xuất khung giờ họp tối ưu.
    
    Chức năng chính:
    1. Phân tích lịch bận của tất cả users
    2. Học pattern thói quen từ lịch sử booking
    3. Tính xác suất tham dự cho từng user tại mỗi slot
    4. Giải ràng buộc đa đối tượng
    5. Đề xuất top 3 slots theo các mục tiêu khác nhau
    """
    
    def __init__(self, db_session):
        """
        Khởi tạo Agent với database session
        
        Args:
            db_session: SQLAlchemy session để truy vấn database
        """
        self.db = db_session
        self.user_patterns = {}  # Cache các pattern học được của user
        self.booking_history = []  # Lịch sử booking để học
        
    # ========================================================================
    # 1. DATA COLLECTION - Lấy dữ liệu từ Database
    # ========================================================================
    
    def get_all_user_availability(self) -> List:
        """
        Lấy lịch bận của TẤT CẢ users trong database
        
        Returns:
            List[UserAvailability]: Danh sách tất cả availability records
        """
        from app.models import UserAvailability
        return UserAvailability.query.all()
    
    def get_all_users(self, club_filter: Optional[str] = None) -> List:
        """
        Lấy danh sách users, có thể filter theo club
        
        Args:
            club_filter: Tên club để filter (Pro/Multi/GCC), None = tất cả
            
        Returns:
            List[User]: Danh sách users
        """
        from app.models import User
        query = User.query
        if club_filter:
            query = query.filter_by(club=club_filter)
        return query.all()
    
    def get_booking_history(self, days_back: int = 90) -> List:
        """
        Lấy lịch sử booking để học pattern
        
        Args:
            days_back: Số ngày quá khứ để lấy lịch sử
            
        Returns:
            List[Booking]: Danh sách bookings
        """
        from app.models import Booking
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        bookings = Booking.query.filter(
            Booking.start_time >= cutoff_date,
            Booking.status == 'confirmed'
        ).all()
        self.booking_history = bookings
        return bookings
    
    # ========================================================================
    # 2. PATTERN LEARNING - Học thói quen và pattern từ lịch sử
    # ========================================================================
    
    def learn_user_patterns(self, user_id: int) -> Dict:
        """
        Học pattern thói quen của một user từ lịch sử booking
        
        Phân tích:
        - Khung giờ ưa thích (morning/afternoon/evening)
        - Ngày trong tuần thường tham gia
        - Tần suất tham dự
        - Độ trễ/sớm so với lịch đã đặt
        
        Args:
            user_id: ID của user cần học pattern
            
        Returns:
            Dict: Pattern data của user
        """
        if user_id in self.user_patterns:
            return self.user_patterns[user_id]
        
        # Lấy lịch sử booking của user
        from app.models import Booking
        user_bookings = [b for b in self.booking_history if b.user_id == user_id]
        
        if not user_bookings:
            # Không có lịch sử -> return pattern mặc định
            return self._default_pattern()
        
        # Phân tích các patterns
        hour_counts = Counter()
        day_counts = Counter()
        total_bookings = len(user_bookings)
        
        for booking in user_bookings:
            hour = booking.start_time.hour
            day = booking.start_time.weekday()
            
            hour_counts[hour] += 1
            day_counts[day] += 1
        
        # Tính xác suất theo khung giờ và ngày
        pattern = {
            'user_id': user_id,
            'total_bookings': total_bookings,
            'preferred_hours': dict(hour_counts),
            'preferred_days': dict(day_counts),
            'hour_probability': {h: count/total_bookings for h, count in hour_counts.items()},
            'day_probability': {d: count/total_bookings for d, count in day_counts.items()},
            'time_slot_preference': self._categorize_time_preference(hour_counts),
            'most_active_day': day_counts.most_common(1)[0][0] if day_counts else 2,  # Default Wednesday
            'attendance_rate': self._calculate_attendance_rate(user_id)
        }
        
        self.user_patterns[user_id] = pattern
        return pattern
    
    def _default_pattern(self) -> Dict:
        """Pattern mặc định cho user mới không có lịch sử"""
        return {
            'user_id': None,
            'total_bookings': 0,
            'preferred_hours': {},
            'preferred_days': {},
            'hour_probability': {},
            'day_probability': {},
            'time_slot_preference': 'afternoon',  # Mặc định chiều
            'most_active_day': 2,  # Wednesday
            'attendance_rate': 0.7  # Giả định 70% attendance cho user mới
        }
    
    def _categorize_time_preference(self, hour_counts: Counter) -> str:
        """
        Phân loại preference thời gian: morning, afternoon, evening
        
        Args:
            hour_counts: Counter của các giờ đã booking
            
        Returns:
            str: 'morning', 'afternoon', hoặc 'evening'
        """
        morning = sum(count for hour, count in hour_counts.items() if 7 <= hour < 12)
        afternoon = sum(count for hour, count in hour_counts.items() if 12 <= hour < 18)
        evening = sum(count for hour, count in hour_counts.items() if 18 <= hour < 22)
        
        max_count = max(morning, afternoon, evening)
        if max_count == 0:
            return 'afternoon'
        if morning == max_count:
            return 'morning'
        elif afternoon == max_count:
            return 'afternoon'
        else:
            return 'evening'
    
    def _calculate_attendance_rate(self, user_id: int) -> float:
        """
        Tính tỷ lệ tham dự dựa trên số booking đã tạo vs hủy
        
        Args:
            user_id: ID của user
            
        Returns:
            float: Attendance rate từ 0.0 đến 1.0
        """
        from app.models import Booking
        total = Booking.query.filter_by(user_id=user_id).count()
        if total == 0:
            return 0.7  # Default 70%
        
        confirmed = Booking.query.filter_by(user_id=user_id, status='confirmed').count()
        return confirmed / total
    
    # ========================================================================
    # 3. AVAILABILITY ANALYSIS - Phân tích lịch rảnh/bận
    # ========================================================================
    
    def build_availability_grid(self, availabilities: List, days_ahead: int = 14) -> Dict:
        """
        Xây dựng lưới thời gian biểu chi tiết
        
        Cấu trúc: grid[date_str][hour] = {
            'busy_users': set(user_ids),
            'available_users': set(user_ids),
            'total_users': int
        }
        
        Args:
            availabilities: List UserAvailability từ DB
            days_ahead: Số ngày trong tương lai để xét
            
        Returns:
            Dict: Lưới availability
        """
        from app.models import User
        all_users = User.query.all()
        all_user_ids = {u.id for u in all_users}
        
        # Tạo grid theo ngày và giờ
        grid = defaultdict(lambda: defaultdict(lambda: {
            'busy_users': set(),
            'available_users': set(),
            'total_users': len(all_user_ids)
        }))
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Map availability vào grid
        for i in range(days_ahead):
            current_date = today + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            day_of_week = current_date.weekday()
            
            for hour in range(WORKING_HOURS['start'], WORKING_HOURS['end']):
                # Tìm users bận vào giờ này
                busy_users = set()
                for av in availabilities:
                    if av.day_of_week == day_of_week and av.is_busy:
                        if av.start_hour <= hour < av.end_hour:
                            busy_users.add(av.user_id)
                
                available_users = all_user_ids - busy_users
                
                grid[date_str][hour] = {
                    'busy_users': busy_users,
                    'available_users': available_users,
                    'total_users': len(all_user_ids)
                }
        
        return grid
    
    # ========================================================================
    # 4. PROBABILITY ESTIMATION - Ước lượng xác suất tham dự
    # ========================================================================
    
    def estimate_attendance_probability(self, user_id: int, slot_datetime: datetime) -> float:
        """
        Ước lượng xác suất user sẽ tham dự tại slot cụ thể
        
        Dựa trên:
        - Lịch sử tham dự
        - Khung giờ ưa thích
        - Ngày trong tuần
        - Attendance rate tổng thể
        
        Args:
            user_id: ID của user
            slot_datetime: Thời điểm slot
            
        Returns:
            float: Xác suất từ 0.0 đến 1.0
        """
        pattern = self.learn_user_patterns(user_id)
        
        # Base probability từ attendance rate
        base_prob = pattern['attendance_rate']
        
        # Điều chỉnh theo giờ
        hour = slot_datetime.hour
        hour_prob = pattern['hour_probability'].get(hour, 0.5)  # Default 0.5 nếu chưa có data
        
        # Điều chỉnh theo ngày
        day = slot_datetime.weekday()
        day_prob = pattern['day_probability'].get(day, 0.5)
        
        # Kết hợp các xác suất (weighted average)
        combined_prob = (
            base_prob * 0.4 +
            hour_prob * 0.3 +
            day_prob * 0.3
        )
        
        # Đảm bảo trong khoảng [0, 1]
        return max(0.0, min(1.0, combined_prob))
    
    def calculate_expected_attendance(self, user_ids: Set[int], slot_datetime: datetime) -> Dict:
        """
        Tính kỳ vọng số người tham dự tại một slot
        
        Args:
            user_ids: Set các user IDs cần xét
            slot_datetime: Thời điểm slot
            
        Returns:
            Dict: {
                'expected_count': float,
                'probabilities': {user_id: prob},
                'high_prob_users': [user_ids với prob > 0.7]
            }
        """
        probabilities = {}
        for user_id in user_ids:
            prob = self.estimate_attendance_probability(user_id, slot_datetime)
            probabilities[user_id] = prob
        
        expected_count = sum(probabilities.values())
        high_prob_users = [uid for uid, prob in probabilities.items() if prob > 0.7]
        
        return {
            'expected_count': expected_count,
            'probabilities': probabilities,
            'high_prob_users': high_prob_users
        }
    
    # ========================================================================
    # 5. CONSTRAINT SOLVING - Giải ràng buộc đa đối tượng
    # ========================================================================
    
    def check_constraints(self, slot_datetime: datetime, duration_minutes: int,
                         available_users: Set[int], constraints: Dict) -> Tuple[bool, Dict]:
        """
        Kiểm tra tất cả constraints cho một slot
        
        Constraints có thể bao gồm:
        - required_members: List user IDs bắt buộc phải có
        - required_mentors: List mentor IDs (users có quyền admin hoặc role mentor)
        - min_attendees: Số người tối thiểu
        - max_attendees: Số người tối đa
        - preferred_members: List user IDs ưu tiên
        - club_filter: Chỉ members từ club cụ thể
        - time_constraints: Giới hạn khung giờ
        
        Args:
            slot_datetime: Thời điểm bắt đầu slot
            duration_minutes: Độ dài meeting
            available_users: Set user IDs available tại slot này
            constraints: Dict các ràng buộc
            
        Returns:
            Tuple[bool, Dict]: (is_valid, violation_details)
        """
        violations = {}
        
        # Check required members
        required = set(constraints.get('required_members', []))
        if required:
            missing_required = required - available_users
            if missing_required:
                violations['missing_required'] = list(missing_required)
        
        # Check required mentors
        required_mentors = set(constraints.get('required_mentors', []))
        if required_mentors:
            missing_mentors = required_mentors - available_users
            if missing_mentors:
                violations['missing_mentors'] = list(missing_mentors)
        
        # Check minimum attendees
        min_attendees = constraints.get('min_attendees', 0)
        if len(available_users) < min_attendees:
            violations['min_attendees'] = f"Need {min_attendees}, have {len(available_users)}"
        
        # Check maximum attendees
        max_attendees = constraints.get('max_attendees', float('inf'))
        if len(available_users) > max_attendees:
            violations['max_attendees'] = f"Max {max_attendees}, have {len(available_users)}"
        
        # Check time constraints
        time_constraints = constraints.get('time_constraints', {})
        if time_constraints:
            earliest = time_constraints.get('earliest_hour', WORKING_HOURS['start'])
            latest = time_constraints.get('latest_hour', WORKING_HOURS['end'])
            
            if not (earliest <= slot_datetime.hour < latest):
                violations['time_range'] = f"Hour {slot_datetime.hour} outside range {earliest}-{latest}"
        
        # Check club filter
        club_filter = constraints.get('club_filter')
        if club_filter:
            from app.models import User
            available_club_members = set()
            for uid in available_users:
                user = User.query.get(uid)
                if user and user.club == club_filter:
                    available_club_members.add(uid)
            
            if not available_club_members:
                violations['club_filter'] = f"No members from club {club_filter}"
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    # ========================================================================
    # 6. SLOT SCORING - Chấm điểm slots theo mục tiêu
    # ========================================================================
    
    def score_slot(self, slot_datetime: datetime, duration_minutes: int,
                   available_users: Set[int], constraints: Dict,
                   objective: str = 'max_attendance') -> float:
        """
        Chấm điểm một slot theo mục tiêu cụ thể
        
        Objectives:
        - 'max_attendance': Tối đa hóa số người tham dự
        - 'max_probability': Tối đa hóa xác suất tham dự
        - 'fairness': Công bằng giữa các thành viên
        - 'mentor_priority': Ưu tiên có mentor
        - 'balanced': Cân bằng nhiều yếu tố
        
        Args:
            slot_datetime: Thời điểm slot
            duration_minutes: Độ dài meeting
            available_users: Set user IDs available
            constraints: Các ràng buộc
            objective: Mục tiêu chấm điểm
            
        Returns:
            float: Điểm số (càng cao càng tốt)
        """
        score = 0.0
        
        # Check constraints trước
        is_valid, violations = self.check_constraints(
            slot_datetime, duration_minutes, available_users, constraints
        )
        
        if not is_valid:
            return -1000.0  # Penalty lớn cho slots không thỏa constraints
        
        # Tính expected attendance
        attendance_data = self.calculate_expected_attendance(available_users, slot_datetime)
        expected_count = attendance_data['expected_count']
        avg_probability = expected_count / max(len(available_users), 1)
        
        # Scoring theo objective
        if objective == 'max_attendance':
            score += expected_count * WEIGHTS['attendance_count']
            score += avg_probability * WEIGHTS['attendance_probability']
        
        elif objective == 'max_probability':
            score += avg_probability * WEIGHTS['attendance_probability'] * 2
            score += expected_count * WEIGHTS['attendance_count'] * 0.5
        
        elif objective == 'fairness':
            # Tính độ công bằng: variance thấp = công bằng
            probs = list(attendance_data['probabilities'].values())
            if probs:
                mean_prob = sum(probs) / len(probs)
                variance = sum((p - mean_prob) ** 2 for p in probs) / len(probs)
                fairness_score = 1.0 / (1.0 + variance)  # Inverse variance
                score += fairness_score * WEIGHTS['fairness'] * 100
        
        elif objective == 'mentor_priority':
            # Kiểm tra mentors available
            from app.models import User
            mentors_available = 0
            for uid in available_users:
                user = User.query.get(uid)
                if user and user.is_admin:  # Giả định admin = mentor
                    mentors_available += 1
                    prob = attendance_data['probabilities'].get(uid, 0)
                    score += prob * WEIGHTS['mentor_present'] * 50
            
            if mentors_available > 0:
                score += WEIGHTS['mentor_present'] * 100
        
        else:  # 'balanced' - default
            # Kết hợp nhiều yếu tố
            score += expected_count * WEIGHTS['attendance_count'] * 10
            score += avg_probability * WEIGHTS['attendance_probability'] * 20
            
            # Bonus cho time preference
            hour = slot_datetime.hour
            if 9 <= hour <= 17:  # Business hours
                score += WEIGHTS['time_preference'] * 30
            if 12 <= hour < 14:  # Lunch time - penalty
                score -= 20
            
            # Bonus cho ngày trong tuần (T2-T5 tốt hơn T6-CN)
            day = slot_datetime.weekday()
            if day < 4:  # Mon-Thu
                score += WEIGHTS['day_preference'] * 20
            elif day == 4:  # Friday
                score += WEIGHTS['day_preference'] * 10
            
            # Bonus cho mentors
            from app.models import User
            for uid in available_users:
                user = User.query.get(uid)
                if user and user.is_admin:
                    score += WEIGHTS['mentor_present'] * 30
                    break
        
        # Bonus cho required members present
        required = set(constraints.get('required_members', []))
        if required and required.issubset(available_users):
            score += WEIGHTS['required_members'] * 50
        
        # Penalty cho slot quá xa trong tương lai
        days_ahead = (slot_datetime.date() - datetime.now().date()).days
        recency_penalty = days_ahead * 2
        score -= recency_penalty * WEIGHTS['recency']
        
        return score
    
    # ========================================================================
    # 7. MAIN ALGORITHM - Tìm top 3 slots tốt nhất
    # ========================================================================
    
    def find_optimal_slots(self, duration_minutes: int = 60,
                          constraints: Optional[Dict] = None,
                          objective: str = 'balanced',
                          days_ahead: int = 14,
                          top_n: int = 3) -> List[Dict]:
        """
        TÌM VÀ ĐỀ XUẤT TOP N KHUNG GIỜ TỐT NHẤT
        
        Đây là hàm chính của Agent - thực hiện toàn bộ quy trình:
        1. Lấy dữ liệu availability từ DB
        2. Học patterns từ lịch sử
        3. Build lưới availability
        4. Tìm tất cả slots khả thi
        5. Chấm điểm theo objective
        6. Trả về top N slots
        
        Args:
            duration_minutes: Độ dài meeting (phút)
            constraints: Dict các ràng buộc (required_members, mentors, etc.)
            objective: Mục tiêu ('max_attendance', 'fairness', 'mentor_priority', 'balanced')
            days_ahead: Số ngày trong tương lai để xét
            top_n: Số lượng slots đề xuất
            
        Returns:
            List[Dict]: Top N slots với đầy đủ thông tin
        """
        if constraints is None:
            constraints = {}
        
        # 1. Lấy dữ liệu
        print("🔍 Đang lấy dữ liệu từ database...")
        all_availabilities = self.get_all_user_availability()
        self.get_booking_history()  # Load history để học pattern
        
        # 2. Học patterns cho tất cả users
        print("🧠 Đang học patterns từ lịch sử...")
        all_users = self.get_all_users()
        for user in all_users:
            self.learn_user_patterns(user.id)
        
        # 3. Build availability grid
        print("📊 Đang xây dựng lưới availability...")
        grid = self.build_availability_grid(all_availabilities, days_ahead)
        
        # 4. Tìm tất cả candidate slots
        print("🔎 Đang tìm kiếm slots khả thi...")
        candidate_slots = []
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(days_ahead):
            current_date = today + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            
            for hour in range(WORKING_HOURS['start'], WORKING_HOURS['end']):
                slot_start = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                slot_end = slot_start + timedelta(minutes=duration_minutes)
                
                # Kiểm tra slot có đủ thời gian liên tục không
                if not self._is_continuous_slot(grid, slot_start, slot_end):
                    continue
                
                # Lấy available users cho slot này
                available_users = self._get_available_users_for_slot(grid, slot_start, slot_end)
                
                if not available_users:
                    continue
                
                # Check constraints
                is_valid, violations = self.check_constraints(
                    slot_start, duration_minutes, available_users, constraints
                )
                
                if not is_valid:
                    continue
                
                # Chấm điểm slot
                score = self.score_slot(
                    slot_start, duration_minutes, available_users, constraints, objective
                )
                
                # Tính thông tin chi tiết
                attendance_data = self.calculate_expected_attendance(available_users, slot_start)
                
                candidate_slots.append({
                    'start_time': slot_start,
                    'end_time': slot_end,
                    'score': score,
                    'available_users': list(available_users),
                    'available_count': len(available_users),
                    'expected_attendance': attendance_data['expected_count'],
                    'attendance_probabilities': attendance_data['probabilities'],
                    'high_probability_users': attendance_data['high_prob_users'],
                    'date': date_str,
                    'hour': hour,
                    'day_of_week': slot_start.weekday(),
                    'objective': objective
                })
        
        # 5. Sắp xếp và lấy top N
        print(f"⭐ Đang xếp hạng {len(candidate_slots)} slots...")
        sorted_slots = sorted(candidate_slots, key=lambda x: x['score'], reverse=True)
        top_slots = sorted_slots[:top_n]
        
        # 6. Enrich thông tin cho user
        print(f"✅ Tìm thấy {len(top_slots)} slots tốt nhất!")
        return self._enrich_slot_info(top_slots)
    
    def _is_continuous_slot(self, grid: Dict, start_time: datetime, end_time: datetime) -> bool:
        """
        Kiểm tra slot có liên tục (không bị gián đoạn) không
        
        Args:
            grid: Availability grid
            start_time: Thời điểm bắt đầu
            end_time: Thời điểm kết thúc
            
        Returns:
            bool: True nếu continuous
        """
        current = start_time
        while current < end_time:
            date_str = current.strftime('%Y-%m-%d')
            hour = current.hour
            
            if hour >= WORKING_HOURS['end']:
                return False
            
            if date_str not in grid or hour not in grid[date_str]:
                return False
            
            current += timedelta(hours=1)
        
        return True
    
    def _get_available_users_for_slot(self, grid: Dict, start_time: datetime, 
                                     end_time: datetime) -> Set[int]:
        """
        Lấy set users available trong TOÀN BỘ khoảng thời gian của slot
        
        Args:
            grid: Availability grid
            start_time: Thời điểm bắt đầu
            end_time: Thời điểm kết thúc
            
        Returns:
            Set[int]: User IDs available
        """
        available_users = None  # Sẽ là intersection của tất cả giờ
        
        current = start_time
        while current < end_time:
            date_str = current.strftime('%Y-%m-%d')
            hour = current.hour
            
            if date_str in grid and hour in grid[date_str]:
                hour_available = grid[date_str][hour]['available_users']
                
                if available_users is None:
                    available_users = hour_available.copy()
                else:
                    available_users &= hour_available  # Intersection
            
            current += timedelta(hours=1)
        
        return available_users if available_users is not None else set()
    
    def _enrich_slot_info(self, slots: List[Dict]) -> List[Dict]:
        """
        Làm giàu thông tin slots để dễ hiển thị cho user
        
        Args:
            slots: List slots cần enrich
            
        Returns:
            List[Dict]: Slots đã được enrich
        """
        from app.models import User
        
        enriched = []
        for slot in slots:
            # Get user details
            user_details = []
            for uid in slot['available_users']:
                user = User.query.get(uid)
                if user:
                    prob = slot['attendance_probabilities'].get(uid, 0)
                    user_details.append({
                        'id': uid,
                        'username': user.username,
                        'club': user.club,
                        'is_mentor': user.is_admin,
                        'attendance_probability': round(prob, 2)
                    })
            
            # Format datetime
            start_str = slot['start_time'].strftime('%Y-%m-%d %H:%M')
            end_str = slot['end_time'].strftime('%H:%M')
            day_names = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
            day_name = day_names[slot['day_of_week']]
            
            enriched.append({
                **slot,
                'start_time_str': start_str,
                'end_time_str': end_str,
                'day_name': day_name,
                'user_details': sorted(user_details, key=lambda x: x['attendance_probability'], reverse=True),
                'mentor_count': sum(1 for u in user_details if u['is_mentor']),
                'score_rounded': round(slot['score'], 2),
                'expected_attendance_rounded': round(slot['expected_attendance'], 1)
            })
        
        return enriched
    
    # ========================================================================
    # 8. ONE-CLICK POLL - Tạo poll tự động với 3 slots tốt nhất
    # ========================================================================
    
    def create_smart_poll(self, meeting_title: str, duration_minutes: int = 60,
                         constraints: Optional[Dict] = None,
                         objectives: Optional[List[str]] = None) -> Dict:
        """
        TẠO POLL "1 CHẠM" với 3 khung giờ tốt nhất theo các mục tiêu khác nhau
        
        Mặc định sẽ đề xuất 3 slots với 3 objectives:
        1. Max attendance (đông người nhất)
        2. Balanced (cân bằng)
        3. Mentor priority (ưu tiên mentor)
        
        Args:
            meeting_title: Tiêu đề meeting
            duration_minutes: Độ dài meeting
            constraints: Các ràng buộc
            objectives: List objectives (nếu muốn custom)
            
        Returns:
            Dict: Poll data với 3 options tốt nhất
        """
        if constraints is None:
            constraints = {}
        
        if objectives is None:
            objectives = ['max_attendance', 'balanced', 'mentor_priority']
        
        print(f"\n{'='*70}")
        print(f"🎯 TẠO POLL THÔNG MINH: {meeting_title}")
        print(f"⏱️  Thời lượng: {duration_minutes} phút")
        print(f"{'='*70}\n")
        
        all_suggestions = []
        
        # Tìm top slot cho mỗi objective
        for objective in objectives:
            print(f"\n--- Objective: {objective.upper()} ---")
            slots = self.find_optimal_slots(
                duration_minutes=duration_minutes,
                constraints=constraints,
                objective=objective,
                top_n=1  # Chỉ lấy 1 slot tốt nhất cho mỗi objective
            )
            
            if slots:
                slot = slots[0]
                slot['objective_type'] = objective
                all_suggestions.append(slot)
        
        # Đảm bảo 3 slots unique (không trùng thời gian)
        unique_slots = []
        seen_times = set()
        
        for slot in all_suggestions:
            time_key = slot['start_time_str']
            if time_key not in seen_times:
                unique_slots.append(slot)
                seen_times.add(time_key)
        
        # Nếu chưa đủ 3 slots, tìm thêm với balanced objective
        while len(unique_slots) < 3:
            extra_slots = self.find_optimal_slots(
                duration_minutes=duration_minutes,
                constraints=constraints,
                objective='balanced',
                top_n=10
            )
            
            for slot in extra_slots:
                time_key = slot['start_time_str']
                if time_key not in seen_times:
                    slot['objective_type'] = 'balanced'
                    unique_slots.append(slot)
                    seen_times.add(time_key)
                    if len(unique_slots) >= 3:
                        break
            
            if len(extra_slots) == 0:
                break  # Không còn slots nào khả thi
        
        poll_data = {
            'title': meeting_title,
            'duration_minutes': duration_minutes,
            'created_at': datetime.now().isoformat(),
            'constraints': constraints,
            'options': unique_slots[:3],  # Top 3
            'recommendation': self._generate_recommendation(unique_slots[:3])
        }
        
        self._print_poll_summary(poll_data)
        
        return poll_data
    
    def _generate_recommendation(self, slots: List[Dict]) -> str:
        """
        Tạo recommendation text cho poll
        
        Args:
            slots: List 3 slots đề xuất
            
        Returns:
            str: Recommendation message
        """
        if not slots:
            return "Không tìm thấy slot phù hợp. Vui lòng thử lại với constraints khác."
        
        best = slots[0]
        
        rec = f"💡 Khuyến nghị: {best['start_time_str']} ({best['day_name']})\n"
        rec += f"   - Kỳ vọng {best['expected_attendance_rounded']} người tham dự\n"
        rec += f"   - {best['available_count']} người available\n"
        rec += f"   - {best['mentor_count']} mentor có thể tham gia\n"
        rec += f"   - Điểm số: {best['score_rounded']}\n"
        
        return rec
    
    def _print_poll_summary(self, poll_data: Dict):
        """In summary của poll ra console"""
        print(f"\n{'='*70}")
        print(f"📊 POLL TỰ ĐỘNG: {poll_data['title']}")
        print(f"{'='*70}")
        
        for i, option in enumerate(poll_data['options'], 1):
            print(f"\n🎯 Option {i}: {option['start_time_str']} - {option['end_time_str']}")
            print(f"   📅 {option['day_name']}")
            print(f"   👥 Available: {option['available_count']} | Kỳ vọng: {option['expected_attendance_rounded']}")
            print(f"   🎓 Mentors: {option['mentor_count']}")
            print(f"   ⭐ Score: {option['score_rounded']}")
            print(f"   🎯 Objective: {option['objective_type']}")
            
            # Top 5 users có xác suất cao nhất
            top_users = option['user_details'][:5]
            print(f"   👤 Top attendees:")
            for user in top_users:
                prob_percent = int(user['attendance_probability'] * 100)
                mentor_badge = "🎓" if user['is_mentor'] else "  "
                print(f"      {mentor_badge} {user['username']} ({user['club']}) - {prob_percent}%")
        
        print(f"\n{poll_data['recommendation']}")
        print(f"{'='*70}\n")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_agent(db_session=None):
    """
    Factory function để tạo agent instance
    
    Args:
        db_session: SQLAlchemy session (optional, sẽ dùng current nếu None)
        
    Returns:
        MeetingSchedulerAgent: Agent instance
    """
    if db_session is None:
        from app.models import db
        db_session = db.session
    
    return MeetingSchedulerAgent(db_session)
