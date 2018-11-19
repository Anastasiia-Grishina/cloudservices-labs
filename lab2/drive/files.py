from flask import Flask, flash, redirect, render_template, request, url_for
from drive import app
from drive.config import s3


@app.route('/bucket/<name>')
def bucket(name):
	
	response = s3.list_objects(Bucket=name)
	file_list = []
	for file in response['Contents']:
		file_list.append({'name': file['Key']})
    
	return render_template('bucket.html', files=file_list, bucket_name=name)


@app.route('/download/<bucket_name>/<file_name>')
def download_file(bucket_name, file_name):
	
	response = s3.download_file(bucket_name, file_name, file_name)
	flash('Successfully downloaded {}'.format(file_name))
    
	return redirect(url_for('bucket', name=bucket_name))


@app.route('/delete/<bucket_name>/<file_name>')
def delete_file(bucket_name, file_name):
	
	response = s3.delete_object(Bucket=bucket_name, Key=file_name)
	flash('Successfully deleted {}'.format(file_name))
    
	return redirect(url_for('bucket', name=bucket_name))