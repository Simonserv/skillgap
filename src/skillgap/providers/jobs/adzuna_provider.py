import os
import requests
import logging

from skillgap.models.job import JobPosting
from skillgap.providers.jobs.base_provider import BaseJobProvider

logger = logging.getLogger(__name__)


class AdzunaProvider(BaseJobProvider):

    URL_TEMPLATE = "https://api.adzuna.com/v1/api/jobs/{country}/search/1"

    def search_jobs(self, keyword: str) -> list[JobPosting]:
        app_id = os.getenv("ee8b7f78")
        app_key = os.getenv("e0167c71682560e172f47ed00661850e")
        country = os.getenv("ADZUNA_COUNTRY", "ph")  # default to PH per handoff priority

        if not app_id or not app_key:
            logger.warning("Adzuna credentials (ADZUNA_APP_ID/ADZUNA_APP_KEY) not found. Skipping Adzuna provider.")
            return []

        url = self.URL_TEMPLATE.format(country=country)
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "what": keyword,
            "content-type": "application/json"
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Error fetching from Adzuna API: {e}")
            return []

        jobs = []
        keyword_lower = keyword.lower()
        for item in data.get("results", []):
            company_info = item.get("company", {})
            company_name = company_info.get("display_name", "") if isinstance(company_info, dict) else ""
            title = item.get("title", "")
            description = item.get("description", "")

            # Filter to ensure keyword actually appears in title
            if keyword_lower not in title.lower():
                continue

            loc_info = item.get("location", {})
            location_name = ", ".join(loc_info.get("area", [])) if isinstance(loc_info, dict) else ""

            # Check if job is remote (Adzuna tags or description search)
            remote = False
            if "remote" in title.lower() or "remote" in description.lower() or item.get("salary_is_predicted") == "remote":
                remote = True

            min_sal = item.get("salary_min")
            max_sal = item.get("salary_max")
            salary_str = ""
            if min_sal is not None and max_sal is not None:
                salary_str = f"{min_sal} - {max_sal} PHP"
            elif min_sal is not None:
                salary_str = f">= {min_sal} PHP"

            jobs.append(
                JobPosting(
                    title=title,
                    company=company_name,
                    location=location_name or item.get("location", {}).get("display_name", "Philippines"),
                    source="Adzuna",
                    url=item.get("redirect_url", ""),
                    description=description,
                    salary=salary_str,
                    remote=remote,
                    posted_date=item.get("created", "")
                )
            )

        return jobs
