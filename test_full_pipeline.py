import os
import tempfile
from dotenv import load_dotenv

# File Imports
from ingest import run_ingestion
from agents.security_agent import run_security_audit_on_ingestion
from agents.optimizer_agent import run_optimizer_on_ingestion
from sandbox import SandboxExecutor
from agents.security_critic import security_critic_node
from agents.optimizerAgent_verifier import verifier_node as optimizer_verifier_node
from verifier import central_verifier_node, route_next_step
from agents.human_in_loop import human_in_loop_node

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def apply_patches_to_environment(test_dir, ingestion_data, proposed_patches):
    """Writes patched code to disk and syncs ingestion memory for next iteration."""
    for patch in proposed_patches:
        target_path = patch["file_path"]
        patched_code = patch["patched_code"]
        
        # 1. Update physical file on disk
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(patched_code)
            
        # 2. Update ingestion_data manifest in memory
        for file_info in ingestion_data.get("file_manifest", []):
            if file_info["path"] == target_path:
                file_info["content"] = patched_code

def run_pipeline():
    # 1. Create temporary test codebase
    test_dir = tempfile.mkdtemp(prefix="pipeline_test_")
    vulnerable_file = os.path.join(test_dir, "app.py")
    
    with open(vulnerable_file, "w") as f:
        f.write('''import sqlite3

def fetch_user(username):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    # Syntax error below
    query = f"SELECT * FROM users WHERE username = '{username}'
    return cursor.execute(query).fetchone()
''')
        
    #Another code example to try Clean Code (Should pass Iteration 1 directly)
        '''import sqlite3

    def fetch_user(username):
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE username = ?"
        return cursor.execute(query, (username,)).fetchone()

    def compute_sum(numbers):
        return sum(numbers)

        # ANOTHER CODE TO TRY Multiple Vulnerabilities (Command Injection + Hardcoded Credentials)
            import os

    AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"

    def run_system_command(user_input):
        # Command injection vulnerability
        os.system(f"ping -c 1 {user_input}")'''
 
    print("=== STEP 1: REPO INGESTION ===")
    ingestion_data = run_ingestion(source_type="repository", local_path=test_dir)
    print(f"Ingested files: {len(ingestion_data.get('file_manifest', []))}")

    # Initial State
    state = {
        "local_path": test_dir,
        "ingestion_data": ingestion_data,
        "optimizer_retry_count": 0,
        "security_retry_count": 0
    }

    max_loops = 5
    loop_count = 0

    while loop_count < max_loops:
        loop_count += 1
        print(f"\n--- PIPELINE ITERATION {loop_count} ---")

        # 2. Security Auditor
        print("-> Running Security Auditor...")
        security_results = run_security_audit_on_ingestion(state["ingestion_data"], GROQ_API_KEY)
        state["security_audit_results"] = security_results

        # 3. Security Critic Node
        print("-> Evaluating Security Critic...")
        state = security_critic_node(state)
        print(f"Security Critic Decision: {state.get('security_critic_decision')}")

        # 4. Code Optimizer Agent
        print("-> Running Code Optimizer...")
        optimizer_results = run_optimizer_on_ingestion(state["ingestion_data"], GROQ_API_KEY)
        proposed_patches = [
            {"file_path": item["file_path"], "patched_code": item["patched_code"]}
            for item in optimizer_results
        ]
        state["proposed_patches"] = proposed_patches

        # 5. Sandbox Execution
        print("-> Running Sandbox Tests...")
        sandbox = SandboxExecutor()
        sandbox_result = sandbox.run_tests(test_dir, proposed_patches)
        state["sandbox_test_result"] = sandbox_result
        print(f"Sandbox Test Status: {sandbox_result.get('status')}")

        # 6. Optimizer Verifier Node
        state = optimizer_verifier_node(state)
        print(f"Optimizer Verifier Decision: {state.get('verifier_decision')}")

        # 7. Central Verifier Check
        state = central_verifier_node(state)
        next_step = route_next_step(state)
        print(f"Central Router Next Step: {next_step}")

        # 8. Loop & Edge Control
        if next_step == "human_in_loop":
            print("\n=== STEP 8: HUMAN-IN-THE-LOOP ===")
            final_state = human_in_loop_node(state)
            print(f"Final Pipeline Status: {final_state.get('pipeline_status')}")
            break
        elif next_step in ["retry_optimizer", "optimizer_agent"]:
            print("[LOOP] Sandbox tests failed. Applying patch attempt & retrying Optimizer...")
            apply_patches_to_environment(test_dir, state["ingestion_data"], proposed_patches)
            state["optimizer_retry_count"] += 1
            continue
        elif next_step in ["reaudit_security", "security_agent"]:
            print("[LOOP] Applying generated patch & re-auditing with Security Agent...")
            apply_patches_to_environment(test_dir, state["ingestion_data"], proposed_patches)
            state["security_retry_count"] += 1
            continue
        else:
            print("[HALT] Exceeded maximum retry limits or hit critical error.")
            break

if __name__ == "__main__":
    run_pipeline()