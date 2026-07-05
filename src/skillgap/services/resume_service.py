from skillgap.models.resume import ResumeProfile

from skillgap.services.pdf_service import PDFService
from skillgap.services.ai_prompts import AIPrompts
from skillgap.services.resume_mapper import ResumeMapper
from skillgap.services.ai_service import AIService

class ResumeService:
    @staticmethod
    def process_resume(pdf_path: str) -> ResumeProfile:
        # Step 1: Extract text from the PDF
        resume_text = PDFService.extract_text(pdf_path)

        # Step 2: Ask the AI to parse it
        ai = AIService()

        prompt = AIPrompts.resume_prompt(resume_text)

        ai_data = ai.generate_json(prompt)

        # Step 3: Convert JSON to ResumeProfile
        profile = ResumeMapper.to_profile(ai_data)

        return profile