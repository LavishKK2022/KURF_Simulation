import cv2
from typing import Tuple
import numpy as np


def get_resource(
        path: str,
        existing_resource: cv2.VideoCapture
) -> cv2.VideoCapture:
    """
    Helper method to retrieve the video resource from
    the path.

    The existing resource is closed.

    Args:
        path (str): The path to the video resource.
        existing_resource (cv2.VideoCapture): The existing
        resource to close.

    Returns:
        cv2.VideoCapture: The video capture object.
    """
    if existing_resource:
        existing_resource.release()
    return cv2.VideoCapture(path)


def check_resource(
        resource: cv2.VideoCapture
) -> bool:
    """
    Checks if the resource is opened correctly.

    Args:
        resource (cv2.VideoCapture): The resource to check.

    Returns:
        bool: True if opened, False otherwise.
    """
    return not resource.isOpened()


def read_data(
        resource: cv2.VideoCapture
) -> Tuple[bool, np.ndarray]:
    """
    Retrieves the next frame from the video.

    Args:
        resource (cv2.VideoCapture): The resource
        to read from.

    Returns:
        Tuple[bool, np.ndarray]: If the operation was
        successful and the next frame.
    """
    return resource.read()


def handle_read_failure(
        resource: cv2.VideoCapture
) -> None:
    """
    Corrects the issue with reading from the
    video file by resetting the videe pointer to 0.

    Args:
        resource (cv2.VideoCapture): The resource
        with which there is an issue.
    """
    resource.set(cv2.CAP_PROP_POS_FRAMES, 0)
