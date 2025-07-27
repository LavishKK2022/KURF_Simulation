import json
import cv2
import base64
import numpy as np
import functools
from app.messaging import RabbitMQModel
from pika.channel import Channel
from pika.spec import (
    Basic,
    BasicProperties
)
from typing import (
    Dict,
    Any,
    Callable,
    Type,
)

ENCODING = 'utf-8'
FILE_ENCODING = '.png'


def dict_to_bytes(payload: Dict[str, Any]) -> bytes:
    """
    Converts a Python dictionary to bytes to send over
    RabbitMQ plumbing.

    Args:
        payload (Dict[str, Any]): The data to encode.

    Returns:
        bytes: The encoded data.
    """
    return json.dumps(payload).encode(ENCODING)


def bytes_to_dict(payload: bytes) -> Dict[str, Any]:
    """
    Converts bytes into a Python dictionary, This is 
    used on the receving end of the RabbitMQ plumbing.

    Args:
        payload (bytes): The data to decode.

    Returns:
        Dict[str, Any]: The decoded data.
    """
    return json.loads(payload)


def image_to_str(payload: np.ndarray) -> str:
    """
    Converts frame image to base64 string.
    This is a loseless operation.

    Args:
        payload (np.ndarray): The frame/image to convert.

    Returns:
        str: The base64 representation of the image.
    """
    _, encoded_image = cv2.imencode(FILE_ENCODING, payload)
    image_bytes = encoded_image.tobytes()
    return base64.b64encode(image_bytes)


def str_to_image(payload: str) -> np.ndarray:
    """
    Converts base64 string into a frame.
    This is a loseless operation.

    Args:
        payload (str): The base64 representation of the image.

    Returns:
        np.ndarray: The decoded frame from the base64 string.
    """
    image_str = base64.b64decode(payload)
    arr_1d = np.frombuffer(image_str, np.uint8)
    return cv2.imdecode(arr_1d, cv2.IMREAD_COLOR)


def simplify(
        func: Callable[[dict], Any],
        format: Type[RabbitMQModel]
) -> Callable[[Channel, Basic.Deliver, BasicProperties, bytes], Any]:
    """
    Simplifies the payload for the RabbitMQ consumer callback.
    This function also formats the data as expected by the payload.

    So as opposed to callback function having multiple uncessary
    arguments, the new callback only required a payload argument
    in the expected format.

    Args:
        func (Callable[[dict], Any]): The function to decorate.
        format (Type[RabbitMQModel]): The format of the callback arguments.

    Returns:
        Callable[[Channel, Basic.Deliver, BasicProperties, bytes], Any]:
        Wrapper for the callback method. This adheres to the RabbitMQ
        requirements whilst simplifying logic for the callback method.
    """
    @functools.wraps(func)
    def wrapper(
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes
    ) -> Any:
        return func(format(**bytes_to_dict(body)))
    return wrapper
