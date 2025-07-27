from app.config import (
    setup_logging,
    file_logging_config,
)
from app.messaging import (
    RabbitMQ,
    LogMessage,
    F_LOG_QUEUE,
)
from app.utils import (
    setup_consumer,
)

# Retrieves the file logger.
logger = setup_logging(file_logging_config)


def log_to_file(payload: LogMessage) -> None:
    """
    Callback method to log file messages to a file.

    Args:
        payload (LogMessage): The log message sent
        to the LOGS_EXCHANGE.
    """
    logger.info(payload.file_message)


if __name__ == '__main__':
    """ Boilerplate for the RabbitMQ consumer """
    setup_consumer(
        client=RabbitMQ(),
        subscribe_queue=F_LOG_QUEUE,
        callback=log_to_file,
        expected_format=LogMessage
    )
