import requests

from skillgap.models.job import JobPosting
from skillgap.providers.jobs.base_provider import BaseJobProvider


class ArbeitnowProvider(BaseJobProvider):

    URL = "https://www.arbeitnow.com/api/job-board-api"

    def search_jobs(self, keyword: str) -> list[JobPosting]:

        response = requests.get(self.URL, timeout=30)

        response.raise_for_status()

        jobs = []

        keyword = keyword.lower()

        for item in response.json().get("data", []):

            title = item.get("title", "")

            description = item.get("description", "")

            if keyword not in title.lower():
                continue

            jobs.append(
                JobPosting(
                    title=title,
                    company=item.get("company_name", ""),
                    location=item.get("location", ""),
                    source="Arbeitnow",
                    url=item.get("url", ""),
                    description=description,
                    remote=True
                )
            )

        return jobs