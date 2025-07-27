import os
import sys
from app.utils import (
    PathHolder,
    FrameCount,
    simplify,
)
from app.messaging import (
    RabbitMQ,
    RabbitMQModel,
    Queue,
    PathMessage,
    PartialMessage,
    AGGREGATE_QUEUE
)
from app.config import (
    Files,
)
from typing import (
    TypeVar,
    Callable,
    Type,
    Any,
    Union,
    Tuple,
)
from time import sleep as wait

path_holder = PathHolder()
rabbit_mq = RabbitMQ()
counter = FrameCount()
T = TypeVar('T')


def setup_consumer(
        client: RabbitMQ,
        subscribe_queue: Queue,
        callback: Callable[[RabbitMQModel], Any],
        expected_format: Type[RabbitMQModel],
        ack: bool = True
) -> None:
    """
    This method helps abstract the RabbitMQ
    boilerplate code to set up the consumer.

    Args:
        client (RabbitMQ): The RabbitMQ client.

        subscribe_queue (Queue): The queue this node subscribes to.

        callback (Callable[[RabbitMQModel], Any]): Callback method
        when the queue receives data.

        expected_format (Type[RabbitMQModel]): The format of the
        message, expected by the callback method.

        ack (bool, optional) = True: RabbitMQ queue acknowledgement.
    """
    client.declare_queue_exchange(subscribe_queue)
    client.consume(
        queue=subscribe_queue,
        on_message_callback=simplify(callback, expected_format),
        auto_ack=ack
    )
    # Stops consuming once program is exited.
    try:
        client.channel.start_consuming()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


def update_path(
        path_holder: PathHolder,
        file: Files
) -> Callable[[PathMessage], None]:
    """
    Boilerplate code to update the paths for the new
    streaming data - as required by the node.

    Each node has a 'file' parameter that makes the
    path to update unique.

    Args:
        path_holder (PathHolder): Mutable object to update
        with the new path.

        file (Files): The file requested by the node - to
        append to the new updated path.

    Returns:
        Callable[[PathMessage], None]: Wrapper function to act
        as callback for the RabbitMQ consumer nodes.
    """
    def wrapper(payload: PathMessage):
        path_holder.path = os.path.join(payload.path, file)
    return wrapper


def setup_publisher(
        resource: Callable[[str, Union[T, None]], Union[T, None]],
        read_data: Callable[[T], Tuple[bool, Any]],
        get_message: Callable[[FrameCount, Any], PartialMessage],
        handle_read_failure: Callable[[T], None] = None,
        resource_hook: Callable[[T], bool] = None
) -> None:
    """
    Boilerplate to set up the publisher nodes.
    This method is often ran as a separate daemon thread.

    This is a tightly bound publisher helper that abstracts away
    common logic between the 'latency', 'reference' and 'streamed'
    emitters.

    Args:
        resource (Callable[[str, Union[T, None]], Union[T, None]]): Method to
        retrieve the resource.

        read_data (Callable[[T], Tuple[bool, Any]]): Method to read from the
        data source.

        get_message (Callable[[FrameCount, Any], PartialMessage]): Method to
        retrieve the message to publish.

        handle_read_failure (Callable[[T], None], optional): Method to handle
        a failure in reading.

        resource_hook (Callable[[T], bool], optional): Method to handle failure
        in accessing a resource.
    """
    current_path = path_holder.path
    source = resource(current_path, None)

    while True:
        path_snapshot = path_holder.path
        if path_snapshot:
            if current_path != path_snapshot:
                current_path = path_snapshot
                source = resource(current_path, source)
            if resource_hook and not resource_hook(source):
                wait(0.25)
                continue
            succeeded, result = read_data(source)
            if handle_read_failure and not succeeded:
                handle_read_failure(source)
                continue
            rabbit_mq.publish_to_queue(
                AGGREGATE_QUEUE,
                get_message(counter, result)
            )
            counter.increment()
        wait(0.01)
