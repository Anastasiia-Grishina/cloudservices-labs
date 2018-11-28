from flask import Flask, flash, redirect, render_template, request, url_for, abort, Markup, session
from maestro import app

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import boto3
from datetime import datetime, timedelta

from maestro.helpers import get_credentials

# @app.route('/compute/list-nodes')
def nodes_list():
	return render_template('index.html')


# # both display and handle form submit, then redirect to nodes_list
# @app.route('/compute/create-node', methods=['GET', 'POST'])
# def create_node(params?):
#	 return render_template('create-node.html')






# redirect to node_details
@app.route('/compute/stop-node/<node_id>')
def stop_node(node_id):
	# TODO select region from session
	cls = get_driver(Provider.EC2)
	access_id, access_key = get_credentials()
	driver = cls(access_id, access_key, region='eu-west-1')

	node = driver.list_nodes(ex_node_ids=[node_id])[0]
	driver.ex_stop_node(node)
	flash(Markup('Stopping {}...'.format(node.name)))

	return redirect(url_for('node_details', node_id=node_id))


# redirect to node_details
@app.route('/compute/start-node/<node_id>')
def start_node(node_id):
	# TODO select region from session
	cls = get_driver(Provider.EC2)
	access_id, access_key = get_credentials()
	driver = cls(access_id, access_key, region='eu-west-1')

	node = driver.list_nodes(ex_node_ids=[node_id])[0]
	driver.ex_start_node(node)
	flash(Markup('Starting {}...'.format(node.name)))

	return redirect(url_for('node_details', node_id=node_id))


# redirect to nodes_list
@app.route('/compute/terminate-node/<node_id>')
def terminate_node(node_id):
	# TODO select region from session
	cls = get_driver(Provider.EC2)
	access_id, access_key = get_credentials()
	driver = cls(access_id, access_key, region='eu-west-1')

	node = driver.list_nodes(ex_node_ids=[node_id])[0]
	driver.destroy_node(node=node)

	flash(Markup('Terminating {}...'.format(node.name)))


	return redirect(url_for('node_details', node_id=node_id))

#  'id': 'i-0e552ea30107e8ac6',
# provide details + actions for nodes
@app.route('/compute/node-details/<node_id>')
def node_details(node_id):

	# TODO select region from session
	cls = get_driver(Provider.EC2)
	access_id, access_key = get_credentials()
	driver = cls(access_id, access_key, region=session['current_region'])

	# check for error?
	node = driver.list_nodes(ex_node_ids=[node_id])[0]

	pretty_node = { 'id': node_id, 'name': node.name, 'state': node.extra['status'], 'type': node.extra['instance_type'], 'zone': node.extra['availability'], 'private_ips': node.private_ips, 'public_ips': node.public_ips, 'private_dns': node.extra['private_dns'], 'public_dns': node.extra['dns_name'], 'security_groups': node.extra['groups'], 'image_id': node.extra['image_id'], 'key': node.extra['key_name']}


	return render_template('node-details.html', node=pretty_node)



@app.route('/compute/node-stats/<node_id>')
def node_stats(node_id):

	# TODO select region from session
	cls = get_driver(Provider.EC2)
	access_id, access_key = get_credentials()
	driver = cls(access_id, access_key, region=session['current_region'])

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



