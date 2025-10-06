from flask import Flask
from flask_login import LoginManager
from app.models import db, User

def create_app(config_class=None):
    app = Flask(__name__)
    
    if config_class is None:
        from config import Config
        config_class = Config
    
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.booking import bp as booking_bp
    app.register_blueprint(booking_bp, url_prefix='/booking')
    
    from app.routes.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Initialize default rooms if they don't exist
        from app.models import Room
        if Room.query.count() == 0:
            large_room = Room(name='Phòng Lớn', capacity=30, description='Phòng họp lớn cho 30 người')
            small_room = Room(name='Phòng Nhỏ', capacity=15, description='Phòng họp nhỏ cho 15 người')
            db.session.add(large_room)
            db.session.add(small_room)
            db.session.commit()
    
    return app