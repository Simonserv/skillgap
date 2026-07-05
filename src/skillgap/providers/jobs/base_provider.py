from abc import ABC, abstractmethod

from skillgap.models.job import JobPosting


class BaseJobProvider(ABC):
    """
    Base interface implemented by every job provider.
    """

    @abstractmethod
    def search_jobs(self, keyword: str) -> list[JobPosting]:
        raise NotImplementedError