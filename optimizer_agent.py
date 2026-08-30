import os
import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI


# ==========================================
# 1. Output Schemas
# ==========================================
class OptimizationItem(BaseModel):
    issue_type: str = Field(description="e.g., Algorithmic Complexity, Memory Overhead, Redundant I/O, Clean Code")
    description: str = Field(description="Detailed explanation of the performance issue or inefficiency")
    original_snippet: str = Field(description="Targeted snippet from original code")
    improved_snippet: str = Field(description="Optimized replacement code snippet")
    performance_gain: str = Field(description="Estimated gain (e.g., O(N^2) to O(N), reduced memory allocations)")


class FileOptimizationReport(BaseModel):
    file_path: str
    status: str = Field(description="'optimized', 'no_change_needed', or 'error'")
    optimizations: List[OptimizationItem] = Field(default_factory=list)
    refactored_content: str = Field(description="Full source code with all optimizations applied")


# ==========================================
# 2. Optimization Agent
# ==========================================
class OptimizerAgent:
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.2):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY", "")
        )
        self.parser = JsonOutputParser(pydantic_object=FileOptimizationReport)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert Performance Optimization & Refactoring AI Agent.\n"
                "Your objective is to analyze source code for performance bottlenecks, algorithmic complexity, "
                "memory leaks, and anti-patterns, then output an optimized, production-grade refactored version.\n\n"
                "CRITICAL INSTRUCTIONS:\n"
                "1. Maintain the exact functionality, public interfaces, and class/function signatures to avoid breaking existing unit tests.\n"
                "2. If 'verifier_feedback' or 'user_feedback' is present, resolve every mentioned issue directly.\n"
                "3. You must return ONLY valid JSON matching the schema.\n\n"
                "{format_instructions}"
            )),
            ("user", (
                "File Path: {file_path}\n"
                "Language: {language}\n"
                "Verifier Error/Sandbox Feedback (Step 5): {verifier_feedback}\n"
                "User Review Feedback (Step 6): {user_feedback}\n\n"
                "Source Code:\n"
                "```\n{content}\n```"
            ))
        ])

        self.chain = self.prompt | self.llm | self.parser

    def analyze_and_optimize(
        self,
        file_path: str,
        content: str,
        language: str = "python",
        verifier_feedback: Optional[str] = None,
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes optimization analysis on a single code file.
        """
        try:
            return self.chain.invoke({
                "file_path": file_path,
                "language": language,
                "verifier_feedback": verifier_feedback or "None (Initial Pass)",
                "user_feedback": user_feedback or "None",
                "content": content,
                "format_instructions": self.parser.get_format_instructions()
            })
        except Exception as e:
            return {
                "file_path": file_path,
                "status": "error",
                "error": str(e),
                "optimizations": [],
                "refactored_content": content
            }


# ==========================================
# 3. Node Entrypoint for Step 3
# ==========================================
def run_optimizer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 3 Optimizer Node:
    Consumes output from ingest.py (file_manifest & task_list)
    or loopback feedback from Step 5 Verifier / Step 6 User Gate.
    """
    manifest = state.get("file_manifest", [])
    task_list = state.get("task_list", [])
    
    verifier_feedback = state.get("verifier_feedback", {})
    user_feedback = state.get("user_feedback", {})

    agent = OptimizerAgent()
    optimization_reports: List[Dict[str, Any]] = []
    
    # Store or update proposed patches for Step 4 Sandbox tests
    proposed_patches = state.get("proposed_patches", {})

    # Create content lookup map
    content_map = {item["path"]: item["content"] for item in manifest}
    for file_path, patched_code in proposed_patches.items():
        content_map[file_path] = patched_code

    for task in task_list:
        file_path = task["file_path"]
        language = task.get("language", "python")
        current_code = content_map.get(file_path, "")

        if not current_code:
            continue

        v_feedback = verifier_feedback.get(file_path)
        u_feedback = user_feedback.get(file_path)

        report = agent.analyze_and_optimize(
            file_path=file_path,
            content=current_code,
            language=language,
            verifier_feedback=v_feedback,
            user_feedback=u_feedback
        )

        optimization_reports.append(report)

        if report.get("status") == "optimized":
            proposed_patches[file_path] = report.get("refactored_content", current_code)
            task["status"] = "optimized"

    return {
        **state,
        "optimization_reports": optimization_reports,
        "proposed_patches": proposed_patches,
        "optimizer_status": "completed"
    }


# ==========================================
# 4. Standalone Test Execution
# ==========================================
if __name__ == "__main__":
    sample_code = """
def sum_even_numbers(numbers):
    total = 0
    for i in range(len(numbers)):
        if numbers[i] % 2 == 0:
            total += numbers[i]
    return total
"""
    mock_state = {
        "file_manifest": [{
            "path": "utils.py",
            "extension": ".py",
            "lines": 7,
            "is_code": True,
            "content": sample_code
        }],
        "task_list": [{
            "file_path": "utils.py",
            "language": "python",
            "lines": 7,
            "status": "pending"
        }]
    }

    print("Running Optimizer Agent...")
    result = run_optimizer_agent(mock_state)
    print(json.dumps(result["optimization_reports"], indent=2))