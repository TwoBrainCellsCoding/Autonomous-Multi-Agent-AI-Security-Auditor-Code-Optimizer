from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import uvicorn
from typing import Optional
import os
import tempfile
from git import Repo

app = FastAPI(
    title="Autonomous Security & Refactoring Multi-Agent Engine",
    description="Input endpoint receiving repository URLs or raw code snippets for automated security auditing.",
    version="1.0.0"
)

# Define request body structure
class AuditRequest(BaseModel):
    # Option A: User sends a Git repo URL
    repo_url: Optional[HttpUrl] = None
    # Option B: User sends raw code snippet
    code_snippet: Optional[str] = None
    # Optional programming language hint
    language: Optional[str] = "python"

    def validate_input(self):
        if not self.repo_url and not self.code_snippet:
            raise ValueError("You must provide either 'repo_url' or 'code_snippet'.")
        if self.repo_url and self.code_snippet:
            raise ValueError("Provide 'repo_url' OR 'code_snippet', not both.")


@app.get("/")
def read_root():
    return {"status": "online", "engine": "Multi-Agent Security Engine API"}


@app.post("/api/v1/audit")
async def audit_code(payload: AuditRequest):
    """
    Gateway Endpoint: Receives either a Git URL or raw code chunk 
    and prepares it for the Ingestion / Planner layer.
    """
    try:
        payload.validate_input()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Scenario A: Processing raw code snippet
    if payload.code_snippet:
        return {
            "status": "success",
            "source_type": "code_snippet",
            "language": payload.language,
            "data": payload.code_snippet,
            "message": "Raw code snippet received successfully. Ready for agent ingestion."
        }

    # Scenario B: Processing Git repository URL
    if payload.repo_url:
        target_url = str(payload.repo_url)
        # Create a temporary directory to clone the repo into
        temp_dir = tempfile.mkdtemp(prefix="agent_audit_")
        
        try:
            # Clone the repository
            Repo.clone_from(target_url, temp_dir, depth=1)
            
            # Count files in cloned directory (quick verification)
            cloned_files = []
            for root, _, files in os.walk(temp_dir):
                if ".git" in root:
                    continue
                for file in files:
                    cloned_files.append(os.path.relpath(os.path.join(root, file), temp_dir))

            return {
                "status": "success",
                "source_type": "repository",
                "repo_url": target_url,
                "local_path": temp_dir,
                "file_count": len(cloned_files),
                "preview_files": cloned_files[:10],  # Show first 10 files
                "message": "Repository cloned successfully. Ready for Ingestion Node."
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to clone repository: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)