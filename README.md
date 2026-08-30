# Autonomous-Multi-Agent-AI-Security-Auditor-Code-Optimizer
An autonomous, multi-agent AI pipeline designed to ingest code repositories, run parallel security vulnerability auditing and algorithmic performance refactoring using Groq LLMs, verify proposed code patches in an isolated sandbox, and automate GitHub Pull Requests with a Human-in-the-Loop review gate.
# # Architecture Diagram
                  ┌───────────────────────────────┐
                  │ 1. FastAPI Webhook / Trigger  │
                  │   (Repo URL / Local Ingestion)│
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │   2. Ingestion & Task Node    │
                  │ (Clones repo, builds manifest)│
                  └───────────────┬───────────────┘
                                  │
       ┌──────────────────────────┴──────────────────────────┐
       ▼                                                     ▼
┌───────────────────────────────┐           ┌───────────────────────────────┐
│  3a. Red-Team Security Agent  │           │   3b. Code Optimizer Agent    │
│  (OWASP, Secrets, Injections) │           │ (Big-O Refactoring & Clean AST│
└───────────────┬───────────────┘           └───────────────┬───────────────┘
                │                                           │
                └──────────────────────┬────────────────────┘
                                       │ (Proposed Code Patches)
                                       ▼
                  ┌───────────────────────────────┐
                  │   4. Ephemeral Test Sandbox   │
                  │  (Pytest / AST Compiler / NPM)│
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │   5. Loop-Back Verifier Node  │
                  └───────┬───────────────┬───────┘
         (Tests Failed)   │               │ (Tests Passed)
        ┌─────────────────┘               └───────────────────┐
        ▼                                                     ▼
┌───────────────────────────────┐           ┌───────────────────────────────────┐
│ Re-route Feedback to Agents   │           │ Human-in-the-Loop Gate            │
│ (Max retry bounded loop)      │           │ (LangGraph Interrupt Point)       │
└───────────────────────────────┘           └───────────────┬───────────────────┘
                                                            │
                            ┌───────────────────────────────┴───────────────────────────────┐
                            ▼                                                               ▼
        ┌───────────────────────────────────────┐                       ┌───────────────────────────────────────┐
        │        (User Requests Changes)        │                       │            (User Approves)            │
        │ Re-route Feedback to Planner/Optimizer│                       │ Final Merge / PR Automation           │
        │      with Custom Human Prompts        │                       │       (GitHub API Integration)        │
        └───────────────────┬───────────────────┘                       └───────────────────┬───────────────────┘
                            │                                                               │
                            └───────────────────────────────┬───────────────────────────────┘
                                                            ▼
                                        ┌───────────────────────────────────────┐
                                        │    Redis State & Checkpointer Layer   │
                                        │ (Persists Agent Memory, Threads, Logs)│
                                        └───────────────────────────────────────┘
