from typing import Dict, Any, Literal

def central_verifier_node(state: Dict[str, Any]) -> Dict[str, Any]:
    #Evaluates both Sandbox functional tests and Security Critic reports.
    
    sandbox_result = state.get("sandbox_test_result", {})
    tests_passed = sandbox_result.get("passed", False)
    opt_retry = state.get("optimizer_retry_count", 0)
    
    sec_critic_decision = state.get("security_critic_decision")
    sec_retry = state.get("security_retry_count", 0)

    #  Check Sandbox Functional Tests
    if not tests_passed:
        if opt_retry >= 3:
            state["final_status"] = "halted_optimizer_max_retries"
            return state
        state["route_decision"] = "retry_optimizer"
        state["optimizer_retry_count"] = opt_retry + 1
        return state

    # Check Security Auditor Findings
    if sec_critic_decision == "loop_security":
        if sec_retry >= 3:
            state["final_status"] = "halted_security_max_retries"
            return state
        state["route_decision"] = "reaudit_security"
        return state

    # Both Checks Pass -> Proceed to Human-in-the-Loop
    state["route_decision"] = "human_in_loop"
    return state


def route_next_step(state: Dict[str, Any]) -> Literal["optimizer_agent", "security_agent", "human_in_loop", "halt"]:
    #Conditional Edge function for LangGraph
    decision = state.get("route_decision")
    if decision == "retry_optimizer":
        return "optimizer_agent"
    elif decision == "reaudit_security":
        return "security_agent"
    elif decision == "human_in_loop":
        return "human_in_loop"
    else:
        return "halt"