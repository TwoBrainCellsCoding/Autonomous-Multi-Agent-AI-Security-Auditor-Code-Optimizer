import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


# --- 1. PYDANTIC OUTPUT SCHEMA ---
class OptimizationDetail(BaseModel):
    area: str = Field(description="Area of code optimized (e.g., algorithmic complexity, caching, async)")
    issue_description: str = Field(description="Description of the performance bottleneck or inefficiency")
    time_complexity_before: str = Field(default="N/A", description="Estimated Big-O before optimization")
    time_complexity_after: str = Field(default="N/A", description="Estimated Big-O after optimization")


class OptimizerReport(BaseModel):
    summary: str = Field(description="Summary of refactorings and performance improvements")
    optimizations: List[OptimizationDetail] = Field(default_factory=list, description="List of optimizations made")
    patched_code: str = Field(description="Complete refactored and optimized source code for the file")


# --- 2. OPTIMIZER SYSTEM PROMPT ---
OPTIMIZER_SYSTEM_PROMPT = """You are a Principal Software Engineer and Performance Optimization Expert.
Your task is to review source code and refactor it for maximum performance, lower memory usage, and cleaner architecture.

Focus on:
1. Algorithmic efficiency (reducing O(N^2) to O(N) or O(N log N))
2. Database query efficiency, batching, and unnecessary I/O
3. Memory leaks, redundant allocations, and generator/stream usage
4. Modern idiomatic conventions and readability

CRITICAL RULE:
You must return the COMPLETE modified source code in `patched_code`. 
Do NOT truncate with placeholders like '// rest of code here'. The patched code must be fully runnable and pass tests.
If no changes are necessary, return the original code inside `patched_code`.
"""


# --- 3. CORE OPTIMIZER FUNCTION ---
def optimize_single_file(
    file_path: str,
    code_content: str,
    api_key: str,
    model_name: str = "llama-3.3-70b-versatile"
) -> OptimizerReport:
    """Sends code to Groq for performance refactoring."""
    llm = ChatGroq(
        model=model_name,
        groq_api_key=api_key,
        temperature=0.1
    )

    structured_llm = llm.with_structured_output(OptimizerReport)

    prompt = ChatPromptTemplate.from_messages([
        ("system", OPTIMIZER_SYSTEM_PROMPT),
        ("user", "File Path: {file_path}\n\nOriginal Code:\n```\n{code_content}\n```")
    ])

    chain = prompt | structured_llm
    return chain.invoke({"file_path": file_path, "code_content": code_content})


def run_optimizer_on_ingestion(
    ingestion_output: Dict[str, Any],
    api_key: str,
    model_name: str = "llama-3.3-70b-versatile"
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