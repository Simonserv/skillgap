from skillgap.models.resume import ResumeProfile


class ResumeMapper:

    @staticmethod
    def to_profile(ai_data: dict) -> ResumeProfile:

        profile = ResumeProfile()

        # basic info
        profile.name = ai_data.get("name", "")
        profile.email = ai_data.get("email", "")
        profile.phone = ai_data.get("phone", "")
        profile.summary = ai_data.get("summary", "")

        # structured fields
        profile.education = ai_data.get("education", [])
        profile.experience = ai_data.get("experience", [])
        profile.projects = ai_data.get("projects", [])

        profile.skills = ai_data.get("skills", {})

        profile.certifications = ai_data.get("certifications", [])
        profile.awards = ai_data.get("awards", [])
        profile.organizations = ai_data.get("organizations", [])
        profile.languages = ai_data.get("languages", [])

        return profile