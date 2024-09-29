from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired


class FaqForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AnswerFaqForm(FlaskForm):
    answer = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField('Submit')
