class ArchitectureService:

    def create_plan(self, requirement: str):

        requirement = requirement.strip()

        if not requirement:
            raise ValueError("Requirement cannot be empty.")

        return {
            "requirement": requirement,
            "architecture": {
                "backend": "FastAPI",
                "api": "REST API",
                "database": "PostgreSQL",
                "services": [
                    "Requirement Analysis",
                    "Architecture Planning",
                    "Code Generation",
                    "Testing"
                ]
            },
            "implementation_plan": [
                "Analyze the existing repository",
                "Design the required API endpoints",
                "Design the database changes",
                "Implement the required functionality",
                "Generate tests",
                "Run tests and verify results"
            ],
            "status": "architecture_planned",
            "next_stage": "implementation"
        }