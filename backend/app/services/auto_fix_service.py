class AutoFixService:

    def generate_fix(
        self,
        test_output: str,
        test_error: str = ""
    ):

        output = test_output.strip()
        error = test_error.strip()

        if not output and not error:
            raise ValueError(
                "Test output or error is required."
            )

        combined_result = (
            f"{output}\n{error}"
        ).lower()

        fixes = []

        if "modulenotfounderror" in combined_result:
            fixes.append({
                "error": "ModuleNotFoundError",
                "action": "Install the missing Python dependency.",
                "auto_fix_available": True
            })

        elif "syntaxerror" in combined_result:
            fixes.append({
                "error": "SyntaxError",
                "action": "Review and correct the reported Python syntax.",
                "auto_fix_available": False
            })

        elif "nameerror" in combined_result:
            fixes.append({
                "error": "NameError",
                "action": "Check the undefined variable or function name.",
                "auto_fix_available": False
            })

        elif "typeerror" in combined_result:
            fixes.append({
                "error": "TypeError",
                "action": "Check the data types and function arguments.",
                "auto_fix_available": False
            })

        elif "assertionerror" in combined_result:
            fixes.append({
                "error": "AssertionError",
                "action": "Review the failing assertion and implementation.",
                "auto_fix_available": False
            })

        elif "filenotfounderror" in combined_result:
            fixes.append({
                "error": "FileNotFoundError",
                "action": "Verify the required file path exists.",
                "auto_fix_available": False
            })

        else:
            fixes.append({
                "error": "UnknownError",
                "action": "Manual debugging is required.",
                "auto_fix_available": False
            })

        auto_fix_available = any(
            fix["auto_fix_available"]
            for fix in fixes
        )

        return {
            "status": "auto_fix_analyzed",
            "auto_fix_available": auto_fix_available,
            "fixes": fixes,
            "total_fixes": len(fixes),
            "next_stage": (
                "apply_fix"
                if auto_fix_available
                else "manual_debugging"
            )
        }