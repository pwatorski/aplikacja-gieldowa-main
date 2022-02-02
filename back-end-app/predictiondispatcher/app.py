import pika
import psycopg2

try:
    db_conn = psycopg2.connect(database='sarna', user='postgres', host='postgress', password='sarna')
except:
    db_conn = psycopg2.connect(database='sarna', user='postgres', host='0.0.0.0', password='sarna')
cur = db_conn.cursor()

def callback(ch, method, properties, body):
    symbol = body.decode()
    print(" [x] Received %s" % symbol)



    ch.basic_ack(delivery_tag=method.delivery_tag)



credentials = pika.PlainCredentials('sarna', 'sarna')
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', credentials=credentials))
except:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='0.0.0.0', credentials=credentials))


channel = connection.channel()
channel.queue_declare(queue='predict_queue', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='predict_queue', on_message_callback=callback)
print('[X]   Connected to all. Starting consuming queue...')
channel.start_consuming()