from flask import Flask, flash, redirect, render_template, request, url_for, abort, Markup, session
from maestro import app
from maestro.helpers import switch_regions

@app.route('/')
def dashboard():
	return render_template('index.html')

@app.route('/switch-region/<region>')
def change_region(region):
	switch_regions(region)

	return_url = request.referrer or '/'

	flash(Markup('Switched region to <b>{}</b>'.format(region)))


	return redirect(return_url)