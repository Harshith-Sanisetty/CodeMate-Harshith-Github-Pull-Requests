

from abc import ABC, abstractmethod

class BaseConnector(ABC):
    """
    Abstract base class defining the interface for a Git server connector.
    """

    @abstractmethod
    def get_pr_metadata(self, pr_url: str) -> dict:
        """Fetches metadata (title, description) for a given PR URL."""
        pass

    @abstractmethod
    def get_pr_diff(self, pr_url: str) -> str:
        """Fetches the diff of a given PR URL as a string."""
        pass