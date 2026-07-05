import json
from collections import defaultdict
from pathlib import Path


class SkillCorrelationAnalyzer:

    @staticmethod
    def get_correlations(jobs: list[dict], target_skill: str, top_n: int = 5) -> list[dict]:
        """
        Calculates conditional probabilities P(Skill B | target_skill).
        Returns top_n co-occurring skills sorted by probability.
        """
        target_skill_lower = target_skill.lower().strip()
        
        target_count = 0
        co_counts = defaultdict(int)

        for job in jobs:
            skills = [s.strip() for s in job.get("skills", [])]
            skills_lower = [s.lower() for s in skills]

            if target_skill_lower in skills_lower:
                target_count += 1
                for s in skills:
                    if s.lower() != target_skill_lower:
                        co_counts[s] += 1

        if target_count == 0:
            return []

        correlations = []
        for skill, count in co_counts.items():
            prob = count / target_count
            correlations.append({
                "skill": skill,
                "probability": round(prob, 4),
                "co_occurrences": count,
                "target_total": target_count
            })

        # Sort by probability descending
        correlations.sort(key=lambda x: x["probability"], reverse=True)
        return correlations[:top_n]

    @classmethod
    def get_correlations_from_file(
        cls,
        filepath: str | Path,
        target_skill: str,
        top_n: int = 5
    ) -> list[dict]:
        """
        Helper method to calculate correlations directly from a dataset JSON file.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                jobs = json.load(f)
            return cls.get_correlations(jobs, target_skill, top_n)
        except Exception:
            return []
