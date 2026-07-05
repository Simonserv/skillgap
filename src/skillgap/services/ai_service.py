import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class AIService:

    MODEL = "llama-3.3-70b-versatile"

    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

    def generate_json(self, prompt: str) -> dict:
        """
        Sends a prompt to the LLM and returns parsed JSON.
        """

        response = self.client.chat.completions.create(
            model=self.MODEL,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown fences if present
        if content.startswith("```"):
            lines = content.splitlines()

            lines = lines[1:]

            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]

            content = "\n".join(lines)

        return json.loads(content)