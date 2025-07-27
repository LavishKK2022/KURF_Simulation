from pika.channel import (
    Channel,
)
from pika.spec import (
    Basic,
    BasicProperties,
)
from pika.adapters.blocking_connection import (
    BlockingChannel,
)
from pika import (
    BlockingConnection as connection,
)
from app.messaging import (
    Exchange,
    Queue,
    RabbitMQModel,
    HOST
)
from typing import (
    Callable,
    Any,
)
from app.utils import (
    dict_to_bytes as convert,
)


class RabbitMQ:
    """ RabbitMQ Helper Model """
    _instance = None

    def __new__(cls):
        """ Method to ensure RabbitMQ class is singleton """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Connect to the RabbitMQ plumbing.
            cls._instance._connect()
        return cls._instance

    def _connect(self) -> None:
        """ Connect to the RabbitMQ service """
        self._conn = connection(HOST)
        self._channel = self._conn.channel()

    def declare_exchange(
        self,
        exchange: Exchange
    ) -> None:
        """
        Declare the Exchange on the RabbitMQ service.

        Args:
            exchange (Exchange): The exchange to declare.
        """
        self.channel.exchange_declare(
            exchange=exchange.name,
            exchange_type=exchange.exchange_type
        )

    def declare_queue(
            self,
            queue: Queue
    ) -> None:
        """
        Declare and bind the queue on the RabbitMQ service.

        Args:
            queue (Queue): The queue to declare and bind.
        """
        self.channel.queue_declare(
            queue=queue.name,
            exclusive=queue.exclusive
        )
        self.channel.queue_bind(
            exchange=queue.exchange.name,
            queue=queue.name
        )

    def declare_queue_exchange(
            self,
            queue: Queue
    ) -> None:
        """
        Declare the queue and it's associated exchange.

        Args:
            queue (Queue): The queue to declare (and its exchange).
        """
        self.declare_exchange(queue.exchange)
        self.declare_queue(queue)

    def publish(
            self,
            exchange: Exchange,
            message: RabbitMQModel,
            routing: str = ''
    ) -> None:
        """
        Publishes messages on the exchange.

        Args:
            exchange (Exchange): The exchange to publish to.
            message (RabbitMQModel): The message to send.
            routing (str, optional): The queue's routing key.
        """
        self.declare_exchange(exchange)
        self.channel.basic_publish(
            exchange=exchange.name,
            routing_key=routing,
            body=convert(message.model_dump(by_alias=True, exclude_none=True))
        )

    def publish_to_queue(
            self,
            queue: Queue,
            message: RabbitMQModel
    ) -> None:
        """
        Publish messages to the defined queue.

        Args:
            queue (Queue): The queue to publish messages to.
            message (RabbitMQModel): The message to send.
        """
        self.publish(
            queue.exchange,
            queue.routing,
            message
        )

    def consume(
            self,
            queue: Queue,
            callback: Callable[
                [Channel, Basic.Deliver, BasicProperties, bytes], Any],
            ack: bool = True
    ) -> None:
        """
        Helper to consume RabbitMQ messages.

        Args:
            queue (Queue): The queue to subscribe to.

            callback (Callable[
                [Channel, Basic.Deliver, BasicProperties, bytes], Any
            ]): The callback method when a message enters the queue.

            ack (bool, optional): Message acknowledgement. Defaults to True.
        """
        self.channel.basic_consume(
            queue=queue.name,
            on_message_callback=callback,
            auto_ack=ack
        )

    @property
    def conn(self) -> connection:
        """
        The physical connection for the RabbitMQ service.

        Returns:
            connection: The physical connection.
        """
        return self._conn

    @property
    def channel(self) -> BlockingChannel:
        """
        The virtual connection to the RabbitMQ service.

        Returns:
            BlockingChannel: The virtual connection.
        """
        return self._channel
