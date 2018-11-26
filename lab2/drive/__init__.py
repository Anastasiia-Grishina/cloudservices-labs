from flask import Flask, session
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.secret_key = 'SOSECRET!!!'

# bootstrap
bootstrap = Bootstrap(app)

import drive.buckets
import drive.files
