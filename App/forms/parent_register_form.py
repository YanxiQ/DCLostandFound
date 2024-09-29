from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from ..models.user_model import User


def email_domain_validate(form, field):
    if not field.data.endswith('@dubaicollege.org'):
        raise ValidationError('The student email must end with @dubaicollege.org, as only Dubai College students are permitted to register.')

def child_account_exists(form, field):
    email = field.data
    student = User.query.filter_by(email=email, role='Student').first()
    if not student:
        raise ValidationError(f'There is no student account associated with the email {email}. Please let your child create an account first.')

def validate_password_strength(form, field):
    password = field.data
    if len(password) < 6:
        raise ValidationError('Your password must be at least 6 characters.')

class ParentRegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    child_email = StringField("Your Child's DC Email", validators=[DataRequired(), email_domain_validate, child_account_exists, EqualTo('child_email')])
    password = PasswordField('Password', validators=[DataRequired(), validate_password_strength])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    phone = StringField('Phone Number', validators=[Length(max=50)])
    submit = SubmitField('Register')

