from abc import ABC, abstractmethod


class BaseEnhancer(ABC):
    """Base class for enhancement components."""

    @abstractmethod
    def enhance(self, input_path: str, output_path: str) -> str:
        """Enhance input data and return the output path."""

        raise NotImplementedError
