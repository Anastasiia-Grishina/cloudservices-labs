from flask import Flask, flash, redirect, render_template, request, url_for, abort, Markup, session
from maestro import app

@app.route('/')
def dashboard():
	return render_template('index.html')

