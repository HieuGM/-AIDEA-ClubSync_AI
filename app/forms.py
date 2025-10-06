from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')

class RegistrationForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    club = SelectField('CLB', choices=[('Pro', 'Pro'), ('Multi', 'Multi'), ('GCC', 'GCC')], validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Nhập lại mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email đã được sử dụng. Vui lòng chọn email khác.')

class BookingForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Mô tả')
    room_id = SelectField('Phòng', coerce=int, validators=[DataRequired()])
    start_time = DateTimeLocalField('Thời gian bắt đầu', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    end_time = DateTimeLocalField('Thời gian kết thúc', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Đặt phòng')
    
    def validate_end_time(self, end_time):
        if end_time.data <= self.start_time.data:
            raise ValidationError('Thời gian kết thúc phải sau thời gian bắt đầu.')