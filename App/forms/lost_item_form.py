from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, FileField
from wtforms.validators import DataRequired, ValidationError


def validate_date_found(form, field):
    if field.data > date.today():
        raise ValidationError('The date cannot be later than today.')
class LostItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Water Bottle', 'Water Bottle'),
        ('PE Kit', 'PE Kit'),
        ('Clothing', 'Clothing'),
        ('Lunch Box', 'Lunch Box'),
        ('Shoes', 'Shoes'),
        ('Accessories', 'Accessories'),
        ('Stationery', 'Stationery'),
        ('Book', 'Book'),
        ('Other', 'Other')], validators=[DataRequired()])
    brand = StringField('Brand')
    colour = StringField('Primary Colour')
    additional_info = TextAreaField('Additional Info')
    location_lost = StringField('Location Lost', validators=[DataRequired()])
    date_lost = DateField('Date Lost', validators=[DataRequired(), validate_date_found])
    images = FileField('Upload Images', render_kw={'multiple': True})