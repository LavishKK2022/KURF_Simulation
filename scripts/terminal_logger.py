from app.config import (
    setup_logging,
    stdout_logging_config,
)
from app.messaging import (
    RabbitMQ,
    LogMessage,
    T_LOG_QUEUE,
)
from app.utils import (
    setup_consumer,
)

# The logger for terminal output.
logger = setup_logging(stdout_logging_config)


def log_to_terminal(payload: LogMessage) -> None:
    """
    Callback method to log terminal messages to the
    terminal.

    Args:
        payload (LogMessage): The log message sent
        to the LOGS_EXCHANGE.
    """
    logger.info(payload.terminal_message)


if __name__ == '__main__':
    """ Boilerplate for RabbitMQ consumer """
    setup_consumer(
        client=RabbitMQ(),
        subscribe_queue=T_LOG_QUEUE,
        callback=log_to_terminal,
        expected_format=LogMessage
    )
