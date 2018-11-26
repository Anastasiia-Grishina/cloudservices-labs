from flask import session

def switch_regions(region_name):
	session['region'] = region_name