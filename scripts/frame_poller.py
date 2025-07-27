from app.database import (
    MongoDB,
    Frames,
    Event,
)
from app.messaging import (
    RabbitMQ,
    FrameMessage,
    REWARD_QUEUE,
)

mongo_client = MongoDB()
rabbit_mq = RabbitMQ()

# Polls from the MongoDB 'Frames' collection to collect documents
# with complete frame data. This is because frame data is gathered
# asnychronously in the MongoDB database.
for key in mongo_client.watch_collection(Frames, Event.UPDATE):
    document: FrameMessage = mongo_client.get_document_by_id(key)
    if (
        document.streamed_frame and
        document.reference_frame and
        document.latency
    ):
        # Publish to the reward calculation queue after
        # complete frame data is gathered.
        rabbit_mq.publish_to_queue(
            REWARD_QUEUE,
            FrameMessage(
                frame_number=document.frame_number,
                streamed_frame=document.streamed_frame,
                reference_frame=document.reference_frame,
                latency=document.latency
            )
        )
