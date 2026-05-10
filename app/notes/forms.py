from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, Optional

class NoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    content = TextAreaField('Content', validators=[Optional()])
    trip_id = SelectField('Trip', coerce=int, validators=[Optional()])
    note_type = SelectField('Category', choices=[
        ('General', 'General'),
        ('Hotel', 'Hotel'),
        ('Transport', 'Transport'),
        ('Food', 'Food'),
        ('Emergency', 'Emergency'),
        ('Shopping', 'Shopping'),
        ('Reminder', 'Reminder')
    ], validators=[Optional()])
    reminder_date = DateField('Reminder Date', validators=[Optional()])
    is_pinned = BooleanField('Pin this note', validators=[Optional()])
