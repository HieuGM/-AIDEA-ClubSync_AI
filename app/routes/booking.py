from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Booking, Room, db
from app.forms import BookingForm
from datetime import datetime

bp = Blueprint('booking', __name__)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = BookingForm()
    form.room_id.choices = [(r.id, f"{r.name} ({r.capacity} người)") for r in Room.query.all()]
    
    if form.validate_on_submit():
        # Check for conflicts
        existing_booking = Booking.query.filter(
            Booking.room_id == form.room_id.data,
            Booking.start_time < form.end_time.data,
            Booking.end_time > form.start_time.data,
            Booking.status == 'confirmed'
        ).first()
        
        if existing_booking:
            flash('Phòng đã được đặt trong thời gian này. Vui lòng chọn thời gian khác.', 'danger')
        else:
            booking = Booking(
                title=form.title.data,
                description=form.description.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                user_id=current_user.id,
                room_id=form.room_id.data
            )
            db.session.add(booking)
            db.session.commit()
            flash('Đặt phòng thành công!', 'success')
            return redirect(url_for('main.calendar'))
    
    return render_template('booking/create.html', title='Đặt phòng', form=form)

@bp.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_time.desc()).all()
    now = datetime.utcnow()
    return render_template('booking/my_bookings.html', title='Lịch của tôi', bookings=bookings, now=now)

@bp.route('/cancel/<int:booking_id>')
@login_required
def cancel(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('Bạn không có quyền hủy lịch này.', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    if booking.start_time <= datetime.utcnow():
        flash('Không thể hủy lịch đã qua hoặc đang diễn ra.', 'warning')
        return redirect(url_for('booking.my_bookings'))
    
    booking.status = 'cancelled'
    db.session.commit()
    flash('Đã hủy lịch thành công.', 'success')
    return redirect(url_for('booking.my_bookings'))