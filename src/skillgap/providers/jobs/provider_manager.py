from concurrent.futures import ThreadPoolExecutor, as_completed

from skillgap.models.job import JobPosting
from skillgap.providers.jobs.base_provider import BaseJobProvider


class ProviderManager:
    """
    Executes multiple job providers concurrently.
    """

    def __init__(self, providers: list[BaseJobProvider]):
        self.providers = providers

    def search(self, keyword: str) -> list[JobPosting]:

        jobs: list[JobPosting] = []

        with ThreadPoolExecutor(max_workers=len(self.providers)) as executor:

            futures = {
                executor.submit(provider.search_jobs, keyword): provider
                for provider in self.providers
            }

            for future in as_completed(futures):

                provider = futures[future]

                try:
                    jobs.extend(future.result())

                except Exception as e:
                    print(f"[{provider.__class__.__name__}] {e}")

        return jobs