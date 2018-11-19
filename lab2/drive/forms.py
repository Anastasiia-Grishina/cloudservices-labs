from flask_wtf import FlaskForm
from wtforms import HiddenField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired
import os

class UploadForm(FlaskForm):
    file = FileField()