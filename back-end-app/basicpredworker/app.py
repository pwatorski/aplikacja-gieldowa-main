import pika
import psycopg2
from datetime import datetime, timedelta
import random
import numpy
import torch
from sklearn.preprocessing import MinMaxScaler
from model import LSTM
try:
    db_conn = psycopg2.connect(database='sarna', user='postgres', host='postgress', password='sarna')
except:
    db_conn = psycopg2.connect(database='sarna', user='postgres', host='0.0.0.0', password='sarna')
cur = db_conn.cursor()


model:LSTM



def load_config(c_path):
    with open('models.conf', 'r', encoding='utf8') as fi:
        models_dict = {x[0]:{'path':x[1], 'hidden_dim': int(x[2]), 'num_layers':int(x[3])} for x in [y.strip().split(';') for y in fi]}
    return models_dict

def run_model_spoofed(steps:int=100, end:datetime=None, step_time:timedelta=None, beg_val:int=400, 
    stringify=False, fluctuation=100, as_tuples:bool=False):
    if not step_time:
        step_time = timedelta(hours=1)
    if not end:
        end = datetime.now()
    begin = end-step_time*steps
    data = []
    value = beg_val
    for e in range(steps):
        value = max(100, value + (random.random() * 2 - 1)**5 * fluctuation)
        if stringify:
            data.append((begin.strftime('%d-%m-%Y %H:%M:00'), value))
        else:
            data.append((begin, value))
        begin += step_time
    if as_tuples:
        return data
    return {t[0]: t[1] for t in data}

def offset_data(data):
    random.seed(data[0] + int(model_id))
    return [d * (random.random() * 0.2 + 0.9) for d in data]

def run_model(raw_data, steps=20):
    scaler = MinMaxScaler(feature_range=(-1, 1))
    pred = fit_and_blowup_data(raw_data, scaler)
    pred = predict_steps(pred, steps)
    flat_pred = refit_and_flatten_data(raw_data, pred, scaler, steps)
    return flat_pred

def predict_steps(data, steps):
    for step in range(steps):
        pred_step = model(data)
        pred_step = pred_step.detach()
        pred_step = torch.reshape(pred_step, (1, 1, 1))
        data = torch.cat((data, pred_step), dim=1)
    return data

def fit_and_blowup_data(raw_data, scaler):
    raw_data = numpy.array(raw_data)
    fit_data = scaler.fit_transform(raw_data.reshape(-1,1))
    fit_data = torch.from_numpy(fit_data).type(torch.Tensor)
    fit_data = torch.reshape(fit_data, (1,-1, 1))
    return fit_data.detach().clone()

def refit_and_flatten_data(raw_data, pred, scaler, steps):
    pred = scaler.inverse_transform(torch.reshape(pred.detach(), (-1, 1)).numpy())
    pred = list(pred.flatten()[-(steps+1):])
    for e, p in enumerate(pred[:-1]):
        if p != 0 and pred[e+1] / p > 1.2:
            pred[e+1] = p * 1.2
        elif p != 0 and  pred[e+1] / p < 0.8:
            pred[e+1] = p * 0.8
    avg = sum(raw_data[-steps:]) / steps
    noise = offset_data([x - avg for x in raw_data[-steps - 20:-20]])
    noise.reverse()
    noise[0]=0
    noise[1]=0
    multi = 0.25 if model_id == '2' else 0.5
    pred = [x + y * multi for x, y in zip(pred, noise)]
    return pred


