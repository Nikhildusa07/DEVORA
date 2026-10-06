from datetime import datetime
from pathlib import Path

from app.services.ai_reasoning_service import AIReasoningService
from app.services.ai_implementation_service import (
    AIImplementationService
)
from app.services.requirement_service import RequirementService
from app.services.repository_analyzer import RepositoryAnalyzer
from app.services.architecture_discovery_service import (
    ArchitectureDiscoveryService
)
from app.services.architecture_service import ArchitectureService
from app.services.dependency_service import DependencyService
from app.services.code_generation_service import CodeGenerationService
from app.services.test_generation_service import TestGenerationService
from app.services.test_execution_service import TestExecutionService
from app.services.debugging_service import DebuggingService
from app.services.auto_fix_service import AutoFixService
from app.services.refactoring_service import RefactoringService
from app.services.code_review_service import CodeReviewService
from app.services.security_service import SecurityService
from app.services.performance_service import PerformanceService
from app.services.deployment_service import DeploymentService
from app.services.monitoring_service import MonitoringService
from app.services.regression_service import RegressionService
from app.services.cicd_service import CICDService
from app.services.git_service import GitService
from app.services.git_branch_service import GitBranchService
from app.services.git_commit_service import GitCommitService
from app.services.pull_request_service import PullRequestService
from app.services.repository_memory_service import (
    RepositoryMemoryService
)


