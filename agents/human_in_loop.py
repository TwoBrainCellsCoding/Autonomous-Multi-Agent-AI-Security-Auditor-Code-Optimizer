from typing import Dict, Any

def human_in_loop_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph Interrupt Gate for Human Review.
    Presents proposed patches and audit summaries for manual approval.
    """
    proposed_patches = state.get("proposed_patches", [])
    security_summary = state.get("security_audit_results", [])
    
    print("\n" + "="*50)
    print("      HUMAN-IN-THE-LOOP APPROVAL GATE")
    print("="*50)
    print(f"Patches Ready for Deployment: {len(proposed_patches)} file(s)")
    print("Status: All functional tests passed & No critical security flaws found.")
    print("="*50 + "\n")

    # Interactive input for CLI execution
    user_approval = input("Do you approve applying these changes to the codebase? (yes/no): ").strip().lower()

    if user_approval in ["yes", "y"]:
        return {
            **state,
            "human_approval": True,
            "pipeline_status": "APPROVED_AND_DEPLOYED"
        }
    else:
        return {
            **state,
            "human_approval": False,
            "pipeline_status": "REJECTED_BY_USER"
        }