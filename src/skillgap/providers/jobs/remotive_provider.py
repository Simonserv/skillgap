import requests

from skillgap.models.job import JobPosting
from skillgap.providers.jobs.base_provider import BaseJobProvider


class RemotiveProvider(BaseJobProvider):

    URL = "https://remotive.com/api/remote-jobs"

    def search_jobs(self, keyword: str) -> list[JobPosting]:

        response = requests.get(
            self.URL,
            params={"search": keyword},
            timeout=30
        )

        response.raise_for_status()

        jobs = []

        keyword_lower = keyword.lower()
        for item in response.json().get("jobs", []):
            title = item.get("title", "")
            description = item.get("description", "")
            company = item.get("company_name", "")

            # Filter to ensure keyword actually appears in title
            if keyword_lower not in title.lower():
                continue

            jobs.append(
                JobPosting(
                    title=title,
                    company=company,
                    location=item.get("candidate_required_location", ""),
                    source="Remotive",
                    url=item.get("url", ""),
                    description=description,
                    salary=item.get("salary", ""),
                    remote=True,
                    posted_date=item.get("publication_date", "")
                )
            )

        return jobs