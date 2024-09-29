from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email

class UserProfileForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number')
    student_id = StringField('Student ID')
    profile_pic = FileField('Profile Picture')
    submit = SubmitField('Update Profile')