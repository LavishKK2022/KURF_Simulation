from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)
from typing import (
    Optional,
)
from bson.objectid import (
    ObjectId,
)


class MongoModel(BaseModel):
    """
    BaseModel for MongoDB Collections.
    Each collection often features an _id by default.

    Model's that subclass this model, will be preconfigured
    to forbid extra fields and can submit data to this model
    using the id (or _id alias).

    Args:
        BaseModel: Pydantic model superclass.
    """
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True,
        validate_by_name=True,
        validate_by_alias=True
    )


class Frames(MongoModel):
    """
    The 'Frames' collection. This embodies the construction
    of a frame.

    It contains all the data relating to a streamed frame and
    enables the calculation of a reward.

    This is the format of its storage in the MongoDB database.

    Args:
        MongoModel: Custom Pydantic model superclass.
    """
    frame_number: int
    reference_frame: str
    streamed_frame: str
    frame_latency: float


class Results(MongoModel):
    """
    The 'Results' collection. This embodies the construction
    of a result.

    It contains all the data relating to a calculated reward and
    enables the decision making for this simulation.

    This is the format of its storage in the MongoDB database.

    Args:
        MongoModel: Custom Pydantic model superclass.
    """
    frame_number: int
    result: float
