class RecommendationConfidenceCalculator:

    @staticmethod
    def calculate_confidence(
        skill_name: str,
        skill_frequency_in_role: float,  # Percentage frequency of the skill (0.0 to 1.0)
        course_difficulty: str = None,
        candidate_seniority: str = None
    ) -> float:
        """
        Calculates a confidence score (0.0 to 100.0) for a recommended action/course.
        Weights:
        - Observed Demand (Skill Frequency in target role): 60%
        - Course-to-Candidate Seniority Match: 40%
        """
        # 1. Demand component (60% weight)
        # Standardize frequency: if it's high, it contributes heavily to confidence.
        demand_score = float(skill_frequency_in_role) * 100.0
        demand_score = min(100.0, max(0.0, demand_score))

        # 2. Suitability / Seniority alignment component (40% weight)
        # Check if the course difficulty aligns with candidate experience
        suitability_score = 80.0  # default baseline
        
        if course_difficulty and candidate_seniority:
            diff_lower = course_difficulty.lower().strip()
            cand_lower = candidate_seniority.lower().strip()

            if "senior" in cand_lower:
                if "advanced" in diff_lower or "expert" in diff_lower:
                    suitability_score = 100.0
                elif "intermediate" in diff_lower:
                    suitability_score = 80.0
                else:
                    suitability_score = 50.0  # beginner course is low suitability for a senior
            elif "mid" in cand_lower or "associate" in cand_lower:
                if "intermediate" in diff_lower:
                    suitability_score = 100.0
                elif "advanced" in diff_lower or "beginner" in diff_lower:
                    suitability_score = 80.0
            else:  # junior/entry-level
                if "beginner" in diff_lower or "introduction" in diff_lower:
                    suitability_score = 100.0
                elif "intermediate" in diff_lower:
                    suitability_score = 70.0
                else:
                    suitability_score = 40.0  # advanced course is too hard/unsuitable for beginner

        # Compute weighted confidence
        confidence = 0.60 * demand_score + 0.40 * suitability_score
        return round(min(100.0, max(0.0, confidence)), 2)
