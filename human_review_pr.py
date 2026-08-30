import os
import json
import redis
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from github import Github, GithubException
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


#Human Review Request Schema
class HumanReviewAction(BaseModel):
    audit_id: str = Field(description="Unique ID of the audit session saved in Step 5")
    action: str = Field(description="'review' to inspect details, 'approve' to open PR, or 'request_changes' to loop back")
    feedback_comments: Optional[str] = Field(
        default="", 
        description="Detailed user feedback/instructions if requesting changes"
    )


#GitHub Automation Service
class GitHubPRService:
    def __init__(self, token: Optional[str] = None):
        self.token = token or GITHUB_TOKEN
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN in your .env file.")
        self.gh = Github(self.token)

    @staticmethod
    def _extract_repo_name(repo_url: str) -> str:
        """Extracts 'owner/repo' from a GitHub URL."""
        clean_url = repo_url.rstrip("/").removesuffix(".git")
        parts = clean_url.split("/")
        return f"{parts[-2]}/{parts[-1]}"

    def create_pull_request_with_patches(
        self,
        repo_url: str,
        patches: List[Dict[str, str]],
        audit_summary: str = "Automated security hardening and performance refactoring."
    ) -> Dict[str, Any]:
        """
        Creates a new branch, commits verified patches, and opens a Pull Request.
        """
        repo_name = self._extract_repo_name(repo_url)
        repo = self.gh.get_repo(repo_name)
        
        default_branch = repo.default_branch
        source_ref = repo.get_git_ref(f"heads/{default_branch}")
        base_sha = source_ref.object.sha

        # Create unique branch name
        branch_name = f"agent-patch-{os.urandom(4).hex()}"
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_sha)

        # Commit proposed patches to the new branch
        for patch in patches:
            file_path = patch["file_path"]
            patched_code = patch["patched_code"]

            try:
                existing_file = repo.get_contents(file_path, ref=branch_name)
                repo.update_file(
                    path=file_path,
                    message=f"refactor(agent): apply verified optimizations & security fixes to {file_path}",
                    content=patched_code,
                    sha=existing_file.sha,
                    branch=branch_name
                )
            except GithubException:
                repo.create_file(
                    path=file_path,
                    message=f"feat(agent): add security-hardened {file_path}",
                    content=patched_code,
                    branch=branch_name
                )

        # Open Pull Request
        pr_body = (
            "Autonomous Multi-Agent AI Audit & Optimizer Report\n\n"
            "Summary of Changes\n"
            f"{audit_summary}\n\n"
            "---\n"
            "Verified and tested automatically via sandboxed execution.*"
        )

        pr = repo.create_pull(
            title=" [Multi-Agent] Security Hardening & Performance Optimizations",
            body=pr_body,
            head=branch_name,
            base=default_branch
        )

        return {
            "status": "success",
            "pr_url": pr.html_url,
            "pr_number": pr.number,
            "branch_created": branch_name
        }

#Review Decision Gateway
def handle_user_review(review: HumanReviewAction, state_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluates human input and routes accordingly.
    """
    session_state = state_data

    # If state not passed in-memory, load from Redis
    if not session_state:
        try:
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            state_raw = r.get(f"audit_session:{review.audit_id}")
            if state_raw:
                session_state = json.loads(state_raw)
        except Exception:
            session_state = None

    if not session_state:
        raise ValueError(f"No active state found for Audit ID: {review.audit_id}")

    # Branch A: Inspection / Read-only View
    if review.action == "review":
        return {
            "status": "in_review",
            "audit_id": review.audit_id,
            "repo_url": session_state.get("repo_url"),
            "proposed_patches": session_state.get("proposed_patches", []),
            "security_reports": session_state.get("security_reports", []),
            "optimizer_reports": session_state.get("optimizer_reports", []),
            "verifier_summary": session_state.get("verifier_message", "")
        }

    # Branch B: User Requests Changes -> Loop Back with Feedback
    elif review.action == "request_changes":
        session_state["human_feedback"] = review.feedback_comments
        session_state["human_gate_status"] = "changes_requested"
        session_state["target_loop_node"] = "optimizer_agent"

        return {
            "status": "loop_back",
            "message": "User requested changes. Feedback queued for Optimizer/Security agents.",
            "feedback": review.feedback_comments,
            "next_node": "optimizer_agent"
        }

    # Branch C: User Approves -> Open GitHub Pull Request
    elif review.action == "approve":
        repo_url = session_state.get("repo_url")
        proposed_patches = session_state.get("proposed_patches", [])
        summary = session_state.get("verifier_message", "Clean code patches approved by human reviewer.")

        if not repo_url or not proposed_patches:
            raise ValueError("Missing repo_url or proposed_patches in state.")

        pr_client = GitHubPRService()
        pr_response = pr_client.create_pull_request_with_patches(
            repo_url=repo_url,
            patches=proposed_patches,
            audit_summary=summary
        )

        session_state["human_gate_status"] = "approved"
        session_state["pr_details"] = pr_response

        return {
            "status": "completed",
            "message": "Pull Request created successfully.",
            "pr_details": pr_response
        }

    else:
        raise ValueError(f"Invalid review action '{review.action}'. Must be 'review', 'approve', or 'request_changes'.")