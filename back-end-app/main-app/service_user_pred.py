# /flask_2/__init__.py
from flask import Flask, send_from_directory, request, redirect, render_template
from flask_restful import Api
#from flask_cors import CORS #comment this on deployment

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
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

#CORS(app) #comment this on deployment
api = Api(app)

@app.route("/", defaults={'path':''})
def serve(path):
    return send_from_directory(app.static_folder,'index.html')

# from file_upload_handler import upload_datafile
# @app.route("/flask/upload_data", methods=["GET", "POST"])
# def handle_upload():
#     return upload_datafile(request)

from data_request_handler import CurrentModelRequestHandler, OwnPredictionRequestHandler
api.add_resource(CurrentModelRequestHandler, '/predictors')
api.add_resource(OwnPredictionRequestHandler, '/own_prediction/<request_id>')

if __name__ == '__main__':

    app.run()
