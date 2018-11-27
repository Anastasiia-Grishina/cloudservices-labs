from flask import Flask, flash, redirect, render_template, request, url_for, abort, Markup, session
from maestro import app

@app.route('/compute/list-nodes')
def nodes_list():
	return render_template('nodes-list.html')


# both display and handle form submit, then redirect to nodes_list
@app.route('/compute/create-node', methods=['GET', 'POST'])
def create_node(params?):
	return render_template('create-node.html')






# redirect to node_details
@app.route('/compute/stop-node')
def stop_node(node_id):
	return render_template('index.html')


# redirect to node_details
@app.route('/compute/start-node')
def start_node(node_id):
	return render_template('index.html')

# redirect to nodes_list
@app.route('/compute/terminate-node')
def terminate_node(node_id):
	return render_template('index.html')


# provide details + actions for nodes
@app.route('/compute/node-details')
def node_details(node_id):
	return render_template('node-details.html')



