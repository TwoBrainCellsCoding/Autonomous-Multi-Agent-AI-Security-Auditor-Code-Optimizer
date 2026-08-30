import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, AliasChoices
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


#PYDANTIC OUTPUT SCHEMA 
class Vulnerability(BaseModel):
    file_path: str = Field(
        default="unknown",
        validation_alias=AliasChoices("file_path", "location"),
        description="Relative path of the file containing the flaw"
    )
    line_number: Optional[str] = Field(
        default="N/A", 
        description="Approximate line location or function name"
    )
    vulnerability_type: str = Field(
        validation_alias=AliasChoices("vulnerability_type", "type"),
        description="Name of security flaw (e.g., SQLi, Hardcoded Secret, XSS)"
    )
    severity: str = Field(
        default="HIGH", 
        description="CRITICAL, HIGH, MEDIUM, or LOW"
    )
    exploit_vector: str = Field(
        default="", 
        description="Step-by-step explanation of how a hacker can exploit this flaw"
    )
    recommended_patch: str = Field(
        validation_alias=AliasChoices("recommended_patch", "remediation", "description"),
        description="Specific code change or defensive pattern to fix the flaw"
    )


class SecurityAuditReport(BaseModel):
    summary: str = Field(
        default="No issues found or analysis completed.", 
        description="High-level summary of security posture and total risks found"
    )
    vulnerabilities: List[Vulnerability] = Field(
        default_factory=list, 
        description="List of identified security vulnerabilities"
    )


#RED-TEAM HACKER SYSTEM PROMPT 
SECURITY_SYSTEM_PROMPT = """You are an elite Red-Team Security Auditor and Application Penetration Tester.
Your task is to analyze code files produced by developers or AI systems and spot security risks before deployment.

Analyze the code for:
1. Injection vulnerabilities (SQLi, Command Injection, OS Exec)
2. Hardcoded API keys, JWT secrets, or DB credentials
3. Insecure deserialization or unsafe `eval()` / `exec()` calls
4. Missing input validation/sanitization and broken authorization

Be realistic and specific. Output your analysis exclusively as a JSON object matching this exact structure:
{{
  "summary": "Brief summary of security findings",
  "vulnerabilities": [
    {{
      "file_path": "path/to/file.py",
      "line_number": "12",
      "vulnerability_type": "Command Injection",
      "severity": "HIGH",
      "exploit_vector": "Detailed explanation of exploit step",
      "recommended_patch": "Corrected code snippet"
    }}
  ]
}}
If no vulnerabilities exist, return an empty vulnerabilities list."""


#CORE SECURITY AUDITOR FUNCTION 
def analyze_single_file(
    file_path: str, 
    code_content: str, 
    api_key: str, 
    model_name: str = "openai/gpt-oss-120b"
) -> SecurityAuditReport:
  
    #Sends code content directly to Groq via native ChatGroq integration.
    llm = ChatGroq(
        model=model_name,
        groq_api_key=api_key,
        temperature=0.1
    )

    structured_llm = llm.with_structured_output(SecurityAuditReport, method="json_mode")

    prompt = ChatPromptTemplate.from_messages([
        ("system", SECURITY_SYSTEM_PROMPT),
        ("user", "File Path: {file_path}\n\nCode Content:\n```\n{code_content}\n```")
    ])

    chain = prompt | structured_llm
    return chain.invoke({"file_path": file_path, "code_content": code_content})


def run_security_audit_on_ingestion(
    ingestion_output: Dict[str, Any], 
    api_key: str, 
    model_name: str = "openai/gpt-oss-120b"
) -> List[Dict[str, Any]]:
    file_manifest = ingestion_output.get("file_manifest", [])
    all_audit_results = []

    for file_info in file_manifest:
        if not file_info.get("is_code", False):
            continue

        path = file_info.get("path", "unknown")
        content = file_info.get("content", "")

        if not content.strip():
            continue

        report = analyze_single_file(
            file_path=path, 
            code_content=content, 
            api_key=api_key, 
            model_name=model_name
        )

        all_audit_results.append({
            "file_path": path,
            "report": report.model_dump()
        })

    return all_audit_results