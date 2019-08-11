from abc import abstractmethod, ABC


class Base(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def save_to_db(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass
