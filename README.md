# Autonomous-Multi-Agent-AI-Security-Auditor-Code-Optimizer
An autonomous, multi-agent AI pipeline designed to ingest code repositories, run parallel security vulnerability auditing and algorithmic performance refactoring using Groq LLMs, verify proposed code patches in an isolated sandbox, and automate GitHub Pull Requests with a Human-in-the-Loop review gate.
# # Architecture Diagram


# Tech Stack & Dependencies
LLM Engine & Inference: Groq (llama-3.3-70b-versatile)
Agent Framework & State: langgraph, langchain-core, langchain-groq, pydantic
Web Framework: FastAPI, uvicorn
Git & Version Control: GitPython, PyGithub
State Persistence & Checkpointer: Redis
Testing & Sandboxing: Python subprocess, tempfile, pytest, compileall
Containerization: Docker

# Setup and Execution Guide
# 1. Clone the Repository & Setup Environment
Bash
git clone https://github.com/TwoBrainCellsCoding/Autonomous-Multi-Agent-AI-Security-Auditor-Code-Optimizer.git.
cd Autonomous-Multi-Agent-AI-Security-Auditor-Code-Optimizer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --no-cache-dir -r requirements.txt

# 2. Configure Environment Variables (.env)
Code snippet
GROQ_API_KEY=gsk_your_groq_api_key_here
GITHUB_TOKEN=ghp_your_github_token_here
REDIS_HOST=localhost
REDIS_PORT=6379 

# 3. Run the FastAPI Server
Bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
Interactive API docs are accessible at http://localhost:8000/docs.

# 4. Run with Docker
Bash
docker build -t sec-auditor-engine .
docker run -d -p 8000:8000 --env-file .env --name sec-auditor-app sec-auditor-engine


