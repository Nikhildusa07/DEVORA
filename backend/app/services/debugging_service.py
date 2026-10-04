class DebuggingService:

    def diagnose(self, test_output: str, test_error: str = ""):

        output = test_output.strip()
        error = test_error.strip()

        if not output and not error:
            raise ValueError(
                "Test output or error is required."
            )

        combined_result = f"{output}\n{error}".lower()

        if "modulenotfounderror" in combined_result:
            diagnosis = "A required Python module is missing."
            recommendation = "Install the missing dependency in the active environment."

        elif "assertionerror" in combined_result:
            diagnosis = "A test assertion failed."
            recommendation = "Review the failing assertion and the related implementation."

        elif "syntaxerror" in combined_result:
            diagnosis = "A Python syntax error was detected."
            recommendation = "Review the reported file and line number for invalid syntax."

        elif "typeerror" in combined_result:
            diagnosis = "A type-related error was detected."
            recommendation = "Check the data types and function arguments involved."

        elif "nameerror" in combined_result:
            diagnosis = "An undefined variable or name was detected."
            recommendation = "Check the variable or function name and its scope."

        elif "filenotfounderror" in combined_result:
            diagnosis = "A required file or path was not found."
            recommendation = "Verify the file path and ensure the required file exists."

        else:
            diagnosis = "The test execution failed for an unidentified reason."
            recommendation = "Review the complete test output and traceback."

        return {
            "status": "failure_diagnosed",
            "diagnosis": diagnosis,
            "recommendation": recommendation,
            "test_output": output,
            "test_error": error,
            "next_stage": "debugging"
        }