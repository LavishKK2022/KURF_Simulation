import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from torchvision.models import VGG16_Weights
from app.messaging import (
    RabbitMQ,
    FrameMessage,
    LogMessage,
    REWARD_QUEUE,
    LOGS_EXCHANGE,
)
from app.database import (
    MongoDB,
    Results,
)
from app.utils import (
    setup_consumer,
    str_to_image,
)
from app.config import (
    LATENCY_WEIGHT,
    SIM_WEIGHT,
)


mongo_client = MongoDB()
rabbit_mq = RabbitMQ()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

vgg = models.vgg16(
    weights=VGG16_Weights.IMAGENET1K_V1
).features.to(device).eval()

transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])


def extract_vgg_features(frame: np.ndarray) -> np.ndarray:
    """
    Extract features from the given frame.

    Args:
        frame (np.ndarray): A frame (stream/reference) from
        the source.

    Returns:
        np.ndarray: extracted features.
    """
    frame = transform(frame).unsqueeze(0).to(device)
    with torch.no_grad():
        features = vgg(frame)
    return features.cpu().numpy().flatten()


def cosine_similarity(
        vec1: np.ndarray,
        vec2: np.ndarray
) -> float:
    """
    Calculate the similarity between frames.
    This calculation is often done between the streamed
    and the reference frames.

    Args:
        vec1 (np.ndarray): Frame to compare.
        vec2 (np.ndarray): Frame to compare with.

    Returns:
        float: Cosine similarity of the frames.
    """
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def calculate_reward(payload: FrameMessage) -> None:
    """
    Calculate the reward for the given frame, by comparing the
    streamed frame to the reference frame and subtracting a score
    for the latency.

    Args:
        payload (FrameMessage): The message containing all related joined
        data for the streamed frame, reference frame and latency.
    """
    streamed_frame = str_to_image(payload.streamed_frame)
    reference_frame = str_to_image(payload.reference_frame)
    similarity = cosine_similarity(
        extract_vgg_features(streamed_frame),
        extract_vgg_features(reference_frame)
    )

    # Publishing the reward in the 'Results' database collection.
    result = (SIM_WEIGHT * similarity) - (LATENCY_WEIGHT * payload.latency)
    mongo_client.insert_document(
        Results,
        Results(
            frame_number=payload.frame_number,
            result=result
        )
    )
    # Publishing the reward in the LOGS_EXCHANGE.
    rabbit_mq.publish(
        exchange=LOGS_EXCHANGE,
        message=LogMessage(
            terminal_message=f'reward for {payload.frame_number} is {result}',
            file_message=f'{payload.frame_number}: {result}'
        )
    )


if __name__ == '__main__':
    """ Boilerplate for the RabbitMQ consumer """
    setup_consumer(
        client=RabbitMQ(),
        subscribe_queue=REWARD_QUEUE,
        callback=calculate_reward,
        expected_format=FrameMessage
    )
