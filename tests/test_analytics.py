import unittest
from datetime import date

from skillgap.models.resume import ResumeProfile
from skillgap.models.job import JobPosting
from skillgap.analytics.readiness import ReadinessScorer
from skillgap.analytics.skill_frequency import SkillFrequencyAnalyzer
from skillgap.analytics.skill_correlation import SkillCorrelationAnalyzer
from skillgap.analytics.recommendation_confidence import RecommendationConfidenceCalculator
from skillgap.services.matching.skill_gap_service import SkillGapService


class TestAnalytics(unittest.TestCase):

    def test_parse_date(self):
        # Specific dates
        d1 = ReadinessScorer.parse_date("Jan 2021")
        self.assertEqual(d1.year, 2021)
        self.assertEqual(d1.month, 1)

        d2 = ReadinessScorer.parse_date("2020-05-12")
        self.assertEqual(d2.year, 2020)
        self.assertEqual(d2.month, 5)

        # Present/current fallback
        d3 = ReadinessScorer.parse_date("Present", default_to_now=True)
        self.assertEqual(d3.year, 2026)
        self.assertEqual(d3.month, 7)

    def test_calculate_experience(self):
        experience = [
            {"start_date": "Jan 2020", "end_date": "Jan 2022"},  # 2 years
            {"start_date": "Jun 2023", "end_date": "Dec 2023"}   # 6 months (0.5 years)
        ]
        years = ReadinessScorer.calculate_total_experience_years(experience)
        self.assertEqual(years, 2.5)

    def test_flatten_skills(self):
        nested = {
            "languages": ["Python", "SQL"],
            "tools": {
                "devops": ["Docker", "Kubernetes"],
                "editor": "VS Code"
            }
        }
        flat = ReadinessScorer.flatten_resume_skills(nested)
        self.assertIn("python", flat)
        self.assertIn("sql", flat)
        self.assertIn("docker", flat)
        self.assertIn("kubernetes", flat)
        self.assertIn("vs code", flat)

    def test_readiness_scoring(self):
        profile = ResumeProfile(
            summary="Python developer with experience building web apps.",
            skills={"languages": ["Python", "SQL"]},
            experience=[
                {"position": "Developer", "company": "A", "start_date": "2020", "end_date": "2023"} # 3 years
            ]
        )

        job = JobPosting(
            title="Python Developer",
            company="B",
            location="Remote",
            source="Test",
            url="http://test.com",
            description="Looking for a Python Developer experienced in Python, SQL, and Docker.",
            skills=["Python", "SQL", "Docker"],
            seniority="Mid"
        )

        readiness = ReadinessScorer.calculate_readiness(profile, job)
        score = readiness["readiness_score"]
        
        # Skill match should be 2 out of 3 = 66.67%
        self.assertAlmostEqual(readiness["breakdown"]["skill_matching"]["score"], 66.67, places=2)
        # Experience match should be 3 years / 3 years = 100%
        self.assertEqual(readiness["breakdown"]["experience_matching"]["score"], 100.0)
        # Composite score should be calculated
        self.assertTrue(0 <= score <= 100)

    def test_skill_frequency(self):
        jobs = [
            {"skills": ["Python", "SQL"], "role_category": "Backend"},
            {"skills": ["Python", "Docker"], "role_category": "Backend"},
            {"skills": ["React"], "role_category": "Frontend"}
        ]
        freq = SkillFrequencyAnalyzer.analyze_frequencies(jobs, role_category="Backend")
        self.assertAlmostEqual(freq["Python"], 1.0)
        self.assertAlmostEqual(freq["SQL"], 0.5)

    def test_skill_correlation(self):
        jobs = [
            {"skills": ["Python", "SQL"]},
            {"skills": ["Python", "Docker"]},
            {"skills": ["Python", "SQL"]},
            {"skills": ["React"]}
        ]
        corr = SkillCorrelationAnalyzer.get_correlations(jobs, target_skill="Python")
        # Python co-occurs with SQL 2 times out of 3 Python jobs -> 2/3 = 66.67%
        sql_rule = next(c for c in corr if c["skill"] == "SQL")
        self.assertAlmostEqual(sql_rule["probability"], 0.6667, places=4)

    def test_confidence_calculator(self):
        conf = RecommendationConfidenceCalculator.calculate_confidence(
            skill_name="Docker",
            skill_frequency_in_role=0.8,
            course_difficulty="Intermediate",
            candidate_seniority="Mid"
        )
        # Docker is in high demand (80%) and the course difficulty (Intermediate)
        # matches the candidate's seniority (Mid) which is high suitability (100%).
        # Weighted score: 0.60 * 80 + 0.40 * 100 = 88.0
        self.assertEqual(conf, 88.0)

    def test_skill_gap_service(self):
        profile = ResumeProfile(
            summary="Python coder",
            skills=["Python"],
            experience=[
                {"position": "Dev", "start_date": "2020", "end_date": "2025"}
            ]
        )
        job = JobPosting(
            title="Senior Dev",
            company="Google",
            location="Remote",
            source="Test",
            url="http://google.com",
            description="Need Python and Docker",
            skills=["Python", "Docker"],
            seniority="Senior"
        )

        service = SkillGapService()
        result = service.analyze_gap(profile, job)
        self.assertEqual(result["job_title"], "Senior Dev")
        self.assertEqual(len(result["recommendations"]), 1)
        self.assertEqual(result["recommendations"][0]["skill"], "docker")
        self.assertTrue(result["potential_improvement"] > 0)


if __name__ == "__main__":
    unittest.main()
