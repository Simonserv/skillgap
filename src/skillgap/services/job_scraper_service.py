import requests
from skillgap.models.job import JobPosting as Job


class JobScraperService:

    @staticmethod
    def fetch_remotive(keyword="software"):
        url = f"https://remotive.com/api/remote-jobs?search={keyword}"
        res = requests.get(url)
        data = res.json()

        jobs = []

        for item in data.get("jobs", []):
            jobs.append(Job(
                title=item.get("title", ""),
                company=item.get("company_name", ""),
                location=item.get("candidate_required_location", ""),
                url=item.get("url", ""),
                description=item.get("description", ""),
                source="remotive"
            ))

        return jobs


    @staticmethod
    def fetch_arbeitnow():
        url = "https://www.arbeitnow.com/api/job-board-api"
        res = requests.get(url)
        data = res.json()

        jobs = []

        for item in data.get("data", []):
            jobs.append(Job(
                title=item.get("title", ""),
                company=item.get("company_name", ""),
                location=item.get("location", ""),
                url=item.get("url", ""),
                description=item.get("description", ""),
                source="arbeitnow"
            ))

        return jobs


    @staticmethod
    def fetch_all(keyword="software"):
        jobs = []
        jobs.extend(JobScraperService.fetch_remotive(keyword))
        jobs.extend(JobScraperService.fetch_arbeitnow())
        return jobs