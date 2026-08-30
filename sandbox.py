import os
import shutil
import subprocess
import tempfile
from typing import Dict, Any, List, Optional


class SandboxExecutor:

    def __init__(self, timeout_seconds: int = 60):
        self.timeout = timeout_seconds

    def _copy_to_sandbox(self, original_repo_path: str) -> str:
        """Creates an isolated temporary copy of the repository."""
        sandbox_dir = tempfile.mkdtemp(prefix="sandbox_run_")
        shutil.copytree(original_repo_path, sandbox_dir, dirs_exist_ok=True)
        return sandbox_dir

    def _apply_patches(self, sandbox_path: str, patches: List[Dict[str, str]]) -> None:
        for patch in patches:
            rel_path = patch.get("file_path")
            new_code = patch.get("patched_code")

            if not rel_path or new_code is None:
                continue

            target_file = os.path.join(sandbox_path, rel_path)
            os.makedirs(os.path.dirname(target_file), exist_ok=True)

            with open(target_file, "w", encoding="utf-8") as f:
                f.write(new_code)

    def _detect_test_command(self, sandbox_path: str) -> List[str]:
        """Detects available test suites or falls back to Python AST syntax compilation."""
        if os.path.exists(os.path.join(sandbox_path, "pytest.ini")) or os.path.exists(os.path.join(sandbox_path, "tests")):
            return ["pytest", "-v"]
        elif os.path.exists(os.path.join(sandbox_path, "package.json")):
            return ["npm", "test"]
        else:
            # Fallback syntax compilation check on all python files
            return ["python", "-m", "compileall", "."]

    def run_tests(
        self,
        original_repo_path: str,
        patches: List[Dict[str, str]],
        custom_test_cmd: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        if not os.path.exists(original_repo_path):
            raise ValueError(f"Original repo path does not exist: {original_repo_path}")

        sandbox_dir = self._copy_to_sandbox(original_repo_path)
        test_cmd = custom_test_cmd or self._detect_test_command(sandbox_dir)

        try:
            #  Apply proposed patches
            self._apply_patches(sandbox_dir, patches)

            #  Execute test command in the isolated workspace
            process = subprocess.run(
                test_cmd,
                cwd=sandbox_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            passed = (process.returncode == 0)
            return {
                "status": "success" if passed else "failed",
                "passed": passed,
                "exit_code": process.returncode,
                "command_executed": " ".join(test_cmd),
                "stdout": process.stdout.strip(),
                "stderr": process.stderr.strip(),
                "error_message": None if passed else "Tests failed or syntax broke under proposed patch."
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "passed": False,
                "exit_code": -1,
                "command_executed": " ".join(test_cmd),
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout} seconds.",
                "error_message": "Test execution exceeded timeout limit."
            }
        except Exception as e:
            return {
                "status": "error",
                "passed": False,
                "exit_code": -1,
                "command_executed": " ".join(test_cmd),
                "stdout": "",
                "stderr": str(e),
                "error_message": f"Sandbox execution failure: {str(e)}"
            }
        finally:
            shutil.rmtree(sandbox_dir, ignore_errors=True)


# LangGraph / Workflow Node Function
def sandbox_testing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node entrypoint for Step 4.
    Consumes proposed patches from state and returns sandbox test outputs.
    """
    local_path = state.get("local_path")
    proposed_patches = state.get("proposed_patches", [])

    executor = SandboxExecutor(timeout_seconds=60)
    test_result = executor.run_tests(
        original_repo_path=local_path,
        patches=proposed_patches
    )

    return {
        **state,
        "sandbox_test_result": test_result
    }


# Direct Test
if __name__ == "__main__":
    # Create a dummy test repo
    test_dir = tempfile.mkdtemp(prefix="mock_sandbox_test_")
    sample_file = os.path.join(test_dir, "math_utils.py")
    with open(sample_file, "w") as f:
        f.write("def multiply(a, b):\n    return a * b\n")

    # Mock a patch
    patches = [{
        "file_path": "math_utils.py",
        "patched_code": "def multiply(a, b):\n    # Optimized\n    return int(a) * int(b)\n"
    }]

    # Run sandbox test
    runner = SandboxExecutor()
    result = runner.run_tests(test_dir, patches)
    print("Execution Result:", result)

    # Cleanup
    shutil.rmtree(test_dir, ignore_errors=True)