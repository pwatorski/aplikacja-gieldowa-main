# /flask_2/__init__.py
from flask import Flask, send_from_directory, request, redirect, render_template
#from flask_cors import CORS #comment this on deployment

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import config
app = Flask(__name__)

CORS(app)

try:
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = 'secret string'

    db = SQLAlchemy(app)
except:
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI_DOCKER
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = 'secret string'

    db = SQLAlchemy(app)

db = SQLAlchemy(app)

from file_upload_handler import upload_datafile
@app.route("/userdata", methods=["GET", "POST"])
def handle_upload():
    print(f'XD')
    return upload_datafile(request)