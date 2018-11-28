from flask import Flask, flash, redirect, render_template, request, url_for, abort, Markup, session
from maestro import app
from maestro.helpers import switch_regions
from werkzeug.utils import secure_filename
from maestro.forms import UploadForm
from werkzeug.utils import secure_filename
from time import time
import boto3
import sys


@app.route('/storage/list-buckets/<region_name>', methods=['GET', 'POST'])
@app.route('/storage/list-buckets/')
def buckets_list(region_name=None):

	# safety
	if region_name is None:
		region_name = 'global'

	ec2 = boto3.client('ec2')
	response_regions = ec2.describe_regions()

	region_list = []
	region_list.append({'name': 'global'})
	for region in response_regions['Regions']:
		region_list.append({'name': region['RegionName']})
	
	s3 = boto3.client('s3')
	response_buckets = s3.list_buckets()
	bucket_list = []

	for bucket in response_buckets['Buckets']:
		try:
			bucket_location = s3.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']

			if region_name.lower() == 'global' or region_name == bucket_location:
				bucket_list.append({'name': bucket['Name'], 'bucket_location': bucket_location})
		except:
			print('{} is a ghost'.format(bucket['Name']), file=sys.stdout)

	return render_template('buckets-list.html', regions=region_list, buckets=bucket_list, region_name=region_name)


@app.route('/storage/delete-bucket/<region_name>/<bucket_name>')
def delete_bucket(region_name, bucket_name):

	s3 = boto3.client('s3')
	bucket_location = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
	switch_regions(bucket_location)

	local_resource = boto3.resource('s3', region_name=session['current_region'])


	# delete all objects in bucket first
	bucket = local_resource.Bucket(bucket_name)
	for key in bucket.objects.all():
		key.delete()
	bucket.delete()
	
	flash(Markup('Successfully deleted <b>{}</b>'.format(bucket_name)))

	return redirect(url_for('buckets_list', region_name=region_name))


@app.route('/storage/create-bucket', methods=['GET', 'POST'])
def create_bucket():

	ec2 = boto3.client('ec2')
	if request.method == 'GET':
		response_regions = ec2.describe_regions()
		region_list = []
		for region in response_regions['Regions']:
			region_list.append({'name': region['RegionName']})
		return render_template('create-bucket.html', regions=region_list)
	
	elif request.method == 'POST':

		bucket_name = request.form['bucket-name']
		region_name = request.form['region-name']

		switch_regions(region_name)
		local_client = boto3.client('s3', region_name=session['current_region'])
		try:
			response = local_client.create_bucket(Bucket=bucket_name, 
								CreateBucketConfiguration={'LocationConstraint': region_name})
			flash(Markup('Successfully created <b>{}</b> in region <b>{}</b>'.format(bucket_name, region_name)))
		except Exception as e:
  			flash(Markup(e.args[0]))
   
		return redirect(url_for('buckets_list', region_name='global'))




@app.route('/storage/list-files/<bucket_name>', methods=['GET', 'POST'])
def bucket(bucket_name):
	form = UploadForm()

	region_name = request.args['region_name']

	switch_regions(region_name)
	local_client = boto3.client('s3', region_name=session['current_region'])

	response = local_client.list_objects(Bucket=bucket_name)
	file_list = []
	if 'Contents' in response:
		for file in response['Contents']:
			file_list.append({'name': file['Key']})

	return render_template('bucket.html', files=file_list, bucket_name=bucket_name, form=form)

@app.route('/storage/upload-file/<bucket_name>', methods=['POST'])
def upload_file(bucket_name):
	local_client = boto3.client('s3', region_name=session['current_region'])

	form = UploadForm()
	f = form.file.data
	filename = secure_filename(f.filename)

	t1 = time()

	response = local_client.upload_fileobj(f, bucket_name, filename)

	t2 = time()
	dt = t2 - t1

	flash(Markup('Successfully uploaded <b>{}</b> (<i>{} seconds</i>)'.format(filename, dt)))

	return redirect(url_for('bucket', bucket_name=bucket_name, region_name=session['current_region']))


@app.route('/storage/download/<bucket_name>/<file_name>')
def download_file(bucket_name, file_name):
	
	local_client = boto3.client('s3', region_name=session['current_region'])

	t1 = time()

	response = local_client.download_file(bucket_name, file_name, file_name)

	t2 = time()

	dt = t2 - t1

	flash(Markup('Successfully downloaded <b>{}</b> (<i>{} seconds</i>)'.format(file_name, dt)))
    
	return redirect(url_for('bucket', bucket_name=bucket_name, region_name=session['current_region']))


@app.route('/storage/delete-file/<bucket_name>/<file_name>')
def delete_file(bucket_name, file_name):
	local_client = boto3.client('s3', region_name=session['current_region'])

	t1 = time()

	response = local_client.delete_object(Bucket=bucket_name, Key=file_name)

	t2 = time()
	dt = t2 - t1

	flash(Markup('Successfully deleted <b>{}</b> (<i>{} seconds</i>)'.format(file_name, dt)))
    
	return redirect(url_for('bucket', bucket_name=bucket_name, region_name=session['current_region']))
