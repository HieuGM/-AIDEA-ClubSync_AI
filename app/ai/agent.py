from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional
import json
import re
import os
from openai import OpenAI

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


class MeetingSchedulerAgent:
    def __init__(self, db_session, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Khởi tạo Agent với database session và OpenAI client
        
        Args:
            db_session: SQLAlchemy session để t ruy vấn database
            api_key: OpenAI API key (nếu None sẽ lấy từ config)
            model: Model name (nếu None sẽ lấy từ config, mặc định gpt-4o-mini)
        """
        self.db = db_session
        self.booking_history = []
        # Khởi tạo NVIDIA client
        from config import Config

        self.api_key = api_key or Config.AI_API_KEY 
        self.model = model or Config.AI_MODEL or 'meta/llama3-8b-instruct'

        if not self.api_key:
            raise ValueError("NVIDIA API key is required. Set NVIDIA_API_KEY in .env file")
 
        # Khởi tạo client trỏ đến endpoint của NVIDIA
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=self.api_key
        )
        print(f"NVIDIA Agent initialized with model: {self.model}")
        
    # 1. DATA COLLECTION - Lấy dữ liệu từ Database
    
    def get_all_user_availability(self) -> List:
        """
        Lấy lịch bận của TẤT CẢ users trong database
        
        Returns:
            List[UserAvailability]: Danh sách tất cả availability records
        """
        from app.models import UserAvailability
        return UserAvailability.query.all()
    
    def get_all_users(self, club_filter: Optional[str]) -> List:
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
    
    # 2. DATA ANALYSIS - Phân tích dữ liệu user và lịch sử

    def analyze_user_history(self, user_id: int) -> Dict:
        """
        Phân tích lịch sử booking của user để tạo summary
        
        Args:
            user_id: ID của user cần phân tích
            
        Returns:
            Dict: Summary data của user
        """
        from app.models import Booking, User
        
        user = User.query.get(user_id)
        if not user:
            return {}
        
        user_bookings = [b for b in self.booking_history if b.user_id == user_id]
        
        if not user_bookings:
            return {
                'user_id': user_id,
                'username': user.username,
                'club': user.club,
                'is_mentor': user.is_admin,
                'total_bookings': 0,
                'attendance_rate': 0.7  # Default
            }
        
        # Phân tích patterns
        hour_counts = Counter()
        day_counts = Counter()
        
        for booking in user_bookings:
            hour_counts[booking.start_time.hour] += 1
            day_counts[booking.start_time.weekday()] += 1
        
        # Tính attendance rate
        total = Booking.query.filter_by(user_id=user_id).count()
        confirmed = Booking.query.filter_by(user_id=user_id, status='confirmed').count()
        attendance_rate = confirmed / total if total > 0 else 0.7
        
        return {
            'user_id': user_id,
            'username': user.username,
            'club': user.club,
            'is_mentor': user.is_admin,
            'total_bookings': len(user_bookings),
            'preferred_hours': dict(hour_counts.most_common(3)),
            'preferred_days': dict(day_counts.most_common(3)),
            'attendance_rate': attendance_rate
        }
        
    # 3. AVAILABILITY ANALYSIS - Phân tích lịch rảnh/bận
    
    def build_availability_grid(self, availabilities: List, days_ahead: int) -> Dict:
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
    
    # 4. OPENAI ANALYSIS - Sử dụng GPT để phân tích và đưa ra quyết định
    
    def ask_gpt_to_analyze_slots(self, candidate_slots: List[Dict], 
                                  constraints: Dict, objective: str) -> List[Dict]:
        """
        Sử dụng OpenAI GPT để phân tích và chấm điểm các slots
        
        Args:
            candidate_slots: Danh sách các slots khả thi
            constraints: Các ràng buộc
            objective: Mục tiêu (max_attendance, balanced, mentor_priority, fairness)
            
        Returns:
            List[Dict]: Slots đã được GPT phân tích và chấm điểm
        """
        print(f"Đang sử dụng ({self.model}) để phân tích {len(candidate_slots)} slots...")
        
        max_slots_to_analyze = min(20, len(candidate_slots))
        slots_summary = []
        for idx, slot in enumerate(candidate_slots[:max_slots_to_analyze]):
            user_summaries = []
            # CHỈ lấy 10 users để giảm context size
            for uid in list(slot['available_users'])[:10]:
                history = self.analyze_user_history(uid)
                if history:
                    user_summaries.append({
                        'id': uid,
                        'username': history.get('username', 'Unknown'),
                        'club': history.get('club', 'Unknown'),
                        'is_mentor': history.get('is_mentor', False),
                        'total_bookings': history.get('total_bookings', 0),
                        'attendance_rate': history.get('attendance_rate', 0.7)
                    })
            
            slots_summary.append({
                'index': idx,
                'start_time': slot['start_time'].strftime('%Y-%m-%d %H:%M'),
                'end_time': slot['end_time'].strftime('%H:%M'),
                'day_of_week': slot['day_of_week'],
                'hour': slot['hour'],
                'available_count': slot['available_count'],
                'users': user_summaries
            })
        
        system_prompt = """Bạn là AI lập lịch họp. Phân tích và chấm điểm slots. Hãy nhớ lịch đó phải có thời gian bắt đầu(start_time) phải muộn hơn thời gian thực tế hiện tại ít nhất 2 tiếng.
        Chỉ trả về duy nhất 1 đối tượng JSON hợp lệ. Không được thêm bất kỳ JSON giải thích, văn bản hay markdown nào khác.

Trả về JSON format BẮT BUỘC:
{
  "analysis": "1-2 câu tổng quan",
  "slots": [
    {"index": 0, "score": số nguyên từ 0-100(phải chấm điểm), "reasoning": "Lý do ngắn (max 20 từ)"}
  ]
}
"""
        
        user_prompt = f"""Chấm điểm {len(slots_summary)} slots sau (0-100 điểm):

MỤC TIÊU: {objective}

RÀNG BUỘC: {json.dumps(constraints, ensure_ascii=False) if constraints else "Không có"}

TRỌNG SỐ CHẤM ĐIỂM: {json.dumps(WEIGHTS, ensure_ascii=False)}


SLOTS (mỗi slot có: thời gian, số người rảnh, có mentor không):
{json.dumps(slots_summary, ensure_ascii=False)}

Chỉ trả về JSON. Lý do phải ngắn (max 15 từ)."""
        
        try:
            # Llama-8B instruction trick: Nhắc lại format 1 lần nữa ở user prompt hoặc system prompt
            # (Giả sử system_prompt của bạn đã có yêu cầu trả JSON)
            
            response = self.client.chat.completions.create(
                model=self.model, # nvidia/llama-3.1-8b-instruct...
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2, # Llama nên để temp thấp hơn (0.2 - 0.4) để output format ổn định
                stream=False
            )
            
            response_text = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            
            print(f"Llama Response length: {len(response_text)} chars")

            if finish_reason == "length":
                print(f"WARNING: Response bị truncate! Chuyển sang fallback.")
                raise ValueError("Response truncated")

            # --- XỬ LÝ OUTPUT CỦA LLAMA ---
            # Llama 8B rất hay trả về dạng: "Here is the json:\n ```json\n{...}\n```"
            # Cách an toàn nhất là dùng Regex tìm khối ngoặc nhọn {} bao ngoài cùng.
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            
            if json_match:
                clean_json_str = json_match.group(0)
            else:
                # Trường hợp Llama không trả về JSON hoặc format quá lạ
                print(f"Raw response không chứa JSON hợp lệ: {response_text[:100]}...")
                raise ValueError("No JSON found in response")

            result = json.loads(clean_json_str)
            print(f"Analysis: {result.get('analysis', 'Done')}")
            
            # --- SỬA LỖI LOGIC NGHIÊM TRỌNG (CRITICAL FIX) ---
            # Tạo map {index_gpt: data} để tra cứu O(1)
            slot_scores_map = {item.get('index'): item for item in result.get('slots', [])}
            
            # Dùng enumerate để lấy đúng vị trí i, KHÔNG dùng .index(slot)
            for idx, slot in enumerate(candidate_slots[:max_slots_to_analyze]):
                
                # Tìm xem GPT/Llama có trả về kết quả cho index này không
                gpt_data = slot_scores_map.get(idx) # Trả về None nếu không tìm thấy
                
                if gpt_data:
                    slot['gpt_score'] = gpt_data.get('score', 50)
                    slot['gpt_reasoning'] = gpt_data.get('reasoning', 'No reasoning')
                else:
                    slot['gpt_score'] = 50
                    slot['gpt_reasoning'] = 'Not analyzed (Index missing)'

            return candidate_slots

        except (json.JSONDecodeError, ValueError, Exception) as e:
            print(f"Lỗi xử lý Llama ({type(e).__name__}): {e}")
            
            # Fallback logic
            print("Sử dụng fallback scoring...")
            for slot in candidate_slots:
                slot['gpt_score'] = min(slot['available_count'] * 10, 100)
                slot['gpt_reasoning'] = f'Fallback: {slot["available_count"]} người rảnh (Error)'
                
            return candidate_slots
    
    # 5. CONSTRAINT SOLVING - Giải ràng buộc đa đối tượng
    
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
        
        # Check time constraints
        time_constraints = constraints.get('time_constraints', {})
        if time_constraints:
            earliest = time_constraints.get('earliest_hour', WORKING_HOURS['start'])
            latest = time_constraints.get('latest_hour', WORKING_HOURS['end'])
            
            # Slot phải bắt đầu và KẾT THÚC trong khung giờ cho phép
            slot_end = slot_datetime + timedelta(minutes=duration_minutes)
            slot_end_hour = slot_end.hour + (1 if slot_end.minute > 0 else 0)  # Round up
            
            if not (earliest <= slot_datetime.hour < latest and slot_end_hour <= latest):
                violations['time_range'] = f"Slot {slot_datetime.hour}:00-{slot_end_hour}:00 outside range {earliest}:00-{latest}:00"
            
            # Check preferred days (0=Monday, 6=Sunday)
            preferred_days = time_constraints.get('preferred_days', [])
            if preferred_days and slot_datetime.weekday() not in preferred_days:
                day_names = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
                violations['preferred_days'] = f"{day_names[slot_datetime.weekday()]} not in preferred days"
        
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
    
    # 5. SLOT SCORING - Chấm điểm cơ bản
    
    def score_slot(self, slot_datetime: datetime, duration_minutes: int,
                   available_users: Set[int], constraints: Dict, 
                   objective: str = 'max_attendance') -> float:
        """
        Chấm điểm cơ bản một slot (sẽ được GPT refine sau)
        
        Args:
            slot_datetime: Thời điểm slot
            duration_minutes: Độ dài meeting
            available_users: Set user IDs available
            constraints: Các ràng buộc
            objective: Mục tiêu chấm điểm
            
        Returns:
            float: Điểm số cơ bản (0-100)
        """
        # Check constraints trước
        is_valid, violations = self.check_constraints(
            slot_datetime, duration_minutes, available_users, constraints
        )
        
        if not is_valid:
            return -1000.0  # Penalty lớn cho slots không thỏa constraints
        
        score = 0.0
        if objective == 'max_attendance':
            # Ưu tiên số lượng: Mỗi người +10 điểm
            score += len(available_users) * 10
        elif objective == 'efficiency':
            # Ưu tiên slot vừa đủ (không quá đông, không quá vắng)
            ideal_size = constraints.get('min_attendees', 3) + 2
            diff = abs(len(available_users) - ideal_size)
            score += max(50 - diff * 5, 0) # Càng gần ideal càng cao
        
        # Bonus cho time slots hợp lý
        hour = slot_datetime.hour
        if 9 <= hour <= 11 or 14 <= hour <= 16:
            score += 20
        elif 8 <= hour <= 18: # Giờ hành chính thường
            score += 10
        else: # Ngoài giờ
            score -= 10
        
        # Bonus cho ngày trong tuần
        day = slot_datetime.weekday()
        if day < 4:  # Thứ 2 - Thứ 5: Ưu tiên cao
            score += 15
        elif day == 4: # Thứ 6: Hơi thấp hơn chút (mọi người hay lười)
            score += 10
        else: # Cuối tuần
            score -= 20 # Trừ điểm nặng nếu họp cuối tuần (trừ khi cần thiết)
    
        return score
    
    # 6. MAIN ALGORITHM - Tìm top slots với AI
    
    def find_optimal_slots(self, duration_minutes: int = 60,
                          constraints: Optional[Dict] = None,
                          objective: str = 'balanced',
                          days_ahead: int = 14,
                          top_n: int = 3,
                          use_gpt: bool = True) -> List[Dict]:
        """
        TÌM VÀ ĐỀ XUẤT TOP N KHUNG GIỜ TỐT NHẤT
        
        Quy trình:
        1. Lấy dữ liệu availability từ DB
        2. Phân tích lịch sử bookings
        3. Build lưới availability
        4. Tìm tất cả slots khả thi
        5. SỬ DỤNG GPT để phân tích và chấm điểm thông minh
        6. Trả về top N slots với reasoning từ AI
        
        Args:
            duration_minutes: Độ dài meeting (phút)
            constraints: Dict các ràng buộc (required_members, mentors, etc.)
            objective: Mục tiêu ('max_attendance', 'fairness', 'mentor_priority', 'balanced')
            days_ahead: Số ngày trong tương lai để xét
            top_n: Số lượng slots đề xuất
            use_gpt: Có sử dụng GPT để phân tích hay không (default True)
            
        Returns:
            List[Dict]: Top N slots với đầy đủ thông tin và reasoning từ GPT
        """
        if constraints is None:
            constraints = {}
        
        # 1. Lấy dữ liệu
        print("Đang lấy dữ liệu từ database...")
        all_availabilities = self.get_all_user_availability()
        self.get_booking_history()  # Load history
        
        # 2. Build availability grid
        print("Đang xây dựng lưới availability...")
        grid = self.build_availability_grid(all_availabilities, days_ahead)
        
        # 3. Tìm tất cả candidate slots
        print("Đang tìm kiếm slots khả thi...")
        candidate_slots = []
        now = datetime.now()
        min_start_time = now + timedelta(hours=2)  # Tối thiểu 2 tiếng sau thời điểm hiện tại
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(days_ahead):
            current_date = today + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            
            for hour in range(WORKING_HOURS['start'], WORKING_HOURS['end']):
                slot_start = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                slot_end = slot_start + timedelta(minutes=duration_minutes)
                
                # Bỏ qua nếu slot bắt đầu trước thời gian tối thiểu (hiện tại + 2 tiếng)
                if slot_start < min_start_time:
                    continue
                
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
                # Chấm điểm cơ bản
                basic_score = self.score_slot(
                    slot_start, duration_minutes, available_users, constraints, objective
                )
                
                
                candidate_slots.append({
                    'start_time': slot_start,
                    'end_time': slot_end,
                    'basic_score': basic_score,
                    'available_users': list(available_users),
                    'available_count': len(available_users),
                    'date': date_str,
                    'hour': hour,
                    'day_of_week': slot_start.weekday(),
                    'objective': objective
                })
        
        if not candidate_slots:
            print("Không tìm thấy slots khả thi nào!")
            return []
        
        print(f"Tìm thấy {len(candidate_slots)} slots khả thi")
        
        # 4. Sử dụng AI để phân tích (nếu enabled)
        # print("OK")
        sorted_slots = sorted(candidate_slots, key=lambda x: x['basic_score'], reverse=True)
        slots_to_analyze_count = min(len(sorted_slots), 10) 
        if use_gpt and slots_to_analyze_count > 0:
            print(f"Gửi {slots_to_analyze_count} slots tốt nhất cho AI phân tích...")
            
            # Chỉ lấy top candidates để gửi đi
            top_candidates_for_ai = sorted_slots[:slots_to_analyze_count]
            
            analyzed_slots = self.ask_gpt_to_analyze_slots(
                top_candidates_for_ai, constraints, objective
            )
            
            sorted_slots = sorted(analyzed_slots, key=lambda x: x.get('gpt_score', 0), reverse=True)
        
        # 5. Lấy top N
        top_slots = sorted_slots[:top_n]
        
        # 6. Enrich thông tin
        print(f"Đề xuất {len(top_slots)} slots tốt nhất!")
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
            List[Dict]: Slots đã được enrich với GPT reasoning
        """
        from app.models import User, Booking
        
        enriched = []
        for slot in slots:
            # Get user details - Dùng available_count gốc từ lúc tạo slot
            actual_available_count = slot.get('available_count', len(slot.get('available_users', [])))
            
            user_details = []
            for uid in slot['available_users']:
                user = User.query.get(uid)
                if user:
                    user_details.append({
                        'id': uid,
                        'username': user.username,
                        'club': user.club,
                        'is_mentor': user.is_admin
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
                'available_count': actual_available_count,
                'user_details': user_details,
                'mentor_count': sum(1 for u in user_details if u['is_mentor']),
                'gpt_score_rounded': round(slot.get('gpt_score', 0), 2),
                'ai_reasoning': slot.get('gpt_reasoning', 'No AI analysis available')
            })
        
        return enriched
    
    def get_busy_users_for_slot(self, slot_datetime: datetime, duration_minutes: int) -> Dict:
        """
        Lấy danh sách người bận và rảnh cho một khung giờ cụ thể
        
        Args:
            slot_datetime: Thời gian bắt đầu slot
            duration_minutes: Độ dài meeting (phút)
            
        Returns:
            Dict: {
                'available_users': [{'id', 'username', 'club', 'is_mentor', 'attendance_rate'}],
                'busy_users': [{'id', 'username', 'club', 'is_mentor', 'reason'}],
                'total_users': int,
                'available_count': int,
                'busy_count': int
            }
        """
        from app.models import User, UserAvailability
        
        # Lấy tất cả users
        all_users = User.query.all()
        all_user_ids = {u.id for u in all_users}
        
        # Build availability grid cho khoảng thời gian này
        availabilities = self.get_all_user_availability()
        grid = self.build_availability_grid(availabilities, days_ahead=30)
        
        # Lấy available users cho slot
        slot_end = slot_datetime + timedelta(minutes=duration_minutes)
        available_user_ids = self._get_available_users_for_slot(grid, slot_datetime, slot_end)
        
        # Tính busy users
        busy_user_ids = all_user_ids - available_user_ids
        
        # Get detailed info cho available users
        available_users = []
        for uid in available_user_ids:
            user = User.query.get(uid)
            if user:
                available_users.append({
                    'id': uid,
                    'username': user.username,
                    'email': user.email,
                    'club': user.club,
                    'is_mentor': user.is_admin
                })
        
        # Get detailed info cho busy users
        busy_users = []
        for uid in busy_user_ids:
            user = User.query.get(uid)
            if user:
                # Tìm lý do bận
                reason = self._get_busy_reason(uid, slot_datetime, slot_end, availabilities)
                busy_users.append({
                    'id': uid,
                    'username': user.username,
                    'email': user.email,
                    'club': user.club,
                    'is_mentor': user.is_admin,
                    'reason': reason
                })
        
        return {
            'slot_start': slot_datetime.strftime('%Y-%m-%d %H:%M'),
            'slot_end': slot_end.strftime('%H:%M'),
            'duration_minutes': duration_minutes,
            'available_users': sorted(available_users, key=lambda x: x['username']),
            'busy_users': sorted(busy_users, key=lambda x: x['username']),
            'total_users': len(all_user_ids),
            'available_count': len(available_user_ids),
            'busy_count': len(busy_user_ids)
        }
    
    def _get_busy_reason(self, user_id: int, start_time: datetime, 
                        end_time: datetime, availabilities: List) -> str:
        """
        Tìm lý do tại sao user bận trong khung giờ này
        
        Args:
            user_id: ID của user
            start_time: Thời gian bắt đầu
            end_time: Thời gian kết thúc
            availabilities: List UserAvailability
            
        Returns:
            str: Lý do bận (ví dụ: "Đã đánh dấu bận 14:00-17:00")
        """
        day_of_week = start_time.weekday()
        start_hour = start_time.hour
        end_hour = end_time.hour
        
        # Tìm availability record của user trong khung giờ này
        for av in availabilities:
            if av.user_id == user_id and av.day_of_week == day_of_week and av.is_busy:
                # Check overlap
                if not (av.end_hour <= start_hour or av.start_hour >= end_hour):
                    if av.recurring:
                        return f"Đã đánh dấu bận {av.start_hour}:00-{av.end_hour}:00 (định kỳ)"
                    else:
                        return f"Đã đánh dấu bận {av.start_hour}:00-{av.end_hour}:00"
        
        return "Không rảnh trong khung giờ này"


# HELPER FUNCTIONS

def create_agent(db_session=None, api_key=None, model=None):
    """
    Factory function để tạo agent instance với OpenAI
    
    Args:
        db_session: SQLAlchemy session (optional, sẽ dùng current nếu None)
        api_key: OpenAI API key (optional, sẽ lấy từ config nếu None)
        model: Model name (optional, default gpt-4o-mini)
        
    Returns:
        MeetingSchedulerAgent: Agent instance powered by OpenAI
    """
    if db_session is None:
        from app.models import db
        db_session = db.session
    
    return MeetingSchedulerAgent(db_session, api_key=api_key, model=model)
