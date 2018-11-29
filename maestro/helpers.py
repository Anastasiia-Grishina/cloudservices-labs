from flask import session
import libcloud.security
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
		print(access_id, access_key, '\n\n\n')

	return access_id, access_key

#TODO remove this and set session['current_region'] in all use cases
# region = 'eu-west-1'
images 			= None
sizes 			= None

images_choice = {'eu-west-1': 
				[('ami-09693313102a30b2c',
					'Amazon Linux 2 AMI (HVM), SSD Volume Type (64-bit x86)'
					), 
				('ami-0b97e17c772f052e6', 
					'Amazon Linux 2 AMI (HVM), SSD Volume Type (64-bit Arm)'
					),
				('ami-031a3db8bacbcdc20',
					'Amazon Linux AMI 2018.03.0 (HVM), SSD Volume Type'
					), 
				('ami-050889503ddaec473',
					'SUSE Linux Enterprise Server 15 (HVM), SSD Volume Type'
					),
				('ami-0e12cbde3e77cbb98',
					'Red Hat Enterprise Linux 7.6 (HVM), SSD Volume Type (64-bit x86)'
					),
				('ami-0b5171a7b859ff1b4', 
					'Red Hat Enterprise Linux 7.6 (HVM), SSD Volume Type (64-bit Arm)'
					),
				('ami-00035f41c82244dab', 
					'Ubuntu Server 18.04 LTS (HVM), SSD Volume Type (64-bit x86)'
					),
				('ami-047d41821c231284a', 
					'Ubuntu Server 18.04 LTS (HVM), SSD Volume Type (64-bit Arm)'
					),
				('ami-09f0b8b3e41191524', 
					'Ubuntu Server 16.04 LTS (HVM), SSD Volume Type (64-bit x86)'
					),
				('ami-0be77ce7582188e55',
					'Ubuntu Server 16.04 LTS (HVM), SSD Volume Type (64-bit Arm)'
					),
				('ami-0d138b26f46625e2f',
					'Microsoft Windows Server 2016 Base'
					),
				('ami-018d33b93a15e38d8',
					'Microsoft Windows Server 2016 Base with Containers'
					)
				]
				}

def get_ec2_driver(region):
	libcloud.security.VERIFY_SSL_CERT = False
	cls = get_driver(Provider.EC2)
	access_id, access_key = get_credentials()
	driver = cls(access_id, access_key, region=region)
	return driver

def get_ec2_images_list():
	global images
	if images is None:
		driver = get_ec2_driver(get_current_region())
		images = driver.list_images()
		images = [image for image in images if image.id[:3]=='ami' and image.name != None]
	return images

def get_ec2_sizes_list():
	global sizes
	if sizes is None:
		driver = get_ec2_driver(get_current_region())
		sizes = driver.list_sizes()
	return sizes