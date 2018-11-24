from flask import Flask, flash, redirect, render_template, request, url_for, abort, Markup
from drive import app
from drive.config import s3, ec2
from werkzeug.utils import secure_filename


@app.route('/buckets-list/<region_name>', methods=['GET', 'POST'])
def buckets_list(region_name):

	response_regions = ec2.describe_regions()
	region_list = []
	region_list.append({'name': 'global'})
	for region in response_regions['Regions']:
		region_list.append({'name': region['RegionName']})
	
	response_buckets = s3.list_buckets()
	bucket_list = []

	buckets_to_escape = ['m7024e-nasman-lab2-3', 'malihatest', 'malihatest-2', 'merian-test-eu-west']
	for bucket in response_buckets['Buckets']:
		try:
			bucket_location = s3.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']

			if region_name.lower() == 'global' or region_name == bucket_location:
				bucket_list.append({'name': bucket['Name']})
		except:
			pass

	return render_template('buckets-list.html', regions=region_list, buckets=bucket_list, region_name=region_name)


@app.route('/delete/<region_name>/<bucket_name>')
def delete_bucket(region_name, bucket_name):
	response = s3.delete_bucket(Bucket=bucket_name)

	flash(Markup('Successfully deleted <b>{}</b>'.format(bucket_name)))
    
	return redirect(url_for('buckets_list', region_name=region_name))


@app.route('/create-bucket', methods=['GET', 'POST'])
def create_bucket():
	if request.method == 'GET':
		response_regions = ec2.describe_regions()
		region_list = []
		for region in response_regions['Regions']:
			region_list.append({'name': region['RegionName']})
		return render_template('create-bucket.html', regions=region_list)
	
	elif request.method == 'POST':

		bucket_name = request.form['bucket-name']
		region_name = request.form['region-name']

		response = s3.create_bucket(Bucket=bucket_name, 
								CreateBucketConfiguration={'LocationConstraint': region_name})

		flash(Markup('Successfully created <b>{}</b> in region <b>{}</b>'.format(bucket_name, region_name)))
    
		return redirect(url_for('buckets_list', region_name='global'))
