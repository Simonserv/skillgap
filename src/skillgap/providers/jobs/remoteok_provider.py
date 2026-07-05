import requests

from skillgap.models.job import JobPosting
from skillgap.providers.jobs.base_provider import BaseJobProvider


class RemoteOKProvider(BaseJobProvider):

    URL = "https://remoteok.com/api"

    def search_jobs(self, keyword: str) -> list[JobPosting]:
        # RemoteOK requires a realistic User-Agent to avoid being blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(self.URL, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, list) or len(data) <= 1:
            return []

        jobs = []
        keyword = keyword.lower()

        # The first element is typically a metadata/license object, skip it
        for item in data[1:]:
            title = item.get("position", "")
            description = item.get("description", "")
            tags = [t.lower() for t in item.get("tags", [])]

            # Filter by keyword in title only
            if keyword not in title.lower():
                continue

            # Parse salary
            sal_min = item.get("salary_min")
            sal_max = item.get("salary_max")
            sal_curr = item.get("salary_currency", "USD")
            salary_str = ""
            if sal_min is not None and sal_max is not None:
                salary_str = f"{sal_min} - {sal_max} {sal_curr}"
            elif sal_min is not None:
                salary_str = f">= {sal_min} {sal_curr}"

            jobs.append(
                JobPosting(
                    title=title,
                    company=item.get("company", ""),
                    location=item.get("location", ""),
                    source="RemoteOK",
                    url=item.get("url", ""),
                    description=description,
                    salary=salary_str,
                    remote=True,
                    posted_date=item.get("date", "")
                )
            )

        return jobs
