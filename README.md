# Autonomous-Multi-Agent-AI-Security-Auditor-Code-Optimizer
An autonomous, multi-agent AI pipeline designed to ingest code repositories, run parallel security vulnerability auditing and algorithmic performance refactoring using Groq LLMs, verify proposed code patches in an isolated sandbox, and automate GitHub Pull Requests with a Human-in-the-Loop review gate.
# # Architecture Diagram
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 1020" width="100%" height="100%">
  <defs>
    <!-- Background Gradient -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>

    <!-- Node Gradient Default -->
    <linearGradient id="nodeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" />
      <stop offset="100%" stop-color="#0f172a" />
    </linearGradient>

    <!-- Blue Node Gradient -->
    <linearGradient id="blueGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e3a8a" />
      <stop offset="100%" stop-color="#172554" />
    </linearGradient>

    <!-- Amber Node Gradient (HITL) -->
    <linearGradient id="amberGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#78350f" />
      <stop offset="100%" stop-color="#451a03" />
    </linearGradient>

    <!-- Red Node Gradient (Security) -->
    <linearGradient id="redGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#7f1d1d" />
      <stop offset="100%" stop-color="#450a0a" />
    </linearGradient>

    <!-- Green Node Gradient (PR) -->
    <linearGradient id="greenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#064e3b" />
      <stop offset="100%" stop-color="#022c22" />
    </linearGradient>

    <!-- Purple Node Gradient (Redis) -->
    <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#581c87" />
      <stop offset="100%" stop-color="#3b0764" />
    </linearGradient>

    <!-- Drop Shadow Filter -->
    <filter id="dropShadow" x="-10%" y="-10%" width="120%" height="125%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.5"/>
    </filter>

    <!-- Arrow Marker Default -->
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38bdf8" />
    </marker>

    <!-- Arrow Marker Red (Loopback) -->
    <marker id="arrowRed" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#f87171" />
    </marker>

    <!-- Arrow Marker Amber (Changes) -->
    <marker id="arrowAmber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#fbbf24" />
    </marker>

    <!-- Arrow Marker Green (Approved) -->
    <marker id="arrowGreen" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#4ade80" />
    </marker>

    <!-- Arrow Marker Purple (Redis) -->
    <marker id="arrowPurple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#c084fc" />
    </marker>
  </defs>

  <style>
    .title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 20px; font-weight: 700; fill: #f8fafc; letter-spacing: 0.5px; }
    .subtitle { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; fill: #94a3b8; }
    .node-title { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; font-weight: 600; fill: #f8fafc; }
    .node-desc { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; fill: #cbd5e1; }
    .label { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11px; font-weight: 600; }
    .line { fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
  </style>

  <!-- Background Canvas -->
  <rect width="950" height="1020" rx="16" fill="url(#bgGrad)" stroke="#334155" stroke-width="1.5" />

  <!-- Header Section -->
  <g transform="translate(475, 45)" text-anchor="middle">
    <text class="title" y="0">Autonomous Multi-Agent AI Security Auditor &amp; Code Optimizer</text>
    <text class="subtitle" y="24">Architecture &amp; Self-Healing Pipeline with Human-in-the-Loop Governance</text>
  </g>

  <!-- ==================== STAGE 1: FASTAPI TRIGGER ==================== -->
  <g transform="translate(325, 95)" filter="url(#dropShadow)">
    <rect width="300" height="56" rx="10" fill="url(#blueGrad)" stroke="#38bdf8" stroke-width="1.5" />
    <text class="node-title" x="150" y="24" text-anchor="middle">1. FastAPI Webhook / Trigger</text>
    <text class="node-desc" x="150" y="42" text-anchor="middle">(Repo URL / Local Ingestion)</text>
  </g>

  <!-- Connector: 1 -> 2 -->
  <path class="line" stroke="#38bdf8" marker-end="url(#arrow)" d="M 475 151 L 475 180" />

  <!-- ==================== STAGE 2: INGESTION & TASK NODE ==================== -->
  <g transform="translate(325, 185)" filter="url(#dropShadow)">
    <rect width="300" height="56" rx="10" fill="url(#nodeGrad)" stroke="#64748b" stroke-width="1.5" />
    <text class="node-title" x="150" y="24" text-anchor="middle">2. Ingestion &amp; Task Node</text>
    <text class="node-desc" x="150" y="42" text-anchor="middle">(Clones repo, builds manifest)</text>
  </g>

  <!-- Connector: 2 -> 3a & 3b Split -->
  <path class="line" stroke="#38bdf8" d="M 475 241 L 475 265" />
  <path class="line" stroke="#38bdf8" d="M 235 265 L 715 265" />
  <path class="line" stroke="#38bdf8" marker-end="url(#arrow)" d="M 235 265 L 235 295" />
  <path class="line" stroke="#38bdf8" marker-end="url(#arrow)" d="M 715 265 L 715 295" />

  <!-- ==================== STAGE 3A: SECURITY AGENT ==================== -->
  <g transform="translate(85, 300)" filter="url(#dropShadow)">
    <rect width="300" height="60" rx="10" fill="url(#redGrad)" stroke="#f87171" stroke-width="1.5" />
    <text class="node-title" x="150" y="25" text-anchor="middle">3a. Red-Team Security Agent</text>
    <text class="node-desc" x="150" y="44" text-anchor="middle">(OWASP, Secrets, Injections)</text>
  </g>

  <!-- ==================== STAGE 3B: OPTIMIZER AGENT ==================== -->
  <g transform="translate(565, 300)" filter="url(#dropShadow)">
    <rect width="300" height="60" rx="10" fill="url(#blueGrad)" stroke="#38bdf8" stroke-width="1.5" />
    <text class="node-title" x="150" y="25" text-anchor="middle">3b. Code Optimizer Agent</text>
    <text class="node-desc" x="150" y="44" text-anchor="middle">(Big-O Refactoring &amp; Clean AST)</text>
  </g>

  <!-- Connector: 3a & 3b -> 4 (Sandbox) Merge -->
  <path class="line" stroke="#38bdf8" d="M 235 360 L 235 390" />
  <path class="line" stroke="#38bdf8" d="M 715 360 L 715 390" />
  <path class="line" stroke="#38bdf8" d="M 235 390 L 715 390" />
  <path class="line" stroke="#38bdf8" marker-end="url(#arrow)" d="M 475 390 L 475 420" />
  <text class="label" x="485" y="408" fill="#94a3b8">Proposed Patches</text>

  <!-- ==================== STAGE 4: SANDBOX RUNNER ==================== -->
  <g transform="translate(325, 425)" filter="url(#dropShadow)">
    <rect width="300" height="56" rx="10" fill="url(#nodeGrad)" stroke="#64748b" stroke-width="1.5" />
    <text class="node-title" x="150" y="24" text-anchor="middle">4. Ephemeral Test Sandbox</text>
    <text class="node-desc" x="150" y="42" text-anchor="middle">(Pytest / AST Compiler / NPM)</text>
  </g>

  <!-- Connector: 4 -> 5 -->
  <path class="line" stroke="#38bdf8" marker-end="url(#arrow)" d="M 475 481 L 475 510" />

  <!-- ==================== STAGE 5: VERIFIER NODE ==================== -->
  <g transform="translate(325, 515)" filter="url(#dropShadow)">
    <rect width="300" height="56" rx="10" fill="url(#nodeGrad)" stroke="#38bdf8" stroke-width="1.5" />
    <text class="node-title" x="150" y="24" text-anchor="middle">5. Loop-Back Verifier Node</text>
    <text class="node-desc" x="150" y="42" text-anchor="middle">(Evaluates Test Execution Output)</text>
  </g>

  <!-- ==================== LOOP-BACK: VERIFIER FAILED ==================== -->
  <!-- Left path back up to Agents -->
  <path class="line" stroke="#f87171" stroke-dasharray="5,4" d="M 325 543 L 50 543 L 50 330 L 80 330" marker-end="url(#arrowRed)" />
  <text class="label" x="60" y="533" fill="#f87171">Tests Failed (Auto-Loopback with stderr)</text>

  <!-- ==================== PATH: VERIFIER PASSED -> HITL ==================== -->
  <path class="line" stroke="#4ade80" marker-end="url(#arrowGreen)" d="M 475 571 L 475 615" />
  <text class="label" x="485" y="598" fill="#4ade80">Tests Passed</text>

  <!-- ==================== STAGE 6: HITL GATE ==================== -->
  <g transform="translate(305, 620)" filter="url(#dropShadow)">
    <rect width="340" height="60" rx="10" fill="url(#amberGrad)" stroke="#fbbf24" stroke-width="1.5" />
    <text class="node-title" x="170" y="25" text-anchor="middle">Human-in-the-Loop Gate</text>
    <text class="node-desc" x="170" y="44" text-anchor="middle">(LangGraph Interrupt Point)</text>
  </g>

  <!-- Branching: HITL -> Changes vs Approve -->
  <path class="line" stroke="#fbbf24" d="M 370 680 L 370 715 L 235 715 L 235 745" marker-end="url(#arrowAmber)" />
  <text class="label" x="160" y="732" fill="#fbbf24">User Requests Changes</text>

  <path class="line" stroke="#4ade80" d="M 580 680 L 580 715 L 715 715 L 715 745" marker-end="url(#arrowGreen)" />
  <text class="label" x="655" y="732" fill="#4ade80">User Approves</text>

  <!-- ==================== HITL: REQUEST CHANGES ACTION ==================== -->
  <g transform="translate(75, 750)" filter="url(#dropShadow)">
    <rect width="320" height="64" rx="10" fill="url(#nodeGrad)" stroke="#fbbf24" stroke-width="1.5" />
    <text class="node-title" x="160" y="25" text-anchor="middle">Re-route Feedback to Agents</text>
    <text class="node-desc" x="160" y="45" text-anchor="middle">(Append Human Prompts &amp; Resume)</text>
  </g>

  <!-- ==================== HITL: APPROVE ACTION ==================== -->
  <g transform="translate(555, 750)" filter="url(#dropShadow)">
    <rect width="320" height="64" rx="10" fill="url(#greenGrad)" stroke="#4ade80" stroke-width="1.5" />
    <text class="node-title" x="160" y="25" text-anchor="middle">Final Merge / PR Automation</text>
    <text class="node-desc" x="160" y="45" text-anchor="middle">(GitHub API Branch &amp; Pull Request)</text>
  </g>

  <!-- Connectors into Redis State Layer -->
  <path class="line" stroke="#c084fc" stroke-dasharray="4,4" d="M 235 814 L 235 870" marker-end="url(#arrowPurple)" />
  <path class="line" stroke="#c084fc" stroke-dasharray="4,4" d="M 715 814 L 715 870" marker-end="url(#arrowPurple)" />

  <!-- ==================== REDIS STATE LAYER ==================== -->
  <g transform="translate(135, 875)" filter="url(#dropShadow)">
    <rect width="680" height="65" rx="12" fill="url(#purpleGrad)" stroke="#c084fc" stroke-width="1.5" />
    <text class="node-title" x="340" y="27" text-anchor="middle">Redis State &amp; Checkpointer Layer</text>
    <text class="node-desc" x="340" y="47" text-anchor="middle">(Persists Agent Memory, Checkpoints, Thread IDs, &amp; Audit Logs)</text>
  </g>

  <!-- Dynamic Loopback Line from Re-Route Node back to Optimizer -->
  <path class="line" stroke="#fbbf24" stroke-dasharray="5,4" d="M 120 750 L 120 700 L 25 700 L 25 280 L 715 280 L 715 295" marker-end="url(#arrowAmber)" />
</svg>
