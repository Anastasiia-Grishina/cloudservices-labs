from flask import Flask, flash, redirect, render_template, request, url_for, abort, Markup, session
from drive import app
from drive.config import switch_regions
from drive.forms import UploadForm
from werkzeug.utils import secure_filename
from time import time
import boto3
import sys


@app.route('/bucket/<name>', methods=['GET', 'POST'])
def bucket(name):
	form = UploadForm()

	region_name = request.args['region_name']

	switch_regions(region_name)
	local_client = boto3.client('s3', region_name=session['region'])

	response = local_client.list_objects(Bucket=name)
	file_list = []
	if 'Contents' in response:
		for file in response['Contents']:
			file_list.append({'name': file['Key']})

	return render_template('bucket.html', files=file_list, bucket_name=name, form=form)

@app.route('/upload-file/<bucket_name>', methods=['POST'])
def upload_file(bucket_name):
	local_client = boto3.client('s3', region_name=session['region'])

	form = UploadForm()
	f = form.file.data
	filename = secure_filename(f.filename)

	t1 = time()

	response = local_client.upload_fileobj(f, bucket_name, filename)

	t2 = time()
	dt = t2 - t1

	flash(Markup('Successfully uploaded <b>{}</b> (<i>{} seconds</i>)'.format(filename, dt)))

	return redirect(url_for('bucket', name=bucket_name, region_name=session['region']))


@app.route('/download/<bucket_name>/<file_name>')
def download_file(bucket_name, file_name):
	
	local_client = boto3.client('s3', region_name=session['region'])

	t1 = time()

	response = local_client.download_file(bucket_name, file_name, file_name)

	t2 = time()

	dt = t2 - t1

	flash(Markup('Successfully downloaded <b>{}</b> (<i>{} seconds</i>)'.format(file_name, dt)))
    
	return redirect(url_for('bucket', name=bucket_name, region_name=session['region']))


@app.route('/delete-file/<bucket_name>/<file_name>')
def delete_file(bucket_name, file_name):
	local_client = boto3.client('s3', region_name=session['region'])

	t1 = time()

	response = local_client.delete_object(Bucket=bucket_name, Key=file_name)

	t2 = time()
	dt = t2 - t1

	flash(Markup('Successfully deleted <b>{}</b> (<i>{} seconds</i>)'.format(file_name, dt)))
    
	return redirect(url_for('bucket', name=bucket_name, region_name=session['region']))
