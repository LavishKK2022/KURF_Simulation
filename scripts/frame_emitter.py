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
    STREAM_QUEUE,
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
    Sends the message to publish.

    This is requested by the tightly bound 'setup_publisher'.
    Encodes the current frame count and the streamed frame.

    Args:
        counter (FrameCount): Mutable helper object to keep
        track of the current frame.

        frame (np.ndarray): The read 'frame'.

    Returns:
        PartialMessage: Message encoding the frame number
        and the streamed frame.
    """
    return PartialMessage(
        frame_number=counter.count,
        streamed_frame=image_to_str(frame)
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
        subscribe_queue=STREAM_QUEUE,
        callback=update_path(PathHolder(), Files.STREAMED),
        expected_format=PathMessage
    )
