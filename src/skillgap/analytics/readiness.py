import re
from datetime import date
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skillgap.models.resume import ResumeProfile
from skillgap.models.job import JobPosting


class ReadinessScorer:

    @staticmethod
    def flatten_resume_skills(skills_data) -> set[str]:
        """
        Recursively flattens any skills dictionary or list into a set of lowercase strings.
        """
        flat_skills = set()

        if isinstance(skills_data, list):
            for item in skills_data:
                if isinstance(item, str):
                    flat_skills.add(item.strip().lower())
                else:
                    flat_skills.update(ReadinessScorer.flatten_resume_skills(item))
        elif isinstance(skills_data, dict):
            for k, v in skills_data.items():
                if isinstance(k, str):
                    flat_skills.add(k.strip().lower())
                flat_skills.update(ReadinessScorer.flatten_resume_skills(v))
        elif isinstance(skills_data, str):
            flat_skills.add(skills_data.strip().lower())

        return {s for s in flat_skills if s}

    @staticmethod
    def parse_date(date_str: str, default_to_now: bool = False) -> date:
        """
        Robustly parses year and month from a date string.
        Falls back to current date if default_to_now is True.
        """
        current_date = date(2026, 7, 4)  # Current local time from metadata
        if not date_str:
            return current_date if default_to_now else date(2000, 1, 1)

        date_str_clean = str(date_str).strip().lower()
        if date_str_clean in ("present", "current", "now", "today", "active", ""):
            return current_date

        # Look for a 4-digit year
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', date_str_clean)
        year = int(year_match.group(1)) if year_match else (2026 if default_to_now else 2000)

        # Look for month name or number
        month = 1
        months_map = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
            "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
            "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
        }

        # Check for month names
        found_month = False
        for m_name, m_num in months_map.items():
            if m_name in date_str_clean:
                month = m_num
                found_month = True
                break

        if not found_month:
            # Check for month numbers (e.g. 05/2021 or 2021-05)
            month_match = re.search(r'\b(0?[1-9]|1[0-2])\b', date_str_clean)
            if month_match:
                month = int(month_match.group(1))

        return date(year, month, 1)

    @staticmethod
    def calculate_total_experience_years(experience: list[dict]) -> float:
        """
        Calculates total years of experience from a list of experience records.
        """
        total_months = 0.0

        for exp in experience:
            start_str = exp.get("start_date", "")
            end_str = exp.get("end_date", "")

            # Parse dates
            start_date = ReadinessScorer.parse_date(start_str, default_to_now=False)
            end_date = ReadinessScorer.parse_date(end_str, default_to_now=True)

            if end_date >= start_date:
                months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                # Count at least 1 month if start and end dates are specified and valid
                total_months += max(1.0, float(months))

        return round(total_months / 12.0, 2)

    @staticmethod
    def get_expected_experience_years(seniority: str) -> float:
        """
        Maps seniority levels to expected years of experience.
        """
        seniority_lower = str(seniority).lower().strip()
        if "lead" in seniority_lower or "principal" in seniority_lower or "manager" in seniority_lower:
            return 8.0
        elif "senior" in seniority_lower:
            return 6.0
        elif "mid" in seniority_lower or "associate" in seniority_lower:
            return 3.0
        elif "junior" in seniority_lower or "entry" in seniority_lower or "intern" in seniority_lower:
            return 1.0
        return 3.0  # default fallback

    @staticmethod
    def calculate_readiness(
        profile: ResumeProfile,
        job: JobPosting,
        additional_skills: set[str] = None
    ) -> dict:
        """
        Calculates the JobMatch composite readiness score:
        - Semantic Similarity: 50%
        - Skill Match: 35%
        - Experience Match: 15%
        """
        # 1. Semantic Similarity (50%)
        # Build text corpus for resume profile
        resume_text_parts = [profile.summary]
        for exp in profile.experience:
            desc = " ".join(exp.get("description", [])) if isinstance(exp.get("description"), list) else str(exp.get("description", ""))
            resume_text_parts.append(f"{exp.get('position', '')} {exp.get('company', '')} {desc}")
        for proj in profile.projects:
            tech = " ".join(proj.get("technologies", []))
            resume_text_parts.append(f"{proj.get('title', '')} {proj.get('description', '')} {tech}")

        resume_corpus = " ".join(resume_text_parts).strip()
        job_corpus = f"{job.title} {job.description}".strip()

        semantic_score = 0.0
        if resume_corpus and job_corpus:
            try:
                vectorizer = TfidfVectorizer(stop_words='english', use_idf=False)
                tfidf = vectorizer.fit_transform([resume_corpus, job_corpus])
                raw_similarity = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
                # Boost the raw similarity to a realistic, recruiter-friendly scale
                semantic_score = min(1.0, raw_similarity * 2.2)
            except Exception:
                semantic_score = 0.0

        # 2. Skill Matching (35%)
        resume_skills = ReadinessScorer.flatten_resume_skills(profile.skills)
        if additional_skills:
            resume_skills.update(s.lower().strip() for s in additional_skills)

        job_skills = {s.lower().strip() for s in job.skills if s}
        
        skill_score = 0.0
        matched_skills = []
        missing_skills = []
        if job_skills:
            matched_skills = list(job_skills.intersection(resume_skills))
            missing_skills = list(job_skills.difference(resume_skills))
            skill_score = len(matched_skills) / len(job_skills)

        # 3. Experience Matching (15%)
        candidate_years = ReadinessScorer.calculate_total_experience_years(profile.experience)
        expected_years = ReadinessScorer.get_expected_experience_years(job.seniority)

        if expected_years <= 0:
            exp_score = 1.0
        else:
            exp_score = min(1.0, candidate_years / expected_years)

        # Composite Score
        composite_score = 0.50 * semantic_score + 0.35 * skill_score + 0.15 * exp_score

        return {
            "readiness_score": round(composite_score * 100, 2),
            "breakdown": {
                "semantic_similarity": {
                    "weight": 0.50,
                    "score": round(semantic_score * 100, 2)
                },
                "skill_matching": {
                    "weight": 0.35,
                    "score": round(skill_score * 100, 2),
                    "matched": matched_skills,
                    "missing": missing_skills
                },
                "experience_matching": {
                    "weight": 0.15,
                    "score": round(exp_score * 100, 2),
                    "candidate_years": candidate_years,
                    "expected_years": expected_years
                }
            }
        }
