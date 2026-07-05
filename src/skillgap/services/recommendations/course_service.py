import json
from pathlib import Path


class CourseService:

    def __init__(self, courses_file: str | Path = None):
        if courses_file is None:
            # Resolve relative to package directory
            courses_file = Path(__file__).parents[2] / "knowledge" / "courses.json"
        
        self.courses_file = Path(courses_file)
        self.courses = self._load_courses()

    def _load_courses(self) -> list[dict]:
        try:
            with open(self.courses_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def get_recommendations_for_skill(self, skill_name: str) -> list[dict]:
        """
        Returns all courses that cover a given skill.
        Matches by comparing the skill name (case-insensitive).
        """
        normalized = skill_name.strip().lower()
        
        matches = []
        for course in self.courses:
            if course.get("skill", "").lower() == normalized:
                matches.append(course)

        # Fallback to substring matching if no exact matches
        if not matches:
            for course in self.courses:
                if normalized in course.get("skill", "").lower():
                    matches.append(course)

        # Fallback to AI generation if still no matches
        if not matches:
            try:
                from skillgap.services.ai_service import AIService
                ai = AIService()
                prompt = (
                    "You are a technical career advisor. A developer is missing the skill: '{skill}'. "
                    "Recommend exactly one premium, high-quality, reputable certification course or learning path "
                    "specifically for this skill from platforms like Coursera, edX, or official documentation. "
                    "Provide a real, correct URL if possible (e.g. on Coursera, edX, or official documentation), "
                    "not a placeholder.\n\n"
                    "Return ONLY valid JSON matching this schema:\n"
                    "{{\n"
                    "  \"title\": \"Course Title\",\n"
                    "  \"provider\": \"Coursera (Google)\" or similar,\n"
                    "  \"duration\": \"Duration (e.g., 20 hours, 4 weeks)\",\n"
                    "  \"difficulty\": \"Beginner/Intermediate/Advanced\",\n"
                    "  \"link\": \"URL link to the course page\",\n"
                    "  \"free\": false,\n"
                    "  \"type\": \"Professional Certificate\" or \"Certificate Course\"\n"
                    "}}\n"
                ).format(skill=skill_name)
                generated = ai.generate_json(prompt)
                if generated and isinstance(generated, dict):
                    generated["id"] = f"ai_gen_{skill_name.lower().replace(' ', '_')}"
                    generated["skill"] = skill_name
                    matches.append(generated)
            except Exception:
                # Fallback to a basic static documentation recommendation if LLM fails (e.g., rate limit)
                matches.append({
                    "id": f"fallback_{skill_name.lower().replace(' ', '_')}",
                    "skill": skill_name,
                    "title": f"Official {skill_name} Learning Guide & Documentation",
                    "provider": f"Official {skill_name} Project",
                    "duration": "Self-paced",
                    "difficulty": "All Levels",
                    "link": f"https://www.google.com/search?q={skill_name}+official+documentation+course",
                    "free": True,
                    "type": "Official Tutorial"
                })

        return matches
