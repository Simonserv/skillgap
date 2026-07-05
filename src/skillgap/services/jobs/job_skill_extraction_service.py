from skillgap.models.job import JobPosting
from skillgap.services.ai_prompts import AIPrompts
from skillgap.services.ai_service import AIService


class JobSkillExtractionService:

    @staticmethod
    def enrich(job: JobPosting) -> JobPosting:
        """
        Uses AI to enrich a JobPosting with structured metadata.
        """

        ai = AIService()

        prompt = AIPrompts.job_prompt(
            job.title,
            job.description
        )

        data = ai.generate_json(prompt)

        job.skills = data.get("skills", [])
        job.seniority = data.get("seniority", "")
        job.role_category = data.get("role_category", "")
        job.industry = data.get("industry", "")

        return job