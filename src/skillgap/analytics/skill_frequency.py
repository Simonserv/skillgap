import json
from collections import Counter
from pathlib import Path


class SkillFrequencyAnalyzer:

    @staticmethod
    def analyze_frequencies(
        jobs: list[dict],
        role_category: str = None,
        industry: str = None
    ) -> dict[str, float]:
        """
        Calculates the percentage frequency of each skill.
        Can be filtered by role_category or industry.
        """
        filtered_jobs = jobs

        if role_category:
            role_category_lower = role_category.lower()
            filtered_jobs = [
                j for j in filtered_jobs
                if j.get("role_category", "").lower() == role_category_lower
            ]

        if industry:
            industry_lower = industry.lower()
            filtered_jobs = [
                j for j in filtered_jobs
                if j.get("industry", "").lower() == industry_lower
            ]

        total_jobs = len(filtered_jobs)
        if total_jobs == 0:
            return {}

        skill_counter = Counter()
        for job in filtered_jobs:
            skills = job.get("skills", [])
            # Deduplicate skills within the same job posting (case-insensitive grouping)
            seen = set()
            for skill in skills:
                normalized = skill.strip()
                if normalized.lower() not in seen:
                    seen.add(normalized.lower())
                    skill_counter[normalized] += 1

        # Calculate percentages
        frequencies = {
            skill: round((count / total_jobs), 4)
            for skill, count in skill_counter.items()
        }

        # Sort by frequency descending
        return dict(sorted(frequencies.items(), key=lambda x: x[1], reverse=True))

    @classmethod
    def analyze_from_file(
        cls,
        filepath: str | Path,
        role_category: str = None,
        industry: str = None
    ) -> dict[str, float]:
        """
        Helper method to analyze frequencies directly from a dataset JSON file.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                jobs = json.load(f)
            return cls.analyze_frequencies(jobs, role_category, industry)
        except Exception:
            return {}
