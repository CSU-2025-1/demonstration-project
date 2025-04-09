import json
import logging
import os
import uuid
import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def send_rpc_event(event_type, data):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    # Эксклюзивная очередь для ответа
    result = channel.queue_declare(queue="", exclusive=True)
    callback_queue = result.method.queue

    corr_id = str(uuid.uuid4())
    response = {}

    def on_response(ch, method, props, body):
        if corr_id == props.correlation_id:
            response["result"] = json.loads(body)

    channel.basic_consume(queue=callback_queue, on_message_callback=on_response, auto_ack=True)

    channel.basic_publish(
        exchange="",
        routing_key="todos_events",
        properties=pika.BasicProperties(reply_to=callback_queue, correlation_id=corr_id),
        body=json.dumps({"type": event_type, "data": data}),
    )

    # Ожидаем ответа от consumer'а
    while "result" not in response:
        connection.process_data_events()

    connection.close()
    logger.info(f"ПОЛУЧЕН ОТВЕТ ОТ CONSUMER: {response['result']}")
