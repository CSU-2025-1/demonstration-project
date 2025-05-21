import json
import logging
import os

import pika
from pymongo import MongoClient

import elasticapm
from elasticapm import Client

elasticapm.instrument()


client = Client(
    {
        "SERVICE_NAME": "logger-app",
        "SERVER_URL": "	https://9ef4f0c366104414ae851b8dca472c54.apm.us-central1.gcp.cloud.es.io:443",
        "SECRET_TOKEN": "exeEUZZ0koQo75fCQh",
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
    }
)


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
    trace_header = event.get("apm", {}).get("traceparent")
    logger.info(f"Received event: {event}")

    trace_parent = elasticapm.trace_parent_from_string(trace_header)
    client.begin_transaction(transaction_type="messaging", trace_parent=trace_parent)
    try:
        events_collection.insert_one(event)
        response = {"status": "success", "event": "todo"}
        client.end_transaction(name=f"consume:{event['type']}", result="success")
    except Exception as e:
        logger.exception("Failed to insert log: %s", e)
        response = {"status": "error", "error": str(e)}
        client.end_transaction(name=f"consume:{event['type']}", result="failure")

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
