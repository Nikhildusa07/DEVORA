class TestGenerationService:

    def generate_tests(self, requirement: str):

        requirement = requirement.strip()

        if not requirement:
            raise ValueError("Requirement cannot be empty.")

        return {
            "requirement": requirement,
            "test_framework": "pytest",
            "tests": [
                {
                    "name": "test_requirement_is_valid",
                    "description": "Verify that the requirement is provided.",
                    "status": "generated"
                },
                {
                    "name": "test_api_endpoint",
                    "description": "Verify that the required API endpoint works.",
                    "status": "generated"
                },
                {
                    "name": "test_invalid_input",
                    "description": "Verify that invalid input is handled correctly.",
                    "status": "generated"
                }
            ],
            "total_tests": 3,
            "status": "tests_generated",
            "next_stage": "test_execution"
        }