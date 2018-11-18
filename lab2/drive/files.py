from flask import Flask
from drive import app

@app.route('/bucket/<name>')
def bucket(name):
   return 'Hello {}'.format(name)