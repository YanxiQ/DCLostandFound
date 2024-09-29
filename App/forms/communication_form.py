from flask_wtf import FlaskForm
from wtforms.fields.simple import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CommunicationForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')