from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Booking, Room, UserAvailability, User, db
from datetime import datetime, timedelta

bp = Blueprint('api', __name__)

@bp.route('/events')
@login_required
def get_events():
    """Get all bookings for calendar display"""
    bookings = Booking.query.filter_by(status='confirmed').all()
    events = [booking.to_calendar_event() for booking in bookings]
    return jsonify(events)

@bp.route('/my-events')
@login_required
def get_my_events():
    """Get current user's bookings for calendar display"""
    bookings = Booking.query.filter_by(user_id=current_user.id, status='confirmed').all()
    events = [booking.to_calendar_event() for booking in bookings]
    return jsonify(events)

@bp.route('/rooms')
@login_required
def get_rooms():
    """Get all rooms"""
    rooms = Room.query.all()
    return jsonify([{
        'id': room.id,
        'name': room.name,
        'capacity': room.capacity,
        'description': room.description
    } for room in rooms])

@bp.route('/check-availability')
@login_required
def check_availability():
    """Check room availability for given time range"""
    room_id = request.args.get('room_id', type=int)
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    
    if not all([room_id, start_str, end_str]):
        return jsonify({'error': 'Missing parameters'}), 400
    
    try:
        start_str_clean = start_str.replace('Z', '')
        end_str_clean = end_str.replace('Z', '')
        
        start_time = datetime.fromisoformat(start_str_clean)
        end_time = datetime.fromisoformat(end_str_clean)
        
        if start_time.tzinfo is not None:
            start_time = start_time.replace(tzinfo=None)
        if end_time.tzinfo is not None:
            end_time = end_time.replace(tzinfo=None)
            
    except ValueError as e:
        return jsonify({'error': f'Invalid datetime format: {str(e)}'}), 400
    
    room = Room.query.get(room_id)
    if not room:
        return jsonify({'error': f'Room with ID {room_id} not found'}), 404
    
    conflicts = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.start_time < end_time,
        Booking.end_time > start_time,
        Booking.status == 'confirmed'
    ).all()

    
    return jsonify({
        'available': len(conflicts) == 0,
        'conflicts': [booking.to_calendar_event() for booking in conflicts],
        'room_name': room.name 
    })

@bp.route('/availability', methods=['GET', 'POST'])
@login_required
def user_availability():
    """Manage user availability/busy times"""
    if request.method == 'GET':
        availability = UserAvailability.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': av.id,
            'day_of_week': av.day_of_week,
            'start_hour': av.start_hour,
            'end_hour': av.end_hour,
            'is_busy': av.is_busy,
            'recurring': av.recurring
        } for av in availability])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        UserAvailability.query.filter_by(user_id=current_user.id).delete()

        for entry in data.get('availability', []):
            av = UserAvailability(
                user_id=current_user.id,
                day_of_week=entry['day_of_week'],
                start_hour=entry['start_hour'],
                end_hour=entry['end_hour'],
                is_busy=entry.get('is_busy', False),
                recurring=entry.get('recurring', True)
            )
            db.session.add(av)
        
        db.session.commit()
        return jsonify({'success': True})

@bp.route('/stats')
@login_required
def get_stats():
    from sqlalchemy import func
    club_stats = db.session.query(
        User.club,
        func.count(Booking.id)
    ).join(User, Booking.user_id == User.id).filter(
        Booking.status == 'confirmed'
    ).group_by(User.club).all()
    
    room_stats = db.session.query(
        Room.name,
        func.count(Booking.id)
    ).join(Booking).filter(Booking.status == 'confirmed').group_by(Room.name).all()
    
    return jsonify({
        'club_bookings': dict(club_stats),
        'room_utilization': dict(room_stats)
    })