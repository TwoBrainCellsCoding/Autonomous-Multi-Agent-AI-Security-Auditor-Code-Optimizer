from pydantic import BaseModel, HttpUrl
from typing import Optional

class AuditRequest(BaseModel):
    repo_url: Optional[HttpUrl] = None
    code_snippet: Optional[str] = None
    language: Optional[str] = "python"

    def validate_input(self):
        if not self.repo_url and not self.code_snippet:
            raise ValueError("You must provide either 'repo_url' or 'code_snippet'.")
        if self.repo_url and self.code_snippet:
            raise ValueError("Provide 'repo_url' OR 'code_snippet', not both.")