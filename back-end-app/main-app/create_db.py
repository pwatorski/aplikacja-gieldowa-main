from datetime import timedelta
import random
from typing import List
from base_app import db
from models import Apisource, Stock, Company, Action
from misc import dane_z_nikad
import psycopg2
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
import pika
import time

some_symbols = ["OEDV", "AAPL", "BAC", "AMZN", "T", "GOOG", "MO", "DAL", "AA", "AXP", "DD", "BABA", "ABT", "UA", "AMAT", "AMGN"]

db_user = 'postgres'
db_password = 'sarna'
db_host = 'localhost'
db_port = 5432
db_name = 'sarna'

DATABASE_URI = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

def request_data(message):
    credentials = pika.PlainCredentials('sarna', 'sarna')
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', credentials=credentials))
    except:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='0.0.0.0', credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,
        ))
    connection.close()

try:
    from tqdm import tqdm
    TQDM=True
except:
    TQDM=False
    print("Consider instaling tqdm package for your Python interpreter:\npy -m pip install tqdm")

def create_apisource(db, name:str):
    apisource = Apisource(name)
    db.session.add(apisource)
    db.session.commit()
    return apisource.id

def create_stock(db, name:str, apisource_id:int):
    stock = Stock(name, apisource_id)
    db.session.add(stock)
    db.session.commit()
    return stock.id

def drop_table(db_conn, cur, table_name):
    try:
        cur.execute(f"DELETE FROM {table_name}") 
        db_conn.commit()
    except:
        pass
    rows_deleted = cur.rowcount
    return rows_deleted
    

def clear_db(db, c_all, c_pred, c_comp, c_act, c_usr, c_check):

    if c_check:
        print(f'Waiting...')    
        time.sleep(10)
    print('Connecting...')
    try:
        db_conn = psycopg2.connect(database='sarna', user='postgres', host='postgress', password='sarna')
    except:
        db_conn = psycopg2.connect(database='sarna', user='postgres', host='0.0.0.0', password='sarna')
    cur = db_conn.cursor()
    if c_check:
        cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('company',))
        if cur.fetchone()[0]:
            print("DB EXISTS!")
            return
        print("DB DOES NOT EXIST!")


    #cur.execute(f"DROP TABLE IF EXISTS action CASCADE") 
    #cur.execute(f"DROP TABLE IF EXISTS company CASCADE") 
    #cur.execute(f"DROP TABLE IF EXISTS stock CASCADE") 
    #cur.execute(f"DROP TABLE IF EXISTS api_source CASCADE") 
    print(f"Deleting candidates {drop_table(db_conn, cur, 'candidate')}")
    print(f"Deleting user_data_point {drop_table(db_conn, cur, 'user_data_point')}")
    print(f"Deleting user_pred {drop_table(db_conn, cur, 'user_pred')}")
    print(f"Deleting user_request {drop_table(db_conn, cur, 'user_request')}")
    if c_pred or c_comp:
        print(f"Deleting predictions {drop_table(db_conn, cur, 'prediction')}")
        print(f"Deleting futures {drop_table(db_conn, cur, 'future')}")
    if c_act:
        print(f"Deleting actions {drop_table(db_conn, cur, 'action')}")
    if c_comp:
        print(f"Deleting company {drop_table(db_conn, cur, 'company')}")
    if c_all:
        print(f"Deleting stock {drop_table(db_conn, cur, 'stock')}")
        print(f"Deleting apisource {drop_table(db_conn, cur, 'api_source')}")
    


    print('Creating Action, Company, Stock, Apisource tables...')
    db.session.commit()
    db.create_all()
    db.session.commit()

    if c_all:
        print('Creating apisource...')
        api_id = create_apisource(db, 'Yahoo')
        db.session.commit()
        print('Creating stock...')
        stock_id = create_stock(db, 'SomeStock', api_id)
        db.session.commit()
    print('Filling candidates...')
    with open('stock_combined.txt', 'r', encoding='utf8') as fi:
        sql = "INSERT INTO candidate(symbol, name) VALUES(%s,%s)"
        records = [x.strip().split(';') for x in fi]
        for symbol, name in tqdm(records[37:1037]):
            cur.execute(sql, (symbol, name, ))
            db_conn.commit()
            pass
        for symbol, name in tqdm(records[:5]):
            cur.execute(sql, (symbol, name, ))
            db_conn.commit()
            pass
    if c_comp:
        print('Filling companies with real data...')
        for symbol, name in tqdm(records[5:37]):
            request_data(symbol)



import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--comp', action='store_true',
                        help='clears actions and companies')
    parser.add_argument('--act', action='store_true',
                        help='clears only actions')
    parser.add_argument('--pred', action='store_true',
                        help='clears predictions')
    parser.add_argument('--all', action='store_true',
                        help='clears all')
    parser.add_argument('--usr', action='store_true',
                        help='clears user pred')
    parser.add_argument('--check', action='store_true',
                        help='check')
    args = parser.parse_args()

    c_all = args.all
    c_pred = args.pred or c_all
    c_comp = args.comp or c_all
    c_act = args.act or c_comp
    c_usr = args.usr or c_all
    clear_db(db, c_all, c_pred, c_comp, c_act, c_usr, args.check)