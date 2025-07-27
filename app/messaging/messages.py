from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator
)
from typing import (
    Self,
    Optional
)
from app.config import Decision


class RabbitMQModel(BaseModel):
    """
    Base model for the RabbitMQ messaging models.
    This ensures extra fields are rejected.

    Args:
        BaseModel: Pydantic Base Model.
    """
    model_config = ConfigDict(extra='forbid')


class LogMessage(RabbitMQModel):
    """ Represent file and terminal log messages """
    terminal_message: str
    file_message: str


class FrameMessage(RabbitMQModel):
    """ Represent complete frame data """
    frame_number: int
    streamed_frame: str
    reference_frame: str
    latency: float


class PathMessage(RabbitMQModel):
    """ Represent new streaming path """
    path: str


class DecisionMessage(RabbitMQModel):
    """ Represent streaming decision """
    decision: Decision


class PartialMessage(RabbitMQModel):
    """ Represent partial message for frame data """
    frame_number: int
    streamed_frame: Optional[str] = None
    reference_frame: Optional[str] = None
    latency: Optional[float] = None

    @model_validator(mode='after')
    def ensure_fields(self) -> Self:
        """
        Custom validator to ensure only 'frame_number' (required)
        and one additional field is provided.

        Raises:
            ValueError: If more fields are provided.

        Returns:
            Self: Pydantic BaseModel requirement.
        """
        field_count = sum(
            1
            for v in self.__dict__.values()
            if v is not None
        )
        # BaseModel validation occurs before this validator is run.
        # As required the variable 'frame_number' will be provided.
        # This check ensures that only one additional field is given.
        if field_count != 2:
            raise ValueError('Partial Field Mismatch')
        return self
