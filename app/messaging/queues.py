from dataclasses import dataclass
from app.messaging import (
    Exchange,
    FILE_EXCHNAGE,
    AGGREGATE_EXCHANGE,
    REWARD_EXCHANGE,
    LOGS_EXCHANGE,
    DECISION_EXCHANGE
)


@dataclass
class Queue:
    """
    Mapping to Queues in RabbitMQ.
    Stores the Exchange to bind to.
    """
    name: str
    routing: str
    exchange: Exchange
    exclusive: bool = True


# Receive file paths to extract stream frames.
STREAM_QUEUE = Queue(
    name='emit.streamed.frames',
    routing='',
    exchange=FILE_EXCHNAGE
)

# Receive file paths to extract reference frames.
REFERENCE_QUEUE = Queue(
    name='emit.reference.frames',
    routing='',
    exchange=FILE_EXCHNAGE
)

# Receive file paths to extract latency values.
LATENCY_QUEUE = Queue(
    name='emit.latency.frames',
    routing='',
    exchange=FILE_EXCHNAGE
)

# Receive partial frame data to aggregate.
AGGREGATE_QUEUE = Queue(
    name='aggregate.frames',
    routing='sort',
    exchange=AGGREGATE_EXCHANGE
)

# Receive complete frame data to calculate reward.
REWARD_QUEUE = Queue(
    name='calculate.reward',
    routing='reward',
    exchange=REWARD_EXCHANGE
)

# Recieve log messages.
T_LOG_QUEUE = Queue(
    name='log.to.terminal',
    routing='',
    exchange=LOGS_EXCHANGE
)

# Receive log messages.
F_LOG_QUEUE = Queue(
    name='log.to.file',
    routing='',
    exchange=LOGS_EXCHANGE
)

# Receive streaming decisions for later relaying.
RELAY_QUEUE = Queue(
    name='relay.new.file',
    routing='switch',
    exchange=DECISION_EXCHANGE
)
