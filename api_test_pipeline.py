import os
from dotenv import load_dotenv
from ingest import run_ingestion
from agents.security_agent import run_security_audit_on_ingestion

load_dotenv()

VULNERABLE_TEST_CODE = """
import sqlite3

AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"

def fetch_user_profile(user_input):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    # SQL Injection Vulnerability
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    cursor.execute(query)
    return cursor.fetchone()
"""

if __name__ == "__main__":
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print(" Error: GROQ_API_KEY not found in .env file!")
    else:
        print("1. Running Ingestion Step...")
        ingest_res = run_ingestion(source_type="code_snippet", raw_code=VULNERABLE_TEST_CODE, language="python")
        print(f"   Ingested {ingest_res['total_files']} file(s).\n")

        print("2. Running Security Auditor Agent (Groq GPT-OSS 120B)...")
        audit_results = run_security_audit_on_ingestion(
            ingestion_output=ingest_res, 
            api_key=api_key,
            model_name="openai/gpt-oss-120b"  
        )

        print("\n--- AUDIT RESULTS ---")
        for res in audit_results:
            file = res["file_path"]
            report = res["report"]
            print(f" File: {file}")
            print(f"Summary: {report['summary']}\n")
            for v in report["vulnerabilities"]:
                print(f"   [{v['severity']}] {v['vulnerability_type']}")
                print(f"     Exploit: {v['exploit_vector']}")
                print(f"     Patch: {v['recommended_patch']}\n")