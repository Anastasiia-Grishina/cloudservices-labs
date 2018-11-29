from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, SelectMultipleField, TextAreaField, TextField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired
import os

class UploadForm(FlaskForm):
    file = FileField()


class CreateNodeForm(FlaskForm):
	# image_id - AMI type
	# size_id  - type of instance, e.g. t2.micro

	image 	= SelectField(u'AMI', coerce=str)
	name	= TextField(u'Name')
	size	= SelectField(u'Instance type', coerce=str)


	nodes_no		= TextField(u'Number of instances to start')
	key_pair		= SelectField(u'Key pair', coerce=str)
	security_group	= SelectField(u'Security group', coerce=str)


	


