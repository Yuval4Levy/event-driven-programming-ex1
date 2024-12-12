from flask import Flask, request, jsonify
import pika
import json
import threading
import os

app = Flask(__name__)

orders: dict = {}

rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'guest')

credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)


def startConsumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port,
                                                                   credentials=credentials))
    channel = connection.channel()
    result = channel.queue_declare(queue='orders_queue', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='orders', queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=processOrder, auto_ack=True)
    print('Waiting for messages...')
    channel.start_consuming()


def calculateShippingCost(totalAmount: float) -> float:
    return round(totalAmount * 0.02, 2)


def processOrder(ch, method, properties, body):
    order = json.loads(body)
    if order['status'] == 'pending':
        orderId: str = order['orderId']
        order['shippingCost']: float = calculateShippingCost(order['totalAmount'])
        orders[orderId] = order
        print(f"Processed order: {orderId}")


@app.route('/order-details', methods=['GET'])
def orderDetails():
    orderId: str = request.args.get('orderId')
    if orderId in orders:
        return jsonify(orders[orderId]), 200
    else:
        return jsonify({"error": "Order not found"}), 404


if __name__ == '__main__':
    consumer_thread = threading.Thread(target=startConsumer)
    consumer_thread.start()
    app.run(host='0.0.0.0', port=5001)
