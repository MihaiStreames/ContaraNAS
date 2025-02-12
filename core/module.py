from abc import ABC, abstractmethod


class Module(ABC):
    def __init__(self, main_window):
        self.main_window = main_window

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def execute(self):
        pass
