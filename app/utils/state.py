import threading


class PathHolder:
    """ Singleton mutable object to hold the current path """
    _instance = None

    def __new__(cls):
        """ Method to ensure singleton """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialise the path and threading lock.
            cls._instance._path = ''
            cls._instance._lock = threading.Lock()
        return cls._instance

    @property
    def path(self) -> str:
        """
        Retrieves the path from the object by
        applying the threading lock.

        Returns:
            str: The current path.
        """
        with self._lock:
            return self._path

    @path.setter
    def path(self, new_path: str) -> None:
        """
        Sets the path for the object by
        applying the threading lock.

        Args:
            new_path (str): The new path to update.
        """
        with self._lock:
            self._path = new_path


class FrameCount:
    """ Singleton mutable object to hold the frame count """
    _instance = None

    def __new__(cls):
        """ Method to ensure singleton """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialise the count.
            cls._instance._count = 0
        return cls._instance

    @property
    def count(self) -> int:
        """
        Retrieve the current count.

        Returns:
            int: The current count.
        """
        return self._count

    @count.setter
    def count(self, new_count: int) -> None:
        """
        Sets the new count.
        This is to be used internally.

        Args:
            new_count (int): The new count.
        """
        self._count = new_count

    def increment(self) -> None:
        """ Increment the counter object  """
        self.count += 1