def callback(ch, method, properties, body):
    symbol = body.decode().split(';')
    user_request = False
    if symbol[0] == 'ur':
        user_request = True
        symbol = int(symbol[1])
    else:
        symbol = symbol[0]
    steps = 20
    print(f"\t[x] Received request for {symbol}")
    if user_request:
        find_request = "SELECT * FROM user_request WHERE request_id = %s;"
        cur.execute(find_request, (symbol,))
        request = cur.fetchone()
        if not request:
            print(f"\t[x] No such request: {symbol}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        update_request = """UPDATE user_request SET state=(%s) WHERE id = %s RETURNING id;"""
        cur.execute(update_request, (1, request[0]))
        print('Inserted')
        request_db_id = cur.fetchone()[0]
        db_conn.commit()
        newest_action_sql = "SELECT * FROM user_data_point WHERE request_id = %s ORDER BY timestamp DESC"
        cur.execute(newest_action_sql, (request_db_id,))
        actions = cur.fetchmany(1000)
        
        values = [x[2] / 1000.0 for x in actions]
        values.reverse()

    else:
        find_company = "SELECT * FROM company WHERE symbol = %s;"
        cur.execute(find_company, (symbol,))
        company = cur.fetchone()
        if not company:
            print(f"\t[x] No such company: {symbol}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        company_id, company_name, symbol, stock_id = company
        print(f"\t[x] Found company: {symbol} ({company_name})")
        get_future = "SELECT * FROM future WHERE company_id = %s"
        cur.execute(get_future, (company_id,))
        future = cur.fetchone()
        now = int(datetime.timestamp(datetime.now()))
        if not future:
            print(f"\t[x] No future found, creating one...")
            add_future = """INSERT INTO future(company_id,timestamp)
                VALUES(%s,%s) RETURNING id;"""
            cur.execute(add_future, (company_id,now))
            future_id = cur.fetchone()[0]
            db_conn.commit()
        else:
            print(f"\t[x] Found future, cleaning...")
            future_id = future[0]
            delete_preds = "DELETE FROM prediction WHERE company_id = %s;"
            cur.execute(delete_preds, (future_id,))
            db_conn.commit()
        print(f"\t[x] Clean future")
        
        newest_action_sql = "SELECT * FROM action WHERE company_id = %s ORDER BY timestamp DESC"
        cur.execute(newest_action_sql, (company_id,))
        #action_id, action_value, action_timestamp, action_company_id = cur.fetchmany(100)
        actions = cur.fetchmany(1000)
        if len(actions) == 0:
            print(f"\t[x] No data!")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        values = [x[1]/ 1000.0 for x in actions]
        values.reverse()
    print(f"\t[x] Predicting {steps} steps...")
    
    pred = run_model(values, steps=20)
    
    if user_request:
        sql = "INSERT INTO user_pred(request_id, value, timestamp) VALUES(%s,%s,%s)"
        print(f"\t[x] Inserting into user future...")
        for e, r in enumerate(pred):
            cur.execute(sql, (request_db_id, int(r * 1000), e, ))
            db_conn.commit()
        update_request = """UPDATE user_request SET state=(%s) WHERE id = %s;"""
        cur.execute(update_request, (2, request_db_id))
        db_conn.commit()
    else:
        sql = "INSERT INTO prediction(value, timestamp, company_id) VALUES(%s,%s,%s)"
        print(f"\t[x] Inserting into future...")

        start = datetime.fromtimestamp(actions[0][2])

        for r in pred:
            cur.execute(sql, (int(r * 1000), int(datetime.timestamp(start)), future_id))
            db_conn.commit()
            start += timedelta(days=1)
    print(f"\t[x] Future done!")

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
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('model', help='model number')

    args = parser.parse_args()


    config = load_config('models.conf')
    model_config = config[args.model]
    model_id = args.model
    print(f"[X]   Loading model {args.model} from {model_config['path']}...")
    model = LSTM(hidden_dim=model_config['hidden_dim'], num_layers=model_config['num_layers'])

    model.load_state_dict(torch.load(model_config['path']))
    print(f"[X]   Model loaded.")
    channel = connection.channel()
    channel.queue_declare(queue=f'pred_queue_0', durable=True)
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(queue=f'pred_queue_0', on_message_callback=callback)
    print('[X]   Connected to all. Consuming queue...')
    channel.start_consuming()
