import json

from skillgap.models.resume_schema import RESUME_SCHEMA
from skillgap.models.job_schema import JOB_SCHEMA


class AIPrompts:

    @staticmethod
    def resume_prompt(resume_text: str) -> str:

        return f"""
You are an expert resume parser.

Return ONLY valid JSON.

Never explain.

Never invent information.

Follow this schema exactly:

{json.dumps(RESUME_SCHEMA, indent=2)}

Resume:

{resume_text}
"""

    @staticmethod
    def job_prompt(title: str, description: str) -> str:

        return f"""
You are an expert technical recruiter.

Read the job posting.

Extract structured information.

Return ONLY JSON.

Industry should be ONE primary industry.

Role category should be ONE standardized role.

Schema:

{json.dumps(JOB_SCHEMA, indent=2)}

Title:

{title}

Description:

{description}
"""