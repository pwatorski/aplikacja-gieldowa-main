import pika
import yfinance as yf
import psycopg2
from datetime import datetime


try:
    db_conn = psycopg2.connect(database='sarna', user='postgres', host='postgress', password='sarna')
except:
    db_conn = psycopg2.connect(database='sarna', user='postgres', host='0.0.0.0', password='sarna')
cur = db_conn.cursor()

def get_company_data(symbol):
    company = yf.Ticker(symbol)
    info = company.info
    name = info["longName"]
    values = company.history(period="2y", interval='1d')
    time_data = []
    for i in values.index:
        dt = i.to_pydatetime()
        time_data.append((int(1000 * values.at[i,"Open"]), int(datetime.timestamp(dt))))
    return {'symbol':symbol, 'name':name, 'records':time_data}

def request_prediction(symbol):
    channel.basic_publish(
        exchange='',
        routing_key='pred_queue_0',
        body=symbol,
        properties=pika.BasicProperties(
            delivery_mode=2,
            expiration='600000',
        ))


def write_in_database(symbol,company_name,time_data):
    cur.execute("SELECT id FROM stock")
    stock_id= cur.fetchone()
    sql = """INSERT INTO company(company_name,symbol,stock_id)
             VALUES(%s,%s,%s) RETURNING id;"""
    cur.execute(sql, (company_name,symbol,stock_id))
    company_id = cur.fetchone()[0]
    db_conn.commit()
    sql = "INSERT INTO action(value, timestamp, company_id) VALUES(%s,%s,%s)"
    for r in time_data:
        cur.execute(sql, (r[0], r[1], company_id))
        db_conn.commit()
    request_prediction(symbol)
    return

def callback(ch, method, properties, body):
    symbol = body.decode()
    print(f"\t[x] Received request for {symbol}")
    print(f"\t[x] Fetching data from Yahoo...")
    try:
        company_data = get_company_data(symbol)
    except:
        print(f"\t[x] Failed!")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    if not company_data['name']:
        print(f"\t[x] ERROR: No such symbol: {symbol}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    print(f"\t[x] Got [{len(company_data['records'])}] records.")
    print(f"\t[x] Adding to db...")
    try:
        write_in_database(symbol, company_data['name'], company_data['records'])
    except Exception as ex:
        print(f"\t[x] ERROR: Could not insert into database!\n{ex}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    print(f"\t[x] Done adding [{len(company_data['records'])}] records for {symbol} ({company_data['name']}).")
    ch.basic_ack(delivery_tag=method.delivery_tag)



credentials = pika.PlainCredentials('sarna', 'sarna')
try:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', credentials=credentials))
    except:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='0.0.0.0', credentials=credentials))
    failed = False
except:
    failed = True
if failed:
    import time
    print(f"[X]   Failed to connect, trying again in 10 seconds.")
    time.sleep(10)
else:
    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)
    channel.queue_declare(queue='pred_queue_0', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)
    print('[X]   Connected to all. Starting consuming queue...')
    channel.start_consuming()