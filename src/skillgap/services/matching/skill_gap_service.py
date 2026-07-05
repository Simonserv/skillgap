from skillgap.models.resume import ResumeProfile
from skillgap.models.job import JobPosting
from skillgap.analytics.readiness import ReadinessScorer
from skillgap.analytics.skill_frequency import SkillFrequencyAnalyzer
from skillgap.analytics.recommendation_confidence import RecommendationConfidenceCalculator
from skillgap.services.recommendations.course_service import CourseService


class SkillGapService:

    def __init__(self, courses_file: str = None):
        self.course_service = CourseService(courses_file)

    def analyze_gap(
        self,
        profile: ResumeProfile,
        job: JobPosting,
        market_dataset_path: str = None
    ) -> dict:
        """
        Runs the complete SkillGap analysis:
        - Current readiness score & breakdown
        - Identifies missing skills
        - Resolves course recommendations with confidence scores
        - Projects the impact of learning each missing skill
        """
        # 1. Compute current readiness
        readiness_data = ReadinessScorer.calculate_readiness(profile, job)
        current_score = readiness_data["readiness_score"]
        missing_skills = readiness_data["breakdown"]["skill_matching"]["missing"]

        # Load market dataset frequencies if available
        frequencies = {}
        if market_dataset_path:
            # We filter by job's role category if possible
            frequencies = SkillFrequencyAnalyzer.analyze_from_file(
                market_dataset_path,
                role_category=job.role_category or None
            )

        # 2. Get recommendations & confidence scores
        recommendations = []
        for skill in missing_skills:
            freq = frequencies.get(skill, frequencies.get(skill.lower(), 0.30))  # default 30% if not found
            courses = self.course_service.get_recommendations_for_skill(skill)
            
            course_recommendations = []
            for course in courses:
                conf = RecommendationConfidenceCalculator.calculate_confidence(
                    skill_name=skill,
                    skill_frequency_in_role=freq,
                    course_difficulty=course.get("difficulty"),
                    candidate_seniority=job.seniority
                )
                course_recommendations.append({
                    "course": course,
                    "confidence": conf
                })

            # Calculate individual skill acquisition projected readiness
            projected = ReadinessScorer.calculate_readiness(profile, job, additional_skills={skill})
            projected_score = projected["readiness_score"]
            improvement = round(projected_score - current_score, 2)

            recommendations.append({
                "skill": skill,
                "market_demand_frequency": round(freq * 100, 2),
                "projected_readiness": projected_score,
                "projected_improvement": improvement,
                "courses": course_recommendations
            })

        # Sort recommendations by market demand frequency descending
        recommendations.sort(key=lambda x: x["market_demand_frequency"], reverse=True)

        # 3. Calculate full acquisition projection (if all missing skills are learned)
        all_learned_projected = ReadinessScorer.calculate_readiness(
            profile,
            job,
            additional_skills=set(missing_skills)
        )
        full_projected_score = all_learned_projected["readiness_score"]

        return {
            "job_title": job.title,
            "company": job.company,
            "current_readiness": current_score,
            "readiness_breakdown": readiness_data["breakdown"],
            "missing_skills_count": len(missing_skills),
            "recommendations": recommendations,
            "full_projected_readiness": full_projected_score,
            "potential_improvement": round(full_projected_score - current_score, 2)
        }
