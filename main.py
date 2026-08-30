import os
import uuid
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import Schemas & Helper Functions
from schemas import AuditRequest
from ingest import run_ingestion
from agents.security_agent import run_security_audit_on_ingestion
from agents.optimizer_agent import run_optimizer_on_ingestion
from sandbox import SandboxExecutor
from agents.security_critic import security_critic_node
from agents.optimizerAgent_verifier import verifier_node as optimizer_verifier_node
from verifier import central_verifier_node, route_next_step
from redis_checkpointer import get_redis_state_manager
from human_review_pr import HumanReviewAction, handle_user_review

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MAX_RETRIES = 3


class AutonomousEnginePipeline:
    #Main Orchestrator tying together FastAPI Ingestion, Agents, Sandbox,
    #Verifier/Critic Loops, Redis Checkpointing, and Human Approval PR Gateway.
    

    def __init__(self, groq_api_key: Optional[str] = None):
        self.api_key = groq_api_key or GROQ_API_KEY
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is missing. Check your .env configuration.")
        self.redis_mgr = get_redis_state_manager()

    def _apply_patches_in_memory_and_disk(
        self, 
        state: Dict[str, Any], 
        proposed_patches: list
    ) -> None:
        """Applies generated patches to active state and workspace files."""
        local_path = state.get("local_path")
        ingestion_data = state.get("ingestion_data", {})

        for patch in proposed_patches:
            rel_path = patch["file_path"]
            patched_code = patch["patched_code"]

            if local_path and os.path.exists(local_path):
                full_path = os.path.join(local_path, rel_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(patched_code)

            for file_info in ingestion_data.get("file_manifest", []):
                if file_info["path"] == rel_path:
                    file_info["content"] = patched_code

    def run_autonomous_loop(self, request: AuditRequest, cloned_local_path: Optional[str] = None) -> Dict[str, Any]:
        #Executes the autonomous loop: Ingest -> [Agents] -> Sandbox -> Verifiers -> Loop/Interrupt.
        audit_id = f"audit-{uuid.uuid4().hex[:8]}"
        print(f" INITIALIZING AUDIT SESSION: {audit_id}")

        #Ingestion Processing
        print("\n[Step 1] Ingesting Codebase...")
        if request.repo_url or cloned_local_path:
            target_path = cloned_local_path or str(request.repo_url)
            ingestion_data = run_ingestion(source_type="repository", local_path=target_path)
        elif request.code_snippet:
            ingestion_data = run_ingestion(
                source_type="code_snippet", 
                raw_code=request.code_snippet, 
                language=request.language or "python"
            )
        else:
            raise ValueError("Invalid request: Provide either repo_url or code_snippet.")

        # Initialize Pipeline State
        state = {
            "audit_id": audit_id,
            "repo_url": str(request.repo_url) if request.repo_url else None,
            "local_path": cloned_local_path,
            "ingestion_data": ingestion_data,
            "proposed_patches": [],
            "optimizer_retry_count": 0,
            "security_retry_count": 0,
            "status": "in_progress"
        }

        # Checkpoint Initial State to Redis
        self.redis_mgr.save_checkpoint(audit_id, state)

        loop_count = 0
        while loop_count < MAX_RETRIES:
            loop_count += 1
            print(f"\n--- PIPELINE ITERATION {loop_count} ---")

            #Security Auditor Agent
            print("-> Running Security Auditor...")
            security_results = run_security_audit_on_ingestion(state["ingestion_data"], self.api_key)
            state["security_audit_results"] = security_results

            #Security Critic Node
            print("-> Running Security Critic...")
            state = security_critic_node(state)

            #Code Optimizer Agent
            print("-> Running Code Optimizer...")
            optimizer_results = run_optimizer_on_ingestion(state["ingestion_data"], self.api_key)
            proposed_patches = [
                {"file_path": item["file_path"], "patched_code": item["patched_code"]}
                for item in optimizer_results
            ]
            state["proposed_patches"] = proposed_patches

            # Sandbox Testing
            print("-> Executing Sandbox Tests...")
            sandbox = SandboxExecutor()
            target_directory = state.get("local_path") or "."
            sandbox_result = sandbox.run_tests(target_directory, proposed_patches)
            state["sandbox_test_result"] = sandbox_result

            #Optimizer Verifier Node
            state = optimizer_verifier_node(state)

            # Central Verifier / Router Decision
            state = central_verifier_node(state)
            next_step = route_next_step(state)
            print(f"Router Output Decision: '{next_step}'")

            # Save state checkpoint after iteration
            self.redis_mgr.save_checkpoint(audit_id, state)

            # Routing Edge Control 
            if next_step == "human_in_loop":
                state["status"] = "awaiting_human_approval"
                self.redis_mgr.save_checkpoint(audit_id, state)
                print(f"\n Pipeline paused at Human Gate. Audit ID: {audit_id}")
                return {
                    "audit_id": audit_id,
                    "status": "awaiting_human_approval",
                    "message": "All automated checks passed. Awaiting human approval to open GitHub PR.",
                    "patches_ready": len(proposed_patches)
                }

            elif next_step in ["retry_optimizer", "optimizer_agent"]:
                print("[LOOP BACK] Tests failed. Patching state & re-running Optimizer...")
                self._apply_patches_in_memory_and_disk(state, proposed_patches)
                state["optimizer_retry_count"] += 1

            elif next_step in ["reaudit_security", "security_agent"]:
                print("[LOOP BACK] Flaws detected. Patching state & re-auditing Security...")
                self._apply_patches_in_memory_and_disk(state, proposed_patches)
                state["security_retry_count"] += 1

            else:
                state["status"] = "failed"
                self.redis_mgr.save_checkpoint(audit_id, state)
                print("[HALT] Exceeded retries or encountered critical failure.")
                return {"audit_id": audit_id, "status": "failed", "message": "Max retries exceeded."}

        state["status"] = "awaiting_human_approval"
        self.redis_mgr.save_checkpoint(audit_id, state)
        return {"audit_id": audit_id, "status": "awaiting_human_approval", "message": "Loop completed."}

    def process_human_review(self, audit_id: str, action: str, feedback: str = "") -> Dict[str, Any]:
        """
        Processes human input from the API/UI gateway and triggers PR creation or feedback loop.
        """
        review_request = HumanReviewAction(
            audit_id=audit_id,
            action=action,
            feedback_comments=feedback
        )
        return handle_user_review(review_request)