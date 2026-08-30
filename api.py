from fastapi import FastAPI, HTTPException
import uvicorn
import tempfile
from git import Repo

from schemas import AuditRequest
from main import AutonomousEnginePipeline
from human_review_pr import HumanReviewAction

app = FastAPI(
    title="Autonomous Security & Refactoring Multi-Agent Engine",
    description="Input endpoint receiving repository URLs or raw code snippets for automated security auditing.",
    version="1.0.0"
)

# Initialize Engine Instance
engine = AutonomousEnginePipeline()

@app.get("/")
def read_root():
    return {"status": "online", "engine": "Multi-Agent Security Engine API"}


@app.post("/api/v1/audit")
async def audit_code(payload: AuditRequest):
    """
    Gateway Endpoint: Clones/Prepares input and triggers the full Multi-Agent pipeline in main.py.
    """
    try:
        payload.validate_input()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Scenario A: Code Snippet Execution
    if payload.code_snippet:
        result = engine.run_autonomous_loop(payload)
        return {"status": "success", "pipeline_result": result}

    # Scenario B: Git Repository Cloning & Execution
    if payload.repo_url:
        target_url = str(payload.repo_url)
        temp_dir = tempfile.mkdtemp(prefix="agent_audit_")
        
        try:
            # Clone repository to local sandbox
            Repo.clone_from(target_url, temp_dir, depth=1)
            
            # Execute Pipeline on local clone path
            result = engine.run_autonomous_loop(payload, cloned_local_path=temp_dir)
            return {
                "status": "success",
                "repo_url": target_url,
                "pipeline_result": result
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@app.post("/api/v1/review")
async def process_review(review: HumanReviewAction):
    """
    Human-in-the-loop Gate: Receives 'approve' or 'request_changes' from frontend.
    Triggers GitHub PR creation on approval or queues feedback loop.
    """
    try:
        review_result = engine.process_human_review(
            audit_id=review.audit_id,
            action=review.action,
            feedback=review.feedback_comments
        )
        return {"status": "success", "review_result": review_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Human review processing failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)