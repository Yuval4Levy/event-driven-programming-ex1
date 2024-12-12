from flask import Flask, request, jsonify
import pika
import json
import random
import os
import time
from datetime import datetime
import logging

app = Flask(__name__)


ITEMS = [
    {"itemId": "ITEM-001", "price": 10.50},
    {"itemId": "ITEM-002", "price": 20.75},
    {"itemId": "ITEM-003", "price": 15.00},
    {"itemId": "ITEM-004", "price": 7.25},
    {"itemId": "ITEM-005", "price": 12.40},
]

logging.basicConfig(level=logging.DEBUG)
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'guest')

credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)

while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port,
                                                                       credentials=credentials))
        channel = connection.channel()
        channel.exchange_declare(exchange='orders', exchange_type='fanout')
        break
    except pika.exceptions.AMQPConnectionError:
        print("Connection to RabbitMQ failed, retrying in 5 seconds...")
        time.sleep(5)


def generateCustomerId() -> str:
    return f"CUST-{random.randint(10000, 99999)}"


def generateItemFromSet() -> dict:
    item = random.choice(ITEMS)
    quantity = random.randint(1, 5)
    return {
        "itemId": item["itemId"],
        "quantity": quantity,
        "price": item["price"]
    }


def generateOrder(order_id, items_num) -> dict:
    customerId: str = generateCustomerId()
    orderDate: str = datetime.now().isoformat()
    items = [generateItemFromSet() for _ in range(items_num)]
    totalAmount = sum(item["price"] * item["quantity"] for item in items)
    currency: str = "USD"
    status: str = "pending"

    return {
        "orderId": order_id,
        "customerId": customerId,
        "orderDate": orderDate,
        "Items": items,
        "totalAmount": totalAmount,
        "currency": currency,
        "status": status
    }


def publishOrder(order):
    try:
        channel.basic_publish(exchange='orders', routing_key='', body=json.dumps(order))
    except Exception as e:
        app.logger.error(f"Failed to publish order: {e}")
        raise


@app.route('/create-order', methods=['POST'])
def createOrder():
    try:
        data = request.get_json()
        if not data or 'orderId' not in data or 'itemsNum' not in data:
            return jsonify({"error": "Invalid input"}), 400

        orderId: str = data['orderId']
        itemsNum: int = data['itemsNum']

        if not isinstance(orderId, str) or not isinstance(itemsNum, int):
            return jsonify({"error": "Invalid input types"}), 400

        if itemsNum <= 0:
            return jsonify({"error": "Invalid input, cannot create an order without items"}), 400

        order = generateOrder(orderId, itemsNum)
        publishOrder(order)
        return jsonify({"response": f"successfully created order: {orderId}"}), 200
    except Exception as e:
        app.logger.error(f"Failed to create order: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        connection.close()
