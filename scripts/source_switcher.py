import os
from app.messaging import (
    RabbitMQ,
    DecisionMessage,
    PathMessage,
    FILE_EXCHNAGE,
    RELAY_QUEUE,
)
from app.config import (
    Decision,
    Folder,
    VIDEO_FOLDER,
)
from app.utils import (
    setup_consumer,
)
from random import randint

rabbit_mq = RabbitMQ()


def emit_new_path(payload: DecisionMessage) -> None:
    """
    Callback to emit the new path to the File Exchange.
    This updates the subscribing nodes to redirect
    their source to the new stream, as published by this
    message.

    Args:
        payload (DecisionMessage): Message that describes
        the streaming decision.
    """
    def get_random_path(path: str) -> str:
        """
        Get a random path from a given folder.
        The folder structure adheres to a strict numbered
        definition that enables this method to work.

        Args:
            path (str): The folder from which a file is
            chosen at random.

        Returns:
            str: The path of the random file.
        """
        count = sum(
            1
            for p in os.listdir(path)
            if os.path.isdir(os.path.join(path, p))
        )
        random = randint(1, count)
        return os.path.join(path, str(random))

    folders = {
        Decision.LOCAL: Folder.LOCAL,
        Decision.STREAM: Folder.STREAM
    }
    folder = os.path.join(VIDEO_FOLDER, folders[payload.decision])
    # Publish the new path.
    rabbit_mq.publish(
        exchange=FILE_EXCHNAGE,
        message=PathMessage(
            path=get_random_path(folder)
        )
    )


if __name__ == '__main__':
    """ Boilerplate for RabbitMQ consumer """
    setup_consumer(
        client=rabbit_mq,
        subscribe_queue=RELAY_QUEUE,
        callback=emit_new_path,
        expected_format=DecisionMessage,
    )
