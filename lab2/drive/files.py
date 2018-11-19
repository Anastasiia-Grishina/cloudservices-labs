from flask import Flask, flash, redirect, render_template, request, url_for, abort, Markup
from drive import app
from drive.config import s3
from drive.forms import UploadForm
from werkzeug.utils import secure_filename
from time import time


@app.route('/bucket/<name>', methods=['GET', 'POST'])
def bucket(name):


	form = UploadForm()

	if request.method == 'POST':

		f = form.file.data
		filename = secure_filename(f.filename)

		t1 = time()

		response = s3.upload_fileobj(f, name, filename)

		t2 = time()
		dt = t2 - t1


		flash(Markup('Successfully uploaded <b>{}</b> (<i>{} seconds</i>)'.format(filename, dt)))

		return redirect(url_for('bucket', name=name))


	response = s3.list_objects(Bucket=name)
	file_list = []
	for file in response['Contents']:
		file_list.append({'name': file['Key']})

	return render_template('bucket.html', files=file_list, bucket_name=name, form=form)


@app.route('/download/<bucket_name>/<file_name>')
def download_file(bucket_name, file_name):
	
	t1 = time()

	response = s3.download_file(bucket_name, file_name, file_name)

	t2 = time()

	dt = t2 - t1

	flash(Markup('Successfully downloaded <b>{}</b> (<i>{} seconds</i>)'.format(file_name, dt)))
    
	return redirect(url_for('bucket', name=bucket_name))


@app.route('/delete/<bucket_name>/<file_name>')
def delete_file(bucket_name, file_name):
	

	t1 = time()

	response = s3.delete_object(Bucket=bucket_name, Key=file_name)

	t2 = time()
	dt = t2 - t1

	flash(Markup('Successfully deleted <b>{}</b> (<i>{} seconds</i>)'.format(file_name, dt)))
    
	return redirect(url_for('bucket', name=bucket_name))