class AutonomousWorkflowService:

    def __init__(self):

        self.ai_reasoning_service = AIReasoningService()

        self.ai_implementation_service = (
            AIImplementationService()
        )

        self.requirement_service = RequirementService()

        self.repository_analyzer = RepositoryAnalyzer()

        self.architecture_discovery_service = (
            ArchitectureDiscoveryService()
        )

        self.architecture_service = ArchitectureService()

        self.dependency_service = DependencyService()

        self.code_generation_service = (
            CodeGenerationService()
        )

        self.test_generation_service = (
            TestGenerationService()
        )

        self.test_execution_service = (
            TestExecutionService()
        )

        self.debugging_service = DebuggingService()

        self.auto_fix_service = AutoFixService()

        self.refactoring_service = RefactoringService()

        self.code_review_service = CodeReviewService()

        self.security_service = SecurityService()

        self.performance_service = PerformanceService()

        self.deployment_service = DeploymentService()

        self.monitoring_service = MonitoringService()

        self.regression_service = RegressionService()

        self.cicd_service = CICDService()

        self.git_service = GitService()

        self.git_branch_service = GitBranchService()

        self.git_commit_service = GitCommitService()

        self.pull_request_service = PullRequestService()

        self.repository_memory_service = (
            RepositoryMemoryService()
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

    def _safe_refactoring_file(
        self,
        repository_path: str
    ):

        repository = Path(
            repository_path
        ).resolve()

        candidates = [
            repository / "backend" / "main.py",
            repository / "main.py"
        ]

        for candidate in candidates:

            if (
                candidate.exists()
                and candidate.is_file()
            ):
                return str(
                    candidate.relative_to(
                        repository
                    )
                )

        return None

    def _create_git_branch_name(self):

        timestamp = datetime.now().strftime(
            "%Y%m%d-%H%M%S"
        )

        return f"devora-auto-{timestamp}"

    def execute(
        self,
        requirement: str,
        code: str,
        repository_path: str
    ):

        repository = Path(
            repository_path
        ).resolve()

        application_path = (
            self._get_application_path(
                repository_path
            )
        )

        ai_reasoning_result = (
            self.ai_reasoning_service.reason(
                requirement
            )
        )

        reasoning_text = (
            ai_reasoning_result.get(
                "reasoning",
                ""
            )
        )

        requirement_result = (
            self.requirement_service.analyze(
                requirement
            )
        )

        repository_result = (
            self.repository_analyzer.analyze(
                repository_path
            )
        )

        architecture_discovery_result = (
            self.architecture_discovery_service.discover(
                repository_path
            )
        )

        architecture_result = (
            self.architecture_service.create_plan(
                requirement
            )
        )

        dependency_result = (
            self.dependency_service.analyze(
                repository_path
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

        ai_implementation_result = (
            self.ai_implementation_service
            .generate_implementation(
                requirement,
                reasoning_text,
                repository_path
            )
        )

        implementation_result = (
            self.ai_implementation_service
            .apply_changes(
                repository_path,
                ai_implementation_result
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

        debugging_result = None
        auto_fix_result = None

        if (
            test_execution_result[
                "return_code"
            ] != 0
        ):

            debugging_result = (
                self.debugging_service.diagnose(
                    test_execution_result[
                        "output"
                    ],
                    test_execution_result.get(
                        "error",
                        ""
                    )
                )
            )

            auto_fix_result = (
                self.auto_fix_service.generate_fix(
                    test_execution_result[
                        "output"
                    ],
                    test_execution_result.get(
                        "error",
                        ""
                    )
                )
            )

        refactoring_result = None

        refactoring_file = (
            self._safe_refactoring_file(
                repository_path
            )
        )

        if refactoring_file:

            refactoring_result = (
                self.refactoring_service.analyze(
                    repository_path,
                    refactoring_file
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

        cicd_result = (
            self.cicd_service.analyze(
                repository_path
            )
        )

        git_result = (
            self.git_service.get_status(
                repository_path
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

        git_automation_result = None

        if (
            test_execution_result[
                "return_code"
            ] == 0
            and not regression_result[
                "regression_detected"
            ]
        ):

            try:

                branch_name = (
                    self._create_git_branch_name()
                )

                branch_result = (
                    self.git_branch_service.create_branch(
                        repository_path,
                        branch_name
                    )
                )

                commit_result = (
                    self.git_commit_service.commit_changes(
                        repository_path,
                        "DEVORA: autonomous implementation"
                    )
                )

                pull_request_result = (
                    self.pull_request_service
                    .generate_pull_request(
                        repository_path,
                        f"DEVORA: {requirement}",
                        (
                            "Autonomous implementation "
                            "generated by DEVORA.\n\n"
                            f"Requirement: {requirement}"
                        ),
                        branch_name,
                        "main"
                    )
                )

                git_automation_result = {
                    "status": "git_automation_completed",
                    "branch": branch_result,
                    "commit": commit_result,
                    "pull_request": pull_request_result
                }

            except Exception as error:

                git_automation_result = {
                    "status": "git_automation_failed",
                    "message": str(error)
                }

        else:

            git_automation_result = {
                "status": "git_automation_skipped",
                "reason": (
                    "Git automation requires "
                    "passing tests and no regression."
                )
            }

        memory_result = None

        try:

            memory_content = {
                "requirement": requirement,
                "workflow_status": "completed",
                "implementation_status": (
                    implementation_result[
                        "status"
                    ]
                ),
                "changed_files": (
                    implementation_result[
                        "changed_files"
                    ]
                ),
                "test_return_code": (
                    test_execution_result[
                        "return_code"
                    ]
                ),
                "regression_detected": (
                    regression_result[
                        "regression_detected"
                    ]
                ),
                "git_automation_status": (
                    git_automation_result[
                        "status"
                    ]
                )
            }

            memory_result = (
                self.repository_memory_service.save_memory(
                    repository_path,
                    "autonomous_workflow",
                    memory_content
                )
            )

        except Exception as error:

            memory_result = {
                "status": "memory_save_skipped",
                "message": str(error)
            }

        if (
            test_execution_result[
                "return_code"
            ] != 0
        ):

            next_stage = "failure_diagnosis"

        elif (
            regression_result[
                "regression_detected"
            ]
        ):

            next_stage = "automatic_rollback"

        elif (
            deployment_result[
                "status"
            ] != "deployment_ready"
        ):

            next_stage = "deployment_configuration"

        elif (
            git_automation_result[
                "status"
            ] == "git_automation_failed"
        ):

            next_stage = "git_recovery"

        else:

            next_stage = "monitoring"

        return {

            "status": "workflow_completed",

            "repository_path": str(
                repository
            ),

            "application_path": (
                application_path
            ),

            "ai_reasoning": (
                ai_reasoning_result
            ),

            "requirement_analysis": (
                requirement_result
            ),

            "repository_analysis": (
                repository_result
            ),

            "architecture_discovery": (
                architecture_discovery_result
            ),

            "architecture": (
                architecture_result
            ),

            "dependency_analysis": (
                dependency_result
            ),

            "code_generation": (
                code_generation_result
            ),

            "ai_implementation": (
                ai_implementation_result
            ),

            "implementation": (
                implementation_result
            ),

            "test_generation": (
                test_generation_result
            ),

            "test_execution": (
                test_execution_result
            ),

            "debugging": (
                debugging_result
            ),

            "auto_fix": (
                auto_fix_result
            ),

            "refactoring": (
                refactoring_result
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

            "cicd": (
                cicd_result
            ),

            "git": (
                git_result
            ),

            "git_automation": (
                git_automation_result
            ),

            "monitoring": (
                monitoring_result
            ),

            "regression_detection": (
                regression_result
            ),

            "repository_memory": (
                memory_result
            ),

            "workflow": [

                "ai_reasoning",
                "requirement_analysis",
                "repository_analysis",
                "architecture_discovery",
                "architecture_planning",
                "dependency_analysis",
                "code_generation",
                "ai_implementation",
                "code_modification",
                "test_generation",
                "test_execution",
                "failure_diagnosis",
                "auto_fix_analysis",
                "refactoring",
                "code_review",
                "security_analysis",
                "performance_analysis",
                "deployment_readiness",
                "cicd_analysis",
                "git_status",
                "git_branch",
                "git_commit",
                "pull_request_generation",
                "monitoring",
                "regression_detection",
                "repository_memory"

            ],

            "next_stage": next_stage
        }