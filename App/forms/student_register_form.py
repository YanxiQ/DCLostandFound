from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from ..models.user_model import User


def email_domain_validate(form, field):
    if not field.data.endswith('@dubaicollege.org'):
        raise ValidationError('Email must end with @dubaicollege.org, as only Dubai College students are permitted to register.')

def validate_password_strength(form, field):
    password = field.data
    if len(password) < 6:
        raise ValidationError('Your password must be at least 6 characters.')

def validate_student(form, field):
    student_id = field.data
    email = form.email.data
    if not student_id.isdigit() or student_id not in email:
        raise ValidationError('Student ID Invalid.')
class StudentRegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('DC Email', validators=[DataRequired(), Email(), email_domain_validate])
    password = PasswordField('Password', validators=[DataRequired(), validate_password_strength])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    phone = StringField('Phone Number', validators=[Length(max=50)])
    student_id = StringField('Student ID', validators=[DataRequired(), validate_student])
    submit = SubmitField('Register')

