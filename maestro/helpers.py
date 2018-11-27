from flask import session


def switch_regions(region_name):
	session['region'] = region_name


def get_credentials():

	access_key = None
	access_id  = None

	with open('credentials.txt') as f:
		access_id = f.readline().strip('\n')
		access_key = f.readline().strip('\n')

	return access_id, access_key