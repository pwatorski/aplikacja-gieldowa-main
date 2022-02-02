from flask import Flask, send_from_directory
from flask_restful import Api

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import config
import sqlalchemy
from sqlalchemy import create_engine, engine
app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI_DOCKER
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)

db_engine = create_engine(config.DATABASE_URI_DOCKER)

def database_is_empty():
    table_names = sqlalchemy.inspect(db_engine).get_table_names()
    is_empty = table_names == []
    print('Db is empty: {}'.format(is_empty))
    return is_empty


api = Api(app)
#if database_is_empty():
    #from create_db import clear_db
    #clear_db(db, True, True, True, True, True)
@app.route("/", defaults={'path':''})
def serve(path):
    return send_from_directory(app.static_folder,'index.html')

@app.route("/make_db/", defaults={'path':''})
def make_db(path):
    from create_db import clear_db
    clear_db(db, True, True, True, True, True, False)
    return {'message':'czoko'}

if __name__ == '__main__':

    db.create_all()
    app.run()
