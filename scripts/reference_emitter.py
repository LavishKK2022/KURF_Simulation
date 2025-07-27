from app.utils import (
    FrameCount,
    PathHolder,
    image_to_str,
    setup_publisher,
    setup_consumer,
    get_resource,
    read_data,
    handle_read_failure,
    check_resource,
    update_path
)
from app.messaging import (
    RabbitMQ,
    PartialMessage,
    PathMessage,
    REFERENCE_QUEUE,
)
from app.config import (
    Files,
)
import numpy as np
import threading


def get_message(
        counter: FrameCount,
        frame: np.ndarray
) -> PartialMessage:
    """
    Sends the method to publish.

    This is a requirement of the tighly bound
    'setup_publisher' method.

    Args:
        counter (FrameCount): Mutable helper to keep track
        of current frame.

        frame (np.ndarray): The read 'frame'.

    Returns:
        PartialMessage: Message describing the partial data.
    """
    return PartialMessage(
        frame_number=counter.count,
        reference_frame=image_to_str(frame)
    )


if __name__ == '__main__':
    """ Boilerplate for RabbitMQ publisher and consumer """
    threading.Thread(
        target=setup_publisher,
        kwargs={
            'resource': get_resource,
            'read_data': read_data,
            'get_message': get_message,
            'handle_read_failure': handle_read_failure,
            'resource_hook': check_resource
        },
        daemon=True
    ).start()
    setup_consumer(
        client=RabbitMQ(),
        subscribe_queue=REFERENCE_QUEUE,
        callback=update_path(PathHolder(), Files.REFERENCE),
        expected_format=PathMessage
    )
