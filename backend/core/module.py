from abc import ABC, abstractmethod


class Module(ABC):
    @abstractmethod
    def get_module_info(self):
        """Get basic module information"""
        pass

    @abstractmethod
    def get_tile_data(self):
        """Get data for dashboard tile display"""
        pass
