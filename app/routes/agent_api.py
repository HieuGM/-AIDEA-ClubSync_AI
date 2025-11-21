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
            # Calculate duration from start and end time
            slot_duration = int((slot['end_time'] - slot['start_time']).total_seconds() / 60)
            
            serializable_slot = {
                'start_time': slot['start_time'].isoformat(),
                'end_time': slot['end_time'].isoformat(),
                'start_time_str': slot['start_time_str'],
                'end_time_str': slot['end_time_str'],
                'day_name': slot['day_name'],
                'duration_minutes': slot_duration,
                'score': slot.get('gpt_score_rounded', 0),
                'available_count': slot['available_count'],
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


@bp.route('/busy-users', methods=['POST'])
@login_required
def get_busy_users():
    """
    API để xem ai rảnh và ai bận cho một khung giờ cụ thể
    Request JSON:
    {
        "slot_datetime": "2025-11-13T14:00:00",
        "duration_minutes": 60
    }
    
    Response:
    {
        "success": true,
        "data": {
            "slot_start": "2025-11-13 14:00",
            "slot_end": "15:00",
            "duration_minutes": 60,
            "available_users": [...],
            "busy_users": [...],
            "total_users": 20,
            "available_count": 12,
            "busy_count": 8
        }
    }
    """
    try:
        data = request.get_json()
        
        slot_datetime_str = data.get('slot_datetime')
        duration_minutes = data.get('duration_minutes', 60)
        
        if not slot_datetime_str:
            return jsonify({
                'success': False,
                'error': 'Missing slot_datetime'
            }), 400
        
        # Parse datetime
        try:
            slot_datetime = datetime.fromisoformat(slot_datetime_str.replace('Z', ''))
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid datetime format. Use ISO format: YYYY-MM-DDTHH:MM:SS'
            }), 400
        
        # Get busy/available users
        agent = create_agent(db.session)
        result = agent.get_busy_users_for_slot(slot_datetime, duration_minutes)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
