from typing import (
    Optional,
    Tuple,
)
from app.messaging import (
    RabbitMQ,
    PartialMessage,
    PathMessage,
    LATENCY_QUEUE,
)
from app.utils import (
    FrameCount,
    PathHolder,
    setup_consumer,
    setup_publisher,
    update_path,
)
from app.config import (
    Files,
)
import threading
import pandas as pd
from pandas import DataFrame

current_row = 0


def get_resource(
        path: str,
        _: Optional[DataFrame]
) -> DataFrame:
    """
    Retrieves the resource as requested by the
    'setup_publisher' method.

    In the case of the latency node, this retrieves
    the pandas dataframe from the latency csv.

    Args:
        path (str): The path to extract data from.
        _ (Optional[DataFrame]): The current resource to close.

    Returns:
        DataFrame: The extracted csv data.
    """
    global current_row
    current_row = 0
    return pd.read_csv(path)


def read_data(
        resource: DataFrame
) -> Tuple[bool, float]:
    """
    Retrieves the data from the provided resource.
    In this case it read's a row from the latency
    dataframe.

    Args:
        resource (DataFrame): The dataframe to read from.

    Returns:
        Tuple[bool, float]: The success of the read operation
        and the data read from the dataframe.
    """
    global current_row
    if current_row >= len(resource):
        current_row = 0
    return (True, resource.iloc[current_row][0])


def get_message(
        counter: FrameCount,
        latency: float
) -> PartialMessage:
    """
    Sends the message to publish.

    This is requested by the 'setup_publisher' method.
    THe latency emitter sends the latency and frame_count
    values.

    Args:
        counter (FrameCount): Mutable helper object to keep
        track of the frame counts.

        latency (float): The latency value of the frame.

    Returns:
        PartialMessage: Message describing the current frame
        count and the latency at this frame.
    """
    return PartialMessage(
        frame_number=counter.count,
        latency=latency
    )


if __name__ == '__main__':
    """ Boilerplate for RabbitMQ publisher and consumer """
    threading.Thread(
        target=setup_publisher,
        kwargs={
            'resource': get_resource,
            'read_data': read_data,
            'get_message': get_message,
            'handle_read_failure': None,
            'resource_hook': None
        },
        daemon=True
    ).start()
    setup_consumer(
        client=RabbitMQ(),
        subscribe_queue=LATENCY_QUEUE,
        callback=update_path(PathHolder(), Files.LATENCY),
        expected_format=PathMessage
    )
