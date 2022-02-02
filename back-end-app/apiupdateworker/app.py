import pika
import yfinance as yf
import psycopg2
from datetime import datetime, timedelta
import time
import math

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
    channel.queue_declare(queue='pred_queue_0', durable=True)

def request_prediction(symbol):
    
    channel.basic_publish(
        exchange='',
        routing_key='pred_queue_0',
        body=symbol,
        properties=pika.BasicProperties(
            delivery_mode=2,
            expiration='600000',
        ))




try:
    db_conn = psycopg2.connect(database='sarna', user='postgres', host='postgress', password='sarna')
except:
    db_conn = psycopg2.connect(database='sarna', user='postgres', host='0.0.0.0', password='sarna')

def dt_to_timestamp(date):
    return int(datetime.timestamp(date))

def timestamp_to_dt(timestamp):
    return datetime.fromtimestamp(timestamp)


step_seconds=45*60


def run(): 
    print(f"\t  [x] Starting checking...")
    cur = db_conn.cursor()

    find_company = "SELECT * FROM company ;"
    while True:
        start=datetime.now()
        cur.execute(find_company)

        companies = cur.fetchall()
        print(f"\t  [x] Got {len(companies)} companies...")
        updates = 0
        pred_reqs = 0
        action_upd = 0
        for company_id,c_name,c_symbol,c_stock in companies:
            sql = "SELECT * FROM action WHERE company_id = %s order by timestamp DESC;"
            cur.execute(sql, (company_id,))
            action = cur.fetchone()
            if action:
                action_dt = timestamp_to_dt(action[2])
            else:
                action_dt = datetime.now() - timedelta(days=600)
            current_company = yf.Ticker(c_symbol)
            values = current_company.history(start=action_dt+timedelta(hours=1), interval='1d')
            time_data = []
            for i in values.index:
                dt = i.to_pydatetime()
                val = values.at[i,"Open"]
                val = int(1000 * val) if val and not math.isnan(val) else 0
                time_data.append((val, int(datetime.timestamp(dt))))
            if action and time_data[0][0]==action[1]:
                time_data=time_data[1:]

            action_upd += len(time_data)
            if len(time_data) > 0:
                print (c_symbol)
                updates += 1

            sql = "SELECT * FROM future WHERE company_id = %s order by timestamp DESC;"
            cur.execute(sql, (company_id,))
            future = cur.fetchone()
            if len(time_data) > 0 or not future:
                request_prediction(c_symbol)
                pred_reqs += 1

            sql = "INSERT INTO action(value, timestamp, company_id) VALUES(%s,%s,%s)"
            for r in time_data:
                cur.execute(sql, (r[0], r[1], company_id))
                db_conn.commit()
            
        end=datetime.now()
        delta=end-start
        print(f"\t  [x] Updated {updates} companies.")
        print(f"\t  [x] Fetched {action_upd} datatpoints.")
        print(f"\t  [x] Requesting {pred_reqs} predictions.")
        print(f"\t  [x] Update elapsed {delta.seconds} seconds.")
        print(f"\t  [x] Waiting {step_seconds-delta.seconds} seconds...")
        time.sleep(max(0,step_seconds-delta.seconds))
print('[X]   Connected to all.')
run()

