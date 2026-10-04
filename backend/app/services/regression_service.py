import json
from pathlib import Path


class RegressionService:

    BASELINE_FILE = ".devora_regression_baseline.json"

    def analyze(
        self,
        repository_path: str,
        current_return_code: int,
        current_output: str = ""
    ):

        repository = Path(repository_path).resolve()

        if not repository.exists():
            raise FileNotFoundError(
                "Repository path does not exist."
            )

        if not repository.is_dir():
            raise NotADirectoryError(
                "Repository path is not a directory."
            )

        baseline_path = (
            repository / self.BASELINE_FILE
        )

        current_status = (
            "passed"
            if current_return_code == 0
            else "failed"
        )

        current_result = {
            "return_code": current_return_code,
            "status": current_status,
            "output": current_output
        }

        if not baseline_path.exists():

            baseline_path.write_text(
                json.dumps(
                    current_result,
                    indent=4
                ),
                encoding="utf-8"
            )

            return {
                "repository": str(repository),
                "status": "baseline_created",
                "baseline": current_result,
                "regression_detected": False,
                "message": "Regression baseline created successfully.",
                "next_stage": "monitoring"
            }

        try:
            baseline = json.loads(
                baseline_path.read_text(
                    encoding="utf-8"
                )
            )

        except json.JSONDecodeError:
            baseline = {
                "return_code": 0,
                "status": "passed",
                "output": ""
            }

        regression_detected = (
            baseline.get("status") == "passed"
            and current_status == "failed"
        )

        if regression_detected:

            status = "regression_detected"
            message = (
                "A previously passing test state "
                "has failed."
            )
            next_stage = "automatic_rollback"

        else:

            status = "no_regression"
            message = (
                "No regression detected."
            )
            next_stage = "monitoring"

        return {
            "repository": str(repository),
            "status": status,
            "baseline": baseline,
            "current": current_result,
            "regression_detected": regression_detected,
            "message": message,
            "next_stage": next_stage
        }