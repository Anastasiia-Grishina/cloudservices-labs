from flask import session
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

def switch_regions(region_name):
	session['region'] = region_name


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
	if images is None:
		cls = get_driver(Provider.EC2)
		access_id, access_key = get_credentials()
		driver = cls(access_id, access_key, region='eu-west-1')

		images = driver.list_images()
	return images

def get_ec2_sizes_list():
	if sizes is None:
		cls = get_driver(Provider.EC2)
		access_id, access_key = get_credentials()
		driver = cls(access_id, access_key, region='eu-west-1')

		sizes = driver.list_sizes()
	return sizes


