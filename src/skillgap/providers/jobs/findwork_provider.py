import os
import requests
import logging

from skillgap.models.job import JobPosting
from skillgap.providers.jobs.base_provider import BaseJobProvider

logger = logging.getLogger(__name__)


class FindworkProvider(BaseJobProvider):

    URL = "https://findwork.dev/api/jobs/"

    def search_jobs(self, keyword: str) -> list[JobPosting]:
        token = os.getenv("FINDWORK_API_KEY") or os.getenv("FINDWORK_TOKEN")

        if not token:
            logger.warning("Findwork token (FINDWORK_API_KEY) not found. Skipping Findwork provider.")
            return []

        headers = {
            "Authorization": f"Token {token}"
        }
        params = {
            "search": keyword
        }

        try:
            response = requests.get(self.URL, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Error fetching from Findwork API: {e}")
            return []

        jobs = []
        keyword_lower = keyword.lower()
        # Findwork returns a paginated response with a "results" list
        for item in data.get("results", []):
            title = item.get("role", "")
            description = item.get("text", "")
            company = item.get("company_name", "")

            # Filter to ensure keyword actually appears in title
            if keyword_lower not in title.lower():
                continue

            # Parse remote field from location or description
            location = item.get("location", "")
            remote = False
            if item.get("remote") or "remote" in location.lower():
                remote = True

            jobs.append(
                JobPosting(
                    title=title,
                    company=company,
                    location=location,
                    source="Findwork",
                    url=item.get("url", ""),
                    description=description,
                    salary="",
                    remote=remote,
                    posted_date=item.get("date_posted", "")
                )
            )

        return jobs
