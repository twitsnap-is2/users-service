import pika
import os
import json

class MetricsChannel:
    def __init__(self):
        try: 
            connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv('RABBIT_URL')))
            print("=================CONNECTION STATUS====================", connection.is_open)
            self.channel = connection.channel()
            self.channel.queue_declare(queue='MetricsQueue', durable=True)
        except Exception as e:
            self.channel = None
            print("Error connecting to rabbitmq: ", e)
    
            
    def sendMetrics(self, data):
        
        try:
            self.channel.basic_publish(exchange='',
                        routing_key='MetricsQueue',
                        body=json.dumps(data))
            print("=================ENVIA METRICAS====================")
        except Exception as e:
            print("Error sending metrics: ", e)



    
