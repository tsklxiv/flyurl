from flask_wtf import FlaskForm
from wtforms import URLField, SubmitField, StringField
from wtforms.validators import URL, DataRequired

class URLShortenerForm(FlaskForm):
    url = URLField("Your long URL:", validators=[URL(), DataRequired()])
    custom_key = StringField("Custom key:")
    submit = SubmitField("Fly!")
