class RequirementService:

    def analyze(self, requirement: str):
        requirement = requirement.strip()

        if not requirement:
            raise ValueError("Requirement cannot be empty.")

        return {
            "requirement": requirement,
            "status": "understood",
            "type": "software_requirement",
            "next_stage": "architecture_planning"
        }