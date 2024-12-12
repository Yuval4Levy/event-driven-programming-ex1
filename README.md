# Order Processing System

This project consists of a producer and a consumer service that communicate via RabbitMQ. The producer generates orders and publishes them to a RabbitMQ exchange, while the consumer processes these orders.

## Author

**Full Name:** Yuval Levy

**ID Number:** 209370378

## Prerequisites

- Docker
- Docker Compose

## Setup Instructions

1. **Clone the repository:**

    ```sh
    git clone https://github.com/Yuval4Levy/event-driven-programming-ex1.git
    cd src
    ```

2. **Build and start the producer service:**

    ```sh
    docker-compose -f docker-compose-producer.yml up --build
    ```

3. **Build and start the consumer service:**

    ```sh
    docker-compose -f docker-compose-consumer.yml up --build
    ```

## API Endpoints

### Producer

- **Create Order**

    **URL:** `http://localhost:5000/create-order`

    **Method:** `POST`

    **Request Body:**

    ```json
    {
        "orderId": "ORDER123",
        "itemsNum": 3
    }
    ```

    **Response:**

    ```json
    {
        "response": "successfully created order: ORDER123"
    }
    ```

### Consumer

- **Get Order Details**

    **URL:** `http://localhost:5001/order-details?orderId=ORDER123`

    **Method:** `GET`

    **Response:**

    ```json
    {
        "orderId": "ORDER123",
        "customerId": "CUST-12345",
        "orderDate": "2024-12-12T14:18:57.000Z",
        "Items": [
            {
                "itemId": "ITEM-001",
                "quantity": 3,
                "price": 10.50
            }
        ],
        "totalAmount": 31.50,
        "currency": "USD",
        "status": "pending",
        "shippingCost": 0.63
    }
    ```

## RabbitMQ Configuration

### Exchange Type

**Type:** `fanout`

**Reason:** The `fanout` exchange type is chosen because it broadcasts messages to all bound queues. This is useful in scenarios where the same message needs to be processed by multiple consumers, ensuring that all services receive the order messages.

### Binding Key

**Is there a binding key on the consumer?** No, the `fanout` exchange type does not use routing keys. All messages sent to the exchange are delivered to all bound queues without any filtering.

### Exchange and Queue Declaration

**Which service declared the exchange and queue and why?**

- **Exchange Declaration:** The producer service declares the exchange. This ensures that the exchange exists before any messages are published to it.

- **Queue Declaration:** The consumer service declares the queue. This ensures that the queue exists before the consumer starts consuming messages from it, it also ensures that each consumer in a scaled system listens to the same queue.
