from flask import render_template
from drive import app
from drive.config import s3


@app.route('/bucket/<name>')
def bucket(name):
	
	response = s3.list_objects(Bucket=name)
	file_list = []
	for file in response['Contents']:
		file_list.append({'name': file['Key']})
    
	return render_template('bucket.html', files=file_list, bucket_name=name)

