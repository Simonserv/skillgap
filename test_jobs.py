from skillgap.services.jobs.job_aggregator_service import JobAggregatorService
from skillgap.services.jobs.job_skill_extraction_service import JobSkillExtractionService

service = JobAggregatorService()

jobs = service.fetch_jobs("backend")

print(f"Fetched {len(jobs)} jobs\n")

job = jobs[0]

print("=" * 80)
print(job.title)
print("=" * 80)

job = JobSkillExtractionService.enrich(job)

print("\nSkills:")
print(job.skills)

print("\nSeniority:")
print(job.seniority)

print("\nRole:")
print(job.role_category)

print("\nIndustry:")
print(job.industry)