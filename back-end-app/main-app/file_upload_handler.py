import pika
from models import UserRequest, UserDataPoint
from base_app import db
import time
def check_request_validity(request):
    if not ('modelId' in request.values and 'dataFile' in request.files):
            return False, {'message':'Invalid data! Provide model id in value "modelId" and the file in "dataFile".'}
    return True, None

def try_parse_data(request):
    file = request.files['dataFile']
    lines = [l.strip() for l in file.read().decode().split('\n')]
    lines = [l for l in lines if len(l) > 0]
    if ';' in lines[0]:
        separator = ';'
    else:
        separator = ','
    if len(lines) == 1:
        try:
            data = [float(x) for x in lines.split(separator)]
        except:
            return None, {'msg':'parsing error'}
    else:
        data = [l.split(separator)[-1] for l in lines]
        try:
            x = float(data[0])
        except:
            data = data[1:]
        try:
            data = [float(d) for d in data]
        except:
            return None, {'msg':'parsing error'}
    return data, None

def send_pred_request(request_id):
    credentials = pika.PlainCredentials('sarna', 'sarna')
    try:
      connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', credentials=credentials))
    except:
      connection = pika.BlockingConnection(pika.ConnectionParameters(host='0.0.0.0', credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='pred_queue_0', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='pred_queue_0',
        body=f'ur;{request_id}',
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    connection.close()

def upload_datafile(request):
    if request.method == "POST":
        success, message = check_request_validity(request)
        if not success:
            return message

        data, message = try_parse_data(request)

        if not data:
            return message

        request_id = int(time.time() * 1000)
        ur = UserRequest(request_id, 0, 0)
        db.session.add(ur)
        db.session.commit()
        
        for e, d in enumerate(data):
            db.session.add(UserDataPoint(ur.id, int(d * 1000), e))
        db.session.commit()

        send_pred_request(request_id)

    return {'request_id':f'{request_id}'}