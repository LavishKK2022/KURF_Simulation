import logging
import logging.config
from logging import Logger
from typing import (
    Dict,
    Any,
)

# The logging definition for the terminal output.
stdout_logging_config = {
    'version': 1,
    'disable_existing_logging': False,
    'formatters': {
        'simple': {
            'format': '[%(levelname)s @ %(asctime)s]: %(message)s'
        }
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        'root': {'level': 'DEBUG', 'handlers': ['stdout']}
    },
}

# The logging definition for the file output.
file_logging_config = {
    'version': 1,
    'disable_existing_logging': False,
    'formatters': {
        'simple': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': 'simulation.log'
        }
    },
    'loggers': {
        'root': {'level': 'DEBUG', 'handlers': ['file']}
    },
}


def setup_logging(config: Dict[str, Any]) -> Logger:
    """
    Helper method to instantiate logging with the
    logging definitions listed above.

    Args:
        config (Dict[str, Any]): The logging dictionaries
        as defined above.

    Returns:
        Logger: The logging object, from which
        logs can be created.
    """
    logging.config.dictConfig(config=config)
    return logging.getLogger('KURF_SIMULATION')
