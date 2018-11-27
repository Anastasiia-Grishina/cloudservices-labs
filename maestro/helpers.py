from flask import session
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from maestro import app
import boto3



def get_regions_list():
	ec2 = boto3.client('ec2')
	response_regions = ec2.describe_regions()

	regions_list = []
	for region in response_regions['Regions']:
		regions_list.append(region['RegionName'])

	return regions_list


def switch_regions(region_name):
	session['current_region'] = region_name

def get_current_region():
	if 'current_region' not in session:
		session['current_region'] = 'eu-west-1'
	return session['current_region']

app.jinja_env.globals.update(get_regions_list=get_regions_list)
app.jinja_env.globals.update(get_current_region=get_current_region)


def get_credentials():

	access_key = None
	access_id  = None

	with open('credentials.txt') as f:
		access_id = f.readline().strip('\n')
		access_key = f.readline().strip('\n')

	return access_id, access_key


# load images and sizes lists on startup 

images = None
sizes = None

def get_ec2_images_list():
	global images
	global current_region
	if images is None:
		cls = get_driver(Provider.EC2)
		access_id, access_key = get_credentials()
		driver = cls(access_id, access_key, region=current_region)

		images = driver.list_images()
	return images

def get_ec2_sizes_list():
	global current_region
	global sizes
	if sizes is None:
		cls = get_driver(Provider.EC2)
		access_id, access_key = get_credentials()
		driver = cls(access_id, access_key, region=current_region)

		sizes = driver.list_sizes()
	return sizes


