from skillgap.models.job import JobPosting


class JobDeduplicator:
    """
    Removes duplicate jobs coming from different providers.
    """

    @staticmethod
    def deduplicate(jobs: list[JobPosting]) -> list[JobPosting]:

        unique = {}

        for job in jobs:

            key = (
                job.title.strip().lower(),
                job.company.strip().lower(),
                job.location.strip().lower(),
            )

            if key not in unique:
                unique[key] = job

        return list(unique.values())