from flask import Flask, flash, redirect, render_template, request, url_for, abort, Markup, session
from maestro import app
from maestro.config import switch_regions
from werkzeug.utils import secure_filename
import boto3


@app.route('/buckets-list/<region_name>', methods=['GET', 'POST'])
def buckets_list(region_name):

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
			bucket_location = s3.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']

			if region_name.lower() == 'global' or region_name == bucket_location:
				bucket_list.append({'name': bucket['Name'], 'bucket_location': bucket_location})

	return render_template('buckets-list.html', regions=region_list, buckets=bucket_list, region_name=region_name)


@app.route('/delete/<region_name>/<bucket_name>')
def delete_bucket(region_name, bucket_name):

	s3 = boto3.client('s3')
	bucket_location = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
	switch_regions(bucket_location)

	local_resource = boto3.resource('s3', region_name=session['region'])

	bucket = local_resource.Bucket(bucket_name)
	for key in bucket.objects.all():
		key.delete()
	bucket.delete()
	
	flash(Markup('Successfully deleted <b>{}</b>'.format(bucket_name)))

	return redirect(url_for('buckets_list', region_name=region_name))


@app.route('/create-bucket', methods=['GET', 'POST'])
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
		local_client = boto3.client('s3', region_name=session['region'])
		try:
			response = local_client.create_bucket(Bucket=bucket_name, 
								CreateBucketConfiguration={'LocationConstraint': region_name})
			flash(Markup('Successfully created <b>{}</b> in region <b>{}</b>'.format(bucket_name, region_name)))
		except Exception as e:
  			flash(Markup(e.args[0]))
   
		return redirect(url_for('buckets_list', region_name='global'))
