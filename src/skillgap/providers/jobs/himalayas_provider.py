import requests

from skillgap.models.job import JobPosting
from skillgap.providers.jobs.base_provider import BaseJobProvider


class HimalayasProvider(BaseJobProvider):

    URL = "https://himalayas.app/jobs/api/search"

    def search_jobs(self, keyword: str) -> list[JobPosting]:
        response = requests.get(
            self.URL,
            params={"q": keyword, "limit": 50},
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        job_items = []
        if isinstance(data, dict):
            job_items = data.get("jobs", [])
        elif isinstance(data, list):
            job_items = data

        jobs = []
        keyword_lower = keyword.lower()
        for item in job_items:
            title = item.get("title", "")
            description = item.get("description", item.get("excerpt", ""))
            company = item.get("companyName", "")

            # Filter to ensure keyword actually appears in title
            if keyword_lower not in title.lower():
                continue

            # Build salary string
            min_sal = item.get("minSalary")
            max_sal = item.get("maxSalary")
            curr = item.get("salaryCurrency", "USD")
            salary_str = ""
            if min_sal is not None and max_sal is not None:
                salary_str = f"{min_sal} - {max_sal} {curr}"
            elif min_sal is not None:
                salary_str = f">= {min_sal} {curr}"

            jobs.append(
                JobPosting(
                    title=title,
                    company=company,
                    location=item.get("locationRestriction", item.get("location", "Remote")),
                    source="Himalayas",
                    url=item.get("url", ""),
                    description=description,
                    salary=salary_str,
                    remote=True,
                    posted_date=str(item.get("pubDate", ""))
                )
            )

        return jobs
