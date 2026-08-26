import os
from typing import Dict, List, Any, Tuple, Optional

# Directories and file patterns to ignore during scanning
IGNORED_DIRS = {
    ".git", "__pycache__", "node_modules", "venv", ".venv", 
    "agent-env", "multiAgent", "dist", "build", ".idea", ".vscode", "coverage"
}

IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".pdf", 
    ".zip", ".tar", ".gz", ".lock", ".pyc", ".min.js", ".min.css",
    ".map", ".exe", ".bin", ".woff", ".woff2", ".ttf", ".eot"
}

# Recognized code extensions mapped to language labels
CODE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".go": "go",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".sh": "bash",
    ".sql": "sql",
    ".html": "html",
    ".css": "css"
}


def _process_repository(local_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Scans the cloned directory from Step 1, extracts code contents,
    and builds a prioritized task list.
    """
    if not os.path.exists(local_path):
        raise ValueError(f"Local repository path does not exist: {local_path}")

    file_manifest: List[Dict[str, Any]] = []
    task_list: List[Dict[str, Any]] = []

    for root, dirs, files in os.walk(local_path):
        # In-place directory filtering
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for file in files:
            _, ext = os.path.splitext(file)
            ext = ext.lower()

            if ext in IGNORED_EXTENSIONS:
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, local_path)

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                line_count = len(content.splitlines())
                is_code = ext in CODE_EXTENSIONS

                file_manifest.append({
                    "path": rel_path,
                    "extension": ext,
                    "lines": line_count,
                    "is_code": is_code,
                    "content": content
                })

                if is_code and line_count > 0:
                    task_list.append({
                        "file_path": rel_path,
                        "language": CODE_EXTENSIONS.get(ext, "unknown"),
                        "lines": line_count,
                        "status": "pending"
                    })
            except Exception:
                continue

    # Prioritize larger files first
    task_list.sort(key=lambda item: item["lines"], reverse=True)
    return file_manifest, task_list


def _process_snippet(raw_code: str, language: str = "python") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Wraps a raw code snippet into the same file manifest and task list structure.
    """
    line_count = len(raw_code.splitlines())
    virtual_filename = f"snippet.{language}"

    file_manifest = [{
        "path": virtual_filename,
        "extension": f".{language}",
        "lines": line_count,
        "is_code": True,
        "content": raw_code
    }]

    task_list = [{
        "file_path": virtual_filename,
        "language": language,
        "lines": line_count,
        "status": "pending"
    }]

    return file_manifest, task_list


def run_ingestion(
    source_type: str,
    local_path: Optional[str] = None,
    raw_code: Optional[str] = None,
    language: str = "python"
) -> Dict[str, Any]:
    """
    Step 2 ingestion entry point called by Step 1.
    """
    if source_type == "repository":
        if not local_path:
            raise ValueError("Missing 'local_path' for repository source type.")
        file_manifest, task_list = _process_repository(local_path)

    elif source_type == "code_snippet":
        if not raw_code:
            raise ValueError("Missing 'raw_code' for code_snippet source type.")
        file_manifest, task_list = _process_snippet(raw_code, language)

    else:
        raise ValueError(f"Unsupported source_type: {source_type}")

    return {
        "source_type": source_type,
        "total_files": len(file_manifest),
        "total_tasks": len(task_list),
        "file_manifest": file_manifest,
        "task_list": task_list
    }