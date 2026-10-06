import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()


class AIReasoningService:

    MODELS = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]

    MAX_RETRIES_PER_MODEL = 2
    RETRY_DELAY_SECONDS = 2

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

    def _is_temporary_error(
        self,
        error
    ):

        error_text = str(error).lower()

        temporary_errors = [
            "503",
            "unavailable",
            "high demand",
            "429",
            "resource exhausted",
            "rate limit",
            "too many requests",
            "temporarily unavailable",
            "internal server error",
            "500",
            "502",
            "504",
        ]

        return any(
            message in error_text
            for message in temporary_errors
        )

    def _generate_with_fallback(
        self,
        prompt: str
    ):

        errors = []

        for model in self.MODELS:

            for attempt in range(
                1,
                self.MAX_RETRIES_PER_MODEL + 1
            ):

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
                        "model": model,
                        "result": result
                    }

                except Exception as error:

                    error_details = {
                        "model": model,
                        "attempt": attempt,
                        "error": str(error)
                    }

                    errors.append(
                        error_details
                    )

                    if (
                        self._is_temporary_error(
                            error
                        )
                        and attempt
                        < self.MAX_RETRIES_PER_MODEL
                    ):

                        time.sleep(
                            self.RETRY_DELAY_SECONDS
                        )

                        continue

                    break

        raise RuntimeError(
            "All configured Gemini models are "
            "currently unavailable.\n"
            f"Attempts: {errors}"
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

        result = self._generate_with_fallback(
            prompt
        )

        return {
            "status": "ai_reasoning_completed",
            "model": result["model"],
            "requirement": requirement,
            "reasoning": result["result"],
            "next_stage": "implementation"
        }