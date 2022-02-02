from flask import Flask, send_from_directory
from flask_restful import Api

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import config

app = Flask(__name__)

CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)
db.create_all()

api = Api(app)

@app.route("/", defaults={'path':''})
def serve(path):
    return send_from_directory(app.static_folder,'index.html')


if __name__ == '__main__':

    db.create_all()
    app.run()
