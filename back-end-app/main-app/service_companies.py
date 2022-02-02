# /flask_2/__init__.py
from flask import Flask, send_from_directory, request, redirect, render_template
from flask_restful import Api
#from flask_cors import CORS #comment this on deployment

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import config


app = Flask(__name__)

CORS(app)

# try:
#     app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#     app.secret_key = 'secret string'

#     db = SQLAlchemy(app)
    
# except:
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI_DOCKER
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)


#CORS(app) #comment this on deployment
api = Api(app)

from data_request_handler import ActionDataRequestHandler, AddCompanyRequestHandler, CandidateRequestHandler, CompanyDataRequestHandler, CurrentModelRequestHandler, PopularCompanyRequestHandler, PredictRequestHandler, OwnPredictionRequestHandler
api.add_resource(ActionDataRequestHandler, '/data/<company>')
api.add_resource(AddCompanyRequestHandler, '/add/<symbol>')
api.add_resource(PredictRequestHandler, '/predict/<symbol>')
api.add_resource(CompanyDataRequestHandler, '/list')
api.add_resource(PopularCompanyRequestHandler, '/popular')
api.add_resource(CandidateRequestHandler, '/candidates')

if __name__ == '__main__':

    db.create_all()
    app.run()
