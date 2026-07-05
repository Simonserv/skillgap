from skillgap.models.job import JobPosting

from skillgap.providers.jobs.provider_manager import ProviderManager
from skillgap.providers.jobs.remotive_provider import RemotiveProvider
from skillgap.providers.jobs.arbeitnow_provider import ArbeitnowProvider
from skillgap.providers.jobs.remoteok_provider import RemoteOKProvider
from skillgap.providers.jobs.himalayas_provider import HimalayasProvider
from skillgap.providers.jobs.weworkremotely_provider import WeWorkRemotelyProvider
from skillgap.providers.jobs.adzuna_provider import AdzunaProvider
from skillgap.providers.jobs.findwork_provider import FindworkProvider

from skillgap.services.jobs.job_deduplicator import JobDeduplicator


class JobAggregatorService:

    def __init__(self):

        self.provider_manager = ProviderManager(
            [
                RemotiveProvider(),
                ArbeitnowProvider(),
                RemoteOKProvider(),
                HimalayasProvider(),
                WeWorkRemotelyProvider(),
                AdzunaProvider(),
                FindworkProvider(),
            ]
        )

    def fetch_jobs(self, keyword: str) -> list[JobPosting]:

        jobs = self.provider_manager.search(keyword)

        jobs = JobDeduplicator.deduplicate(jobs)

        return jobs