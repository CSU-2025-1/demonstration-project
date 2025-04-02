import json
import logging
import os

import pika
from pymongo import MongoClient

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
MONGO_URL = os.getenv("MONGO_URL")

mongo_client = MongoClient(MONGO_URL)
db = mongo_client["logs"]
events_collection = db["todos_events"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("LOGGER")


def callback(ch, method, properties, body):
    event = json.loads(body)
    logger.info(f"Received event: {event}")
    try:
        events_collection.insert_one(event)
        response = {"status": "success", "event": "todo"}
    except Exception as e:
        logger.error("Failed to insert log: %s", e)
        response = {"status": "error", "error": str(e)}

    # Отправляем ответ обратно в очередь producer'у
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps({"test": "response"}),
    )


connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(queue="todos_events")

channel.basic_consume(queue="todos_events", on_message_callback=callback, auto_ack=True)

logger.info("Waiting for messages...")
channel.start_consuming()
