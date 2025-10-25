from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html', title='ClubSync.AI - Trang chủ')

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

@bp.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html', title='Lịch đặt phòng')

@bp.route('/availability')
@login_required
def availability():
    return render_template('availability.html', title='Quản lý thời gian')

@bp.route('/smart-scheduler')
@login_required
def smart_scheduler():
    return render_template('smart_scheduler.html', title='AI Smart Scheduler')