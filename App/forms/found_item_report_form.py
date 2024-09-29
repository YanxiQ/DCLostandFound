from datetime import date

from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import StringField, TextAreaField, FileField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


def validate_date_found(form, field):
    if field.data > date.today():
        raise ValidationError('The date cannot be later than today.')
class FoundItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=200)])
    category = SelectField('Category', choices=[
        ('Water Bottle', 'Water Bottle'),
        ('PE Kit', 'PE Kit'),
        ('Clothing', 'Clothing'),
        ('Lunch Box', 'Lunch Box'),
        ('Shoes', 'Shoes'),
        ('Accessories', 'Accessories'),
        ('Stationery','Stationery'),
        ('Book','Book'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    brand = StringField('Brand', validators=[Length(max=50)])
    colour = StringField('Primary Colour', validators=[Length(max=50)])
    additional_info = TextAreaField('Additional Info', validators=[Length(max=500)])
    date_found = DateField('Date Found', validators=[DataRequired(), validate_date_found], format='%Y-%m-%d')
    location_found = StringField('Location Found', validators=[DataRequired()])
    images = MultipleFileField('Image', validators=[DataRequired()])
    submit = SubmitField('Report Found Item')