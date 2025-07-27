from dataclasses import dataclass
from enum import Enum
from typing import Type
from app.messaging import (
    RabbitMQModel,
    LogMessage,
    PathMessage,
    DecisionMessage,
    FrameMessage,
    PartialMessage
)


class ExchangeType(str, Enum):
    """ Types of RabbitMQ Exchanges """
    TOPIC = 'topic'
    DIRECT = 'direct'
    FANOUT = 'fanout'


@dataclass
class Exchange:
    """
    Maps to RabbitMQ Exchange
    Enforces the expected Message Type.
    """
    name: str
    exchange_type: str
    expected_message: Type[RabbitMQModel]


# Emitting logs as 'LogMessage'[s]
LOGS_EXCHANGE = Exchange(
    name='log.messages',
    exchange_type=ExchangeType.FANOUT,
    expected_message=LogMessage
)

# Emitting the new file paths as 'PathMessage'[s]
FILE_EXCHNAGE = Exchange(
    name='send.path',
    exchange_type=ExchangeType.FANOUT,
    expected_message=PathMessage
)

# Emitting the streaming source decision as 'DecisionMessage'[s]
DECISION_EXCHANGE = Exchange(
    name='send.decision',
    exchange_type=ExchangeType.DIRECT,
    expected_message=DecisionMessage
)

# Emitting the complete frame data for reward calculation as
# 'FrameMessage'[s]
REWARD_EXCHANGE = Exchange(
    name='calculate.rewards',
    exchange_type=ExchangeType.DIRECT,
    expected_message=FrameMessage
)

# Emitting partial frame data for grouping into the MongoDB
# database as 'PartialMessage'[s]
AGGREGATE_EXCHANGE = Exchange(
    name='aggregate.frames',
    exchange_type=ExchangeType.DIRECT,
    expected_message=PartialMessage
)
