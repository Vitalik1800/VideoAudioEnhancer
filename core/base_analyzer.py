from abc import ABC, abstractmethod


class BaseAnalyzer(ABC):
    """Base class for analysis components."""

    @abstractmethod
    def process(self, input_path: str) -> dict:
        """Analyze input data and return analysis results."""

        raise NotImplementedError
