from pathlib import Path

from app.services.requirement_service import RequirementService
from app.services.architecture_service import ArchitectureService
from app.services.code_generation_service import CodeGenerationService
from app.services.test_generation_service import TestGenerationService
from app.services.test_execution_service import TestExecutionService
from app.services.code_review_service import CodeReviewService
from app.services.security_service import SecurityService
from app.services.performance_service import PerformanceService
from app.services.deployment_service import DeploymentService
from app.services.monitoring_service import MonitoringService
from app.services.regression_service import RegressionService


class AutonomousWorkflowService:

    def __init__(self):

        self.requirement_service = RequirementService()

        self.architecture_service = ArchitectureService()

        self.code_generation_service = (
            CodeGenerationService()
        )

        self.test_generation_service = (
            TestGenerationService()
        )

        self.test_execution_service = (
            TestExecutionService()
        )

        self.code_review_service = (
            CodeReviewService()
        )

        self.security_service = (
            SecurityService()
        )

        self.performance_service = (
            PerformanceService()
        )

        self.deployment_service = (
            DeploymentService()
        )

        self.monitoring_service = (
            MonitoringService()
        )

        self.regression_service = (
            RegressionService()
        )

    def _get_application_path(
        self,
        repository_path: str
    ):

        repository = Path(
            repository_path
        ).resolve()

        backend_path = repository / "backend"

        if (
            backend_path.is_dir()
            and (backend_path / "main.py").exists()
        ):
            return str(backend_path)

        return str(repository)

    def execute(
        self,
        requirement: str,
        code: str,
        repository_path: str
    ):

        application_path = self._get_application_path(
            repository_path
        )

        requirement_result = (
            self.requirement_service.analyze(
                requirement
            )
        )

        architecture_result = (
            self.architecture_service.create_plan(
                requirement
            )
        )

        code_generation_result = (
            self.code_generation_service.generate_task(
                requirement,
                architecture_result[
                    "implementation_plan"
                ]
            )
        )

        test_generation_result = (
            self.test_generation_service.generate_tests(
                requirement
            )
        )

        test_execution_result = (
            self.test_execution_service.execute_tests(
                application_path
            )
        )

        code_review_result = (
            self.code_review_service.review(
                code
            )
        )

        security_result = (
            self.security_service.analyze(
                code
            )
        )

        performance_result = (
            self.performance_service.analyze(
                code
            )
        )

        deployment_result = (
            self.deployment_service.check_readiness(
                application_path
            )
        )

        monitoring_result = (
            self.monitoring_service.get_health()
        )

        regression_result = (
            self.regression_service.analyze(
                repository_path,
                test_execution_result[
                    "return_code"
                ],
                test_execution_result[
                    "output"
                ]
            )
        )

        if test_execution_result["return_code"] != 0:

            next_stage = "failure_diagnosis"

        elif regression_result[
            "regression_detected"
        ]:

            next_stage = "automatic_rollback"

        elif deployment_result[
            "status"
        ] != "deployment_ready":

            next_stage = "deployment_configuration"

        else:

            next_stage = "monitoring"

        return {
            "status": "workflow_completed",

            "repository_path": str(
                Path(repository_path).resolve()
            ),

            "application_path": application_path,

            "requirement_analysis": (
                requirement_result
            ),

            "architecture": (
                architecture_result
            ),

            "code_generation": (
                code_generation_result
            ),

            "test_generation": (
                test_generation_result
            ),

            "test_execution": (
                test_execution_result
            ),

            "code_review": (
                code_review_result
            ),

            "security_analysis": (
                security_result
            ),

            "performance_analysis": (
                performance_result
            ),

            "deployment": (
                deployment_result
            ),

            "monitoring": (
                monitoring_result
            ),

            "regression_detection": (
                regression_result
            ),

            "workflow": [
                "requirement_analysis",
                "architecture_planning",
                "code_generation",
                "test_generation",
                "test_execution",
                "code_review",
                "security_analysis",
                "performance_analysis",
                "deployment",
                "monitoring",
                "regression_detection"
            ],

            "next_stage": next_stage
        }