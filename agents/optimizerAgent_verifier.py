from typing import Dict, Any, Literal


class Verifier:
    """
    Inspects sandbox test outputs and decides whether
    to loop back to the Optimizer Agent or proceed.
    """

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    def verify_optimizer_output(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates sandbox results specifically for proposed code optimizations.
        """
        sandbox_result = state.get("sandbox_test_result", {})
        tests_passed = sandbox_result.get("passed", False)
        retry_count = state.get("optimizer_retry_count", 0)

        #Case A: Tests Passed -> Move Forward
        if tests_passed:
            return {
                **state,
                "verifier_decision": "passed",
                "verifier_message": "All sandbox tests passed successfully.",
                "error_feedback": None
            }

        #Case B: Max retries exceeded -> Stop looping to prevent infinite recursion
        if retry_count >= self.max_retries:
            return {
                **state,
                "verifier_decision": "max_retries_exceeded",
                "verifier_message": f"Tests failed after {self.max_retries} attempts. Halting optimizer loop.",
                "error_feedback": sandbox_result.get("stderr") or sandbox_result.get("stdout")
            }

        #Case C: Tests Failed -> Loop Back to Optimizer Agent
        stderr_log = sandbox_result.get("stderr", "")
        stdout_log = sandbox_result.get("stdout", "")
        error_details = stderr_log if stderr_log.strip() else stdout_log

        return {
            **state,
            "optimizer_retry_count": retry_count + 1,
            "verifier_decision": "loop_optimizer",
            "verifier_message": f"Tests failed on attempt {retry_count + 1}. Looping back to Optimizer Agent with error logs.",
            "error_feedback": error_details
        }

# LangGraph / Workflow Decision Function
def verifier_node(state: Dict[str, Any]) -> Dict[str, Any]:
    #State node function for Step 5
    verifier = Verifier(max_retries=3)
    return verifier.verify_optimizer_output(state)


def route_verifier_decision(state: Dict[str, Any]) -> Literal["optimizer_agent", "proceed", "halt"]:
    #Conditional edge router for LangGraph
    decision = state.get("verifier_decision")
    if decision == "loop_optimizer":
        return "optimizer_agent"
    elif decision == "passed":
        return "proceed"
    else:
        return "halt"


# Direct Test Execution
if __name__ == "__main__":
    mock_failed_state = {
        "optimizer_retry_count": 0,
        "sandbox_test_result": {
            "passed": False,
            "exit_code": 1,
            "stderr": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
            "stdout": ""
        }
    }

    result = verifier_node(mock_failed_state)
    print("Test Failed Output")
    print(f"Decision: {result['verifier_decision']}")
    print(f"Next Node: {route_verifier_decision(result)}")
    print(f"Retry Count: {result['optimizer_retry_count']}")
    print(f"Feedback Sent Back: {result['error_feedback']}\n")

    mock_passed_state = {
        "optimizer_retry_count": 1,
        "sandbox_test_result": {
            "passed": True,
            "exit_code": 0,
            "stderr": "",
            "stdout": "Ran 5 tests in 0.02s ... OK"
        }
    }

    result = verifier_node(mock_passed_state)
    print("Test Passed Output ")
    print(f"Decision: {result['verifier_decision']}")
    print(f"Next Node: {route_verifier_decision(result)}")