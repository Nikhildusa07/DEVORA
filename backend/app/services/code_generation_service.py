class CodeGenerationService:

    def generate_task(self, requirement: str, implementation_plan: list):

        requirement = requirement.strip()

        if not requirement:
            raise ValueError("Requirement cannot be empty.")

        if not implementation_plan:
            raise ValueError("Implementation plan cannot be empty.")

        return {
            "requirement": requirement,
            "generation_target": "backend",
            "language": "Python",
            "framework": "FastAPI",
            "tasks": [
                {
                    "task": "Create required data model",
                    "status": "pending"
                },
                {
                    "task": "Create required API endpoints",
                    "status": "pending"
                },
                {
                    "task": "Implement business logic",
                    "status": "pending"
                },
                {
                    "task": "Create tests",
                    "status": "pending"
                }
            ],
            "implementation_plan": implementation_plan,
            "status": "code_generation_ready",
            "next_stage": "code_implementation"
        }