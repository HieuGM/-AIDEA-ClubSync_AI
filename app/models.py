from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    club = db.Column(db.String(10), nullable=False)  # Pro, Multi, GCC
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    bookings = db.relationship('Booking', backref='user', lazy=True, cascade='all, delete-orphan')
    availability = db.relationship('UserAvailability', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def __repr__(self):
        return f'<User {self.username}>'

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    bookings = db.relationship('Booking', backref='room', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Room {self.name}>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    status = db.Column(db.String(20), default='confirmed')  # confirmed, cancelled, pending
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_calendar_event(self):
        """Convert booking to FullCalendar format"""
        return {
            'id': self.id,
            'title': f"{self.title} - {self.room.name}",
            'start': self.start_time.isoformat(),
            'end': self.end_time.isoformat(),
            'backgroundColor': self._get_color_by_club(),
            'borderColor': self._get_color_by_club(),
            'extendedProps': {
                'user': self.user.username,
                'club': self.user.club,
                'room': self.room.name,
                'description': self.description,
                'status': self.status
            }
        }
    
    def _get_color_by_club(self):
        colors = {
            'Pro': '#FF6B6B',    # Red
            'Multi': '#4ECDC4',  # Teal
            'GCC': '#45B7D1'     # Blue
        }
        return colors.get(self.user.club, '#95A5A6')
    
    def __repr__(self):
        return f'<Booking {self.title}>'

class UserAvailability(db.Model):
    """Track user's busy/available time slots"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_hour = db.Column(db.Integer, nullable=False)   # 0-23
    end_hour = db.Column(db.Integer, nullable=False)     # 0-23
    is_busy = db.Column(db.Boolean, default=False)       # True=busy, False=available
    recurring = db.Column(db.Boolean, default=True)      # Weekly recurring
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserAvailability {self.user.username} - Day {self.day_of_week}>'