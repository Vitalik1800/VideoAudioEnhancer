from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    """Base class for processing components."""

    @abstractmethod
    def process(self, input_path: str, output_path: str) -> str:
        """Process input data and return the output path."""

        raise NotImplementedError
