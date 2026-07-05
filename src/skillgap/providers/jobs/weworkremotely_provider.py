import xml.etree.ElementTree as ET
import requests

from skillgap.models.job import JobPosting
from skillgap.providers.jobs.base_provider import BaseJobProvider


class WeWorkRemotelyProvider(BaseJobProvider):

    URL = "https://weworkremotely.com/remote-jobs.rss"

    def search_jobs(self, keyword: str) -> list[JobPosting]:
        response = requests.get(self.URL, timeout=30)
        response.raise_for_status()

        # Parse RSS XML
        root = ET.fromstring(response.content)
        jobs = []
        keyword = keyword.lower()

        for item in root.findall(".//item"):
            title_text = item.find("title")
            title = title_text.text if title_text is not None else ""

            desc_node = item.find("description")
            description = desc_node.text if desc_node is not None else ""

            # Filter by keyword in title only
            if keyword not in title.lower():
                continue

            link_node = item.find("link")
            url = link_node.text if link_node is not None else ""

            pub_node = item.find("pubDate")
            posted_date = pub_node.text if pub_node is not None else ""

            # WeWorkRemotely RSS title format is typically "Company: Position Name (Category)"
            company = ""
            position_title = title
            if ":" in title:
                parts = title.split(":", 1)
                company = parts[0].strip()
                position_title = parts[1].strip()

            jobs.append(
                JobPosting(
                    title=position_title,
                    company=company,
                    location="Remote",
                    source="WeWorkRemotely",
                    url=url,
                    description=description,
                    remote=True,
                    posted_date=posted_date
                )
            )

        return jobs
