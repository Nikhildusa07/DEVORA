import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class AIReasoningService:

    MODELS = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
    ]

    def __init__(self):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    def reason(
        self,
        requirement: str,
        repository_context: str = ""
    ):

        requirement = requirement.strip()

        repository_context = (
            repository_context.strip()
        )

        if not requirement:
            raise ValueError(
                "Requirement cannot be empty."
            )

        prompt = f"""
You are DEVORA, an autonomous AI
software engineering system.

Your responsibility is to reason about
software requirements and determine a
safe implementation strategy.

Requirement:
{requirement}

Repository Context:
{repository_context}

Analyze the requirement and provide:

1. Requirement understanding
2. Functional requirements
3. Technical requirements
4. Architecture changes
5. Files that may need to be created
6. Files that may need to be modified
7. API changes
8. Database changes
9. Testing strategy
10. Security considerations
11. Performance considerations
12. Implementation steps
13. Potential risks

Do not claim that code has been changed.
Only provide a reasoning and implementation plan.

Return the result in clear structured text.
"""

        errors = []

        for model in self.MODELS:

            try:

                response = (
                    self.client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                )

                result = response.text

                if not result:
                    raise RuntimeError(
                        "AI model returned an empty response."
                    )

                return {
                    "status": "ai_reasoning_completed",
                    "model": model,
                    "requirement": requirement,
                    "reasoning": result,
                    "next_stage": "implementation"
                }

            except Exception as error:

                errors.append({
                    "model": model,
                    "error": str(error)
                })

        raise RuntimeError(
            "All configured Gemini models are currently "
            "unavailable.\n"
            f"Attempts: {errors}"
        )   