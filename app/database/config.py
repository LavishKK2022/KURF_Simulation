from enum import Enum

# The URL string for the local MongoDB server.
URL = "mongodb://localhost:27017/"

# The database this pipeline works with.
DATABASE = "simulation"


class Event(str, Enum):
    """ Codifies the operations that can be 'watched' on MongoDB """

    INSERT = 'insert'
    UPDATE = 'update'
    REPLACE = 'replace'
    DELETE = 'delete'
