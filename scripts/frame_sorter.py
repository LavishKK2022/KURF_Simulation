from functools import partial
from app.messaging import (
    AGGREGATE_QUEUE,
    PartialMessage,
    RabbitMQ,
)
from app.database import (
    MongoDB,
    Frames,
    field,
    get_other_fields
)
from app.utils import (
    setup_consumer,
)

mongo_client = MongoDB()


def upsert_to_database(payload: PartialMessage) -> None:
    """
    Upserts partail frames to the database.
    This aids in aggregating frames and their correlated data
    by gruoping frames based on their frame number.

    This matches the referenced frames, streamed frames and
    the latency values.

    Args:
        payload (PartialMessage): The partial data to upsert.

    Raises:
        KeyError: If no data is sent in the payload.
    """
    # Partial function for the MongoDB upsert.
    upsert = partial(
        mongo_client.upsert_document,
        Frames,
        {field(Frames, 'frame_number'): payload.frame_number}
    )

    # By using '$setOnInsert' the collection schema is adhered to.
    if payload.latency:
        latency_field = field(Frames, 'latency')
        upsert(
            {
                '$set': {latency_field: payload.latency},
                '$setOnInsert': get_other_fields(Frames, latency_field)
            }
        )
    elif payload.reference_frame:
        reference_field = field(Frames, 'reference_frame')
        upsert(
            {
                '$set': {reference_field: payload.reference_frame},
                '$setOnInsert': get_other_fields(Frames, reference_field)
            }
        )
    elif payload.streamed_frame:
        streamed_field = field(Frames, 'streamed_frame')
        upsert(
            {
                '$set': {streamed_field: payload.streamed_frame},
                '$setOnInsert': get_other_fields(Frames, streamed_field)
            }
        )
    else:
        raise KeyError('Malformed Request: Frame Sorter')


if __name__ == '__main__':
    """ Boilerplate for RabbitMQ consumer """
    setup_consumer(
        client=RabbitMQ(),
        subscribe_queue=AGGREGATE_QUEUE,
        callback=upsert_to_database,
        expected_format=PartialMessage
    )
