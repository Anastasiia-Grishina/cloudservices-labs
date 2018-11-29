from flask import Flask, flash, redirect, render_template, request, url_for, abort, Markup, session
from maestro import app
from maestro.helpers import get_ec2_driver, get_credentials,\
	get_ec2_images_list, get_ec2_sizes_list, switch_regions, get_current_region
from maestro.helpers import images_choice
from maestro.forms import CreateNodeForm
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from datetime import datetime, timedelta
import boto3


@app.route('/compute/list-nodes')
def nodes_list():
	print(get_credentials())
	driver = get_ec2_driver(get_current_region())
	nodes = driver.list_nodes()

	return render_template('nodes-list.html', nodes = nodes)


# both display and handle form submit, then redirect to nodes_list
@app.route('/compute/create-node', methods=['GET', 'POST'])
def create_node():
	form = 	CreateNodeForm()
	if request.method == 'GET':
		region = get_current_region()
		driver = get_ec2_driver(region)

		# form.image.choices 			= images_choice[region]
		images_local  				= get_ec2_images_list()
		form.image.choices 			= [(image.id, image.name) for image in images_local[:20]]
		sizes_local					= get_ec2_sizes_list()
		form.size.choices 			= [(size.id, size.name) for size in sizes_local]
		form.key_pair.choices 		= [(key_pair.name, key_pair.name) for key_pair in driver.list_key_pairs()]
		form.key_pair.choices 		= [('None', 'None')] + form.key_pair.choices
		form.security_group.choices = [(sg.id, sg.name) for sg in driver.ex_get_security_groups()]
		form.security_group.choices = [('None', 'None')] + form.security_group.choices

		return render_template('create-node.html', form=form)
		
	elif request.method == 'POST':
		name 			= form.name.data
		image_id 		= form.image.data
		size_id			= form.size.data
		nodes_no_str	= form.nodes_no.data
		key_pair		= form.key_pair.data
		security_group  = form.security_group.data

		try:
			nodes_no = int(nodes_no_str)
		except:
  			flash(Markup('Please, provide a valid number of instances to create.'))
  			return redirect(url_for('create_node'))

		print('\n\n\nimage id', image_id)

		size = [s for s in get_ec2_sizes_list() if s.id == size_id][0]
		image = [im for im in get_ec2_images_list() if im.id == image_id][0]

		driver = get_ec2_driver(get_current_region())
		if ((key_pair != 'None') and (security_group != 'None')):
				print('both none')
				node = driver.create_node(name=name, image=image, size=size,\
					ex_mincount=nodes_no, ex_maxcount=nodes_no, ex_keyname=key_pair, \
					ex_security_group_ids=[security_group]
					)
		elif (key_pair != 'None' and security_group == 'None'):
			node = driver.create_node(name=name, image=image, size=size, \
					ex_mincount=nodes_no, ex_maxcount=nodes_no, ex_keyname=key_pair
					)
		elif (key_pair == 'None' and security_group != 'None'):
			node = driver.create_node(name=name, image=image, size=size, \
					ex_mincount=nodes_no, ex_maxcount=nodes_no, \
					ex_security_group_ids=[security_group]
					)
		else:
			node = driver.create_node(name=name, image=image, size=size, \
					ex_mincount=nodes_no, ex_maxcount=nodes_no)


		flash(Markup('Successfully created <b>{}</b> instance(s) <b>{}</b>'.format(nodes_no, name)))
		if (nodes_no == 1):
			return redirect(url_for('node_details', node_id=node.id))
		else:
			return redirect(url_for('node_details', node_id=node[0].id))

@app.route('/compute/stop-node/<node_id>')
def stop_node(node_id):
	# TODO select region from session

	driver = get_ec2_driver(get_current_region())
	node = driver.list_nodes(ex_node_ids=[node_id])[0]
	driver.ex_stop_node(node)
	
	flash(Markup('Stopping {}...'.format(node.name)))

	return redirect(url_for('node_details', node_id=node_id))


# redirect to node_details
@app.route('/compute/start-node/<node_id>')
def start_node(node_id):

	driver = get_ec2_driver(get_current_region())
	node = driver.list_nodes(ex_node_ids=[node_id])[0]
	driver.ex_start_node(node)
	flash(Markup('Starting {}...'.format(node.name)))

	return redirect(url_for('node_details', node_id=node_id))


# redirect to nodes_list
@app.route('/compute/terminate-node/<node_id>')
def terminate_node(node_id):

	driver = get_ec2_driver(get_current_region())

	# cls = get_driver(Provider.EC2)
	# access_id, access_key = get_credentials()
	# driver = cls(access_id, access_key, region='eu-west-1')
	node = driver.list_nodes(ex_node_ids=[node_id])[0]
	driver.destroy_node(node=node)

	flash(Markup('Terminating {}...'.format(node.name)))

	return redirect(url_for('node_details', node_id=node_id))

#  'id': 'i-0e552ea30107e8ac6',
# provide details + actions for nodes
@app.route('/compute/node-details/<node_id>')
def node_details(node_id):

	driver = get_ec2_driver(get_current_region())
	# check for error?
	node = driver.list_nodes(ex_node_ids=[node_id])[0]

	pretty_node = { 'id': node_id, 'name': node.name, 'state': node.extra['status'], 'type': node.extra['instance_type'], 'zone': node.extra['availability'], 'private_ips': node.private_ips, 'public_ips': node.public_ips, 'private_dns': node.extra['private_dns'], 'public_dns': node.extra['dns_name'], 'security_groups': node.extra['groups'], 'image_id': node.extra['image_id'], 'key': node.extra['key_name']}

	return render_template('node-details.html', node=pretty_node)


@app.route('/compute/node-stats/<node_id>')
def node_stats(node_id):

	driver = get_ec2_driver(get_current_region())

	# check for error?
	node = driver.list_nodes(ex_node_ids=[node_id])[0]

	pretty_node = { 'id': node_id, 'name': node.name }
	stats = { 'cpu': { }, 'network_in': { 'data': [], 'labels': [] }, 'network_out': { 'data': [], 'labels': [] }, 'disk_read': { 'data': [], 'labels': [] }, 'disk_write': { 'data': [], 'labels': [] } }

	metrics = ['CPUUtilization', 'NetworkIn', 'NetworkOut', 'DiskReadBytes', 'DiskWriteBytes']
	query = []

	for m in metrics:
		query.append({
			'Id': 'metric_'+m,
			'MetricStat': {
				'Metric': {
					'Namespace': 'AWS/EC2',
					'MetricName': m,
					'Dimensions': [
						{
							'Name': 'InstanceId',
							'Value': node_id
						},
					]
				},
				'Period': 60,
				'Stat': 'Average',
			}
		})

	cloudwatch = boto3.client('cloudwatch', region_name=session['current_region'])
	response = cloudwatch.get_metric_data(
		MetricDataQueries=query,
		StartTime=datetime.now() - timedelta(hours=2),
		EndTime=datetime.now(),
		ScanBy='TimestampAscending'
	)

	for metric in response['MetricDataResults']:
		index = metrics.index(metric['Label'])
		key = [*stats][index]

		stats[key]['data'] = metric['Values']
		stats[key]['labels'] = [ t.strftime('%d-%m-%Y %H:%M') for t in metric['Timestamps'] ]

	return render_template('node-stats.html', node=pretty_node, stats=stats)