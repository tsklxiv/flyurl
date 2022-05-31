from flask_wtf import FlaskForm
from wtforms import URLField, SubmitField
from wtforms.validators import URL, DataRequired

class URLShortenerForm(FlaskForm):
    url = URLField("Your long URL:", validators=[URL(), DataRequired()])
    submit = SubmitField("Shorten!")
