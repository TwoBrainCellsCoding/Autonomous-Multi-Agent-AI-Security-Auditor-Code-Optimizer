import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field,  AliasChoices
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


#PYDANTIC OUTPUT SCHEMA 
class OptimizationDetail(BaseModel):
    area: str = Field(
        default="General Optimization",
        validation_alias=AliasChoices("area", "category", "type"),
        description="Area of code optimized"
    )
    issue_description: str = Field(
        default="Code refactored for performance",
        validation_alias=AliasChoices("issue_description", "description", "issue"),
        description="Description of the performance bottleneck"
    )
    time_complexity_before: str = Field(
        default="N/A",
        validation_alias=AliasChoices("time_complexity_before", "before"),
        description="Estimated Big-O before optimization"
    )
    time_complexity_after: str = Field(
        default="N/A",
        validation_alias=AliasChoices("time_complexity_after", "after"),
        description="Estimated Big-O after optimization"
    )

class OptimizerReport(BaseModel):
    summary: str = Field(
        default="Performance optimization and code cleanup completed.",  # Ensures validation won't fail if omitted by the model
        validation_alias=AliasChoices("summary", "explanation", "details", "description"),
        description="Summary of refactorings made"
    )
    optimizations: List[OptimizationDetail] = Field(
        default_factory=list,
        validation_alias=AliasChoices("optimizations", "details", "changes"),
        description="List of optimizations made"
    )
    patched_code: str = Field(
        default="",
        validation_alias=AliasChoices("patched_code", "optimized_code", "code"),
        description="Complete refactored source code"
    )
#OPTIMIZER SYSTEM PROMPT 
OPTIMIZER_SYSTEM_PROMPT = """You are a Principal Software Engineer and Performance Optimization Expert.

Output your response strictly as a JSON object containing the exact following keys:
{{
  "summary": "High-level summary of the refactoring and optimizations applied",
  "optimizations": [
    {{
      "area": "Algorithmic Efficiency",
      "issue_description": "Reduced redundant passes",
      "time_complexity_before": "O(N)",
      "time_complexity_after": "O(N)"
    }}
  ],
  "patched_code": "Complete, fully functional optimized source code string"
}}

CRITICAL RULE: Always include 'summary' and 'patched_code' in the JSON output."""


#CORE OPTIMIZER FUNCTION 
def optimize_single_file(
    file_path: str,
    code_content: str,
    api_key: str,
    model_name: str = "openai/gpt-oss-120b"
) -> OptimizerReport:
    """Sends code to Groq for performance refactoring."""
    llm = ChatGroq(
        model=model_name,
        groq_api_key=api_key,
        temperature=0.1
    )

    structured_llm = llm.with_structured_output(OptimizerReport, method="json_mode")

    prompt = ChatPromptTemplate.from_messages([
        ("system", OPTIMIZER_SYSTEM_PROMPT),
        ("user", "File Path: {file_path}\n\nOriginal Code:\n```\n{code_content}\n```")
    ])

    chain = prompt | structured_llm
    return chain.invoke({"file_path": file_path, "code_content": code_content})


def run_optimizer_on_ingestion(
    ingestion_output: Dict[str, Any],
    api_key: str,
    model_name: str = "openai/gpt-oss-120b"
) -> List[Dict[str, Any]]:
    """Runs performance optimization across all code files in the file manifest."""
    file_manifest = ingestion_output.get("file_manifest", [])
    all_optimizer_results = []

    for file_info in file_manifest:
        if not file_info.get("is_code", False):
            continue

        path = file_info.get("path", "unknown")
        content = file_info.get("content", "")

        if not content.strip():
            continue

        report = optimize_single_file(
            file_path=path,
            code_content=content,
            api_key=api_key,
            model_name=model_name
        )

        all_optimizer_results.append({
            "file_path": path,
            "report": report.model_dump(),
            "patched_code": report.patched_code
        })

    return all_optimizer_results