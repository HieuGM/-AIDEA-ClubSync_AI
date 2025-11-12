"""
API Routes cho AI Agent - Intelligent Meeting Scheduler
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.ai.agent import create_agent
from app.models import db
from datetime import datetime

bp = Blueprint('agent', __name__)


@bp.route('/suggest-slots', methods=['POST'])
@login_required
def suggest_slots():
    """
    API để tìm và đề xuất slots tối ưu
    
    Request JSON:
    {
        "duration_minutes": 60,
        "constraints": {
            "required_members": [1, 2, 3],
            "required_mentors": [4],
            "min_attendees": 5,
            "club_filter": "Pro"
        },
        "objective": "balanced",
        "days_ahead": 14,
        "top_n": 3
    }
    
    Response:
    {
        "success": true,
        "slots": [...],
        "message": "Found 3 optimal slots"
    }
    """
    try:
        data = request.get_json()
        
        # Parse parameters
        duration_minutes = data.get('duration_minutes', 60)
        constraints = data.get('constraints', {})
        objective = data.get('objective', 'balanced')
        days_ahead = data.get('days_ahead', 14)
        top_n = data.get('top_n', 3)
        
        # Validate objective
        valid_objectives = ['max_attendance', 'max_probability', 'fairness', 
                           'mentor_priority', 'balanced']
        if objective not in valid_objectives:
            return jsonify({
                'success': False,
                'error': f'Invalid objective. Must be one of: {valid_objectives}'
            }), 400
        
        # Create agent and find slots
        agent = create_agent(db.session)
        slots = agent.find_optimal_slots(
            duration_minutes=duration_minutes,
            constraints=constraints,
            objective=objective,
            days_ahead=days_ahead,
            top_n=top_n
        )
        
        # Convert datetime objects to strings for JSON
        serializable_slots = []
        for slot in slots:
            serializable_slot = {
                'start_time': slot['start_time'].isoformat(),
                'end_time': slot['end_time'].isoformat(),
                'start_time_str': slot['start_time_str'],
                'end_time_str': slot['end_time_str'],
                'day_name': slot['day_name'],
                'score': slot.get('gpt_score_rounded', 0),
                'available_count': slot['available_count'],
                'expected_attendance': slot.get('expected_attendance_rounded', 0),
                'avg_attendance_rate': slot.get('avg_attendance_rate', 0),
                'mentor_count': slot['mentor_count'],
                'objective': slot.get('objective', 'balanced'),
                'ai_reasoning': slot.get('ai_reasoning', ''),
                'user_details': slot['user_details']
            }
            serializable_slots.append(serializable_slot)
        
        return jsonify({
            'success': True,
            'slots': serializable_slots,
            'message': f'Found {len(serializable_slots)} optimal slots'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/create-poll', methods=['POST'])
@login_required
def create_poll():
    """
    API để tạo poll "1 chạm" với 3 slots tốt nhất
    
    Request JSON:
    {
        "meeting_title": "Weekly Standup",
        "duration_minutes": 60,
        "constraints": {
            "required_members": [1, 2],
            "min_attendees": 5
        },
        "objectives": ["max_attendance", "balanced", "mentor_priority"]
    }
    
    Response:
    {
        "success": true,
        "poll": {
            "title": "Weekly Standup",
            "options": [...],
            "recommendation": "..."
        }
    }
    """
    try:
        data = request.get_json()
        
        meeting_title = data.get('meeting_title', 'Team Meeting')
        duration_minutes = data.get('duration_minutes', 60)
        constraints = data.get('constraints', {})
        objectives = data.get('objectives', None)
        
        # Create agent and generate poll
        agent = create_agent(db.session)
        poll_data = agent.create_smart_poll(
            meeting_title=meeting_title,
            duration_minutes=duration_minutes,
            constraints=constraints,
            objectives=objectives
        )
        
        # Serialize datetime objects
        serializable_poll = {
            'title': poll_data['title'],
            'duration_minutes': poll_data['duration_minutes'],
            'created_at': poll_data['created_at'],
            'recommendation': poll_data['recommendation'],
            'options': []
        }
        
        for option in poll_data['options']:
            serializable_option = {
                'start_time': option['start_time'].isoformat(),
                'end_time': option['end_time'].isoformat(),
                'start_time_str': option['start_time_str'],
                'end_time_str': option['end_time_str'],
                'day_name': option['day_name'],
                'score': option.get('gpt_score_rounded', 0),
                'available_count': option['available_count'],
                'expected_attendance': option.get('expected_attendance_rounded', 0),
                'avg_attendance_rate': option.get('avg_attendance_rate', 0),
                'mentor_count': option['mentor_count'],
                'ai_reasoning': option.get('ai_reasoning', ''),
                'user_details': option['user_details']
            }
            serializable_poll['options'].append(serializable_option)
        
        return jsonify({
            'success': True,
            'poll': serializable_poll,
            'message': 'Poll created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/user-patterns/<int:user_id>', methods=['GET'])
@login_required
def get_user_patterns(user_id):
    """
    API để xem patterns học được của một user
    
    Response:
    {
        "success": true,
        "patterns": {
            "total_bookings": 15,
            "preferred_hours": {...},
            "time_slot_preference": "afternoon",
            "attendance_rate": 0.85
        }
    }
    """
    try:
        # Only admins or the user themselves can view patterns
        if not current_user.is_admin and current_user.id != user_id:
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403
        
        agent = create_agent(db.session)
        agent.get_booking_history()  # Load history first
        patterns = agent.learn_user_patterns(user_id)
        
        return jsonify({
            'success': True,
            'patterns': patterns
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/attendance-probability', methods=['POST'])
@login_required
def get_attendance_probability():
    """
    API để tính xác suất tham dự của users tại một slot cụ thể
    
    Request JSON:
    {
        "user_ids": [1, 2, 3, 4],
        "slot_datetime": "2025-10-27T14:00:00"
    }
    
    Response:
    {
        "success": true,
        "probabilities": {
            "1": 0.85,
            "2": 0.72,
            ...
        },
        "expected_count": 3.2
    }
    """
    try:
        data = request.get_json()
        
        user_ids = data.get('user_ids', [])
        slot_datetime_str = data.get('slot_datetime')
        
        if not user_ids or not slot_datetime_str:
            return jsonify({
                'success': False,
                'error': 'Missing user_ids or slot_datetime'
            }), 400
        
        # Parse datetime
        slot_datetime = datetime.fromisoformat(slot_datetime_str.replace('Z', ''))
        
        # Calculate probabilities
        agent = create_agent(db.session)
        agent.get_booking_history()
        
        probabilities = {}
        for user_id in user_ids:
            prob = agent.estimate_attendance_probability(user_id, slot_datetime)
            probabilities[str(user_id)] = round(prob, 2)
        
        expected_count = sum(probabilities.values())
        
        return jsonify({
            'success': True,
            'probabilities': probabilities,
            'expected_count': round(expected_count, 1)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/analyze-constraints', methods=['POST'])
@login_required
def analyze_constraints():
    """
    API để phân tích xem constraints có khả thi không
    
    Request JSON:
    {
        "constraints": {
            "required_members": [1, 2, 3],
            "min_attendees": 10,
            "club_filter": "Pro"
        },
        "days_ahead": 14
    }
    
    Response:
    {
        "success": true,
        "feasible": true,
        "analysis": {
            "total_feasible_slots": 25,
            "best_score": 85.5,
            "recommendations": [...]
        }
    }
    """
    try:
        data = request.get_json()
        
        constraints = data.get('constraints', {})
        days_ahead = data.get('days_ahead', 14)
        
        agent = create_agent(db.session)
        slots = agent.find_optimal_slots(
            duration_minutes=60,
            constraints=constraints,
            objective='balanced',
            days_ahead=days_ahead,
            top_n=5
        )
        
        feasible = len(slots) > 0
        
        analysis = {
            'total_feasible_slots': len(slots),
            'best_score': slots[0].get('gpt_score_rounded', 0) if slots else 0,
            'recommendations': []
        }
        
        if not feasible:
            analysis['recommendations'].append(
                'No feasible slots found. Consider relaxing constraints.'
            )
        else:
            if len(slots) < 3:
                analysis['recommendations'].append(
                    'Limited options available. Consider extending days_ahead or relaxing constraints.'
                )
            
            best_slot = slots[0]
            if best_slot['available_count'] < constraints.get('min_attendees', 0):
                analysis['recommendations'].append(
                    f"Available count ({best_slot['available_count']}) "
                    f"may not meet minimum requirement ({constraints.get('min_attendees')})"
                )
        
        return jsonify({
            'success': True,
            'feasible': feasible,
            'analysis': analysis,
            'sample_slots': [
                {
                    'start_time_str': s['start_time_str'],
                    'score': s.get('gpt_score_rounded', 0),
                    'available_count': s['available_count']
                }
                for s in slots[:3]
            ]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for AI Agent"""
    try:
        agent = create_agent(db.session)
        user_count = len(agent.get_all_users())
        
        return jsonify({
            'status': 'healthy',
            'agent': 'MeetingSchedulerAgent',
            'total_users': user_count,
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
