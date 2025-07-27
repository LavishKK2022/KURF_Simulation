import os
from enum import (
    Enum,
    IntEnum,
)

# The number of frames to process before
# a decision is made.
PROCESS_FRAMES = os.getenv('FRAMES', 60)

# Identifies the base folder, structured
# as per the demonstration above.
VIDEO_FOLDER = os.getenv('SOURCE')

# The weight of the cosine similarity
# in the reward model.
SIM_WEIGHT = os.getenv('S_WEIGHT', 1.0)

# The weight of the latency value
# in the reward model.
LATENCY_WEIGHT = os.getenv('L_WEIGHT', 0.001)


class Decision(IntEnum):
    """ Defines stream decision """
    STREAM = 1
    LOCAL = 0


class Folder(str, Enum):
    """ Defines the folder structure """
    STREAM = 'stream'
    LOCAL = 'local'


class Files(str, Enum):
    """ Defines the file structure """
    REFERENCE = 'reference'
    STREAMED = 'streamed'
    LATENCY = 'latency'
