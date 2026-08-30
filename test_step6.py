import os
from human_review_pr import HumanReviewAction, handle_user_review

def test_step6_flow():
    # Simulated state from Step 5
    mock_step5_state = {
        "repo_url": "https://github.com/TwoBrainCellsCoding/Autonomous-Multi-Agent-AI-Security-Auditor-Code-Optimizer",  # Replace with a real test repo to test PR creation
        "proposed_patches": [
            {
                "file_path": "README.md",
                "patched_code": "# Autonomous Multi-Agent AI Audit\n\nOptimized & Hardened."
            }
        ],
        "verifier_message": "All sandbox AST syntax tests passed."
    }

    print("==================================================")
    print("TEST 1: HUMAN GATE - REQUEST CHANGES LOOP BACK")
    print("==================================================")
    review_request = HumanReviewAction(
        audit_id="audit_test_123",
        action="request_changes",
        feedback_comments="Please make the function asynchronous and add docstrings."
    )
    res_loop = handle_user_review(review_request, state_data=mock_step5_state)
    print("Result:", res_loop)

    print("\n==================================================")
    print("TEST 2: HUMAN GATE - APPROVE & PR CREATION")
    print("==================================================")
    if os.getenv("GITHUB_TOKEN"):
        review_approve = HumanReviewAction(
            audit_id="audit_test_123",
            action="approve"
        )
        try:
            res_approve = handle_user_review(review_approve, state_data=mock_step5_state)
            print("Result:", res_approve)
        except Exception as e:
            print(f"PR Creation Skipped / Error (Verify repo URL & token): {e}")
    else:
        print("[!] Set GITHUB_TOKEN in your .env to test actual GitHub PR creation.")

if __name__ == "__main__":
    test_step6_flow()