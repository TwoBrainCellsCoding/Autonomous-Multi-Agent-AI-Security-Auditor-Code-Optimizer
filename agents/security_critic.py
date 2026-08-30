from typing import Dict, Any, List

class SecurityCritic:
    '''Evaluates security audit reports.
    If CRITICAL or HIGH vulnerabilities exist, it triggers a re-audit loop'''

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    def evaluate_security(self, state: Dict[str, Any]) -> Dict[str, Any]:
        audit_results = state.get("security_audit_results", [])
        retry_count = state.get("security_retry_count", 0)

        critical_or_high_found = False
        findings_summary = []

        for item in audit_results:
            report = item.get("report", {})
            vulnerabilities = report.get("vulnerabilities", [])

            for vuln in vulnerabilities:
                severity = vuln.get("severity", "").upper()
                if severity in ["CRITICAL", "HIGH"]:
                    critical_or_high_found = True
                    findings_summary.append(
                        f"[{severity}] {vuln.get('vulnerability_type')}: {vuln.get('exploit_vector')}"
                    )

        # Case A: Security Audit Passed
        if not critical_or_high_found:
            return {
                **state,
                "security_critic_decision": "passed",
                "security_critic_message": "No CRITICAL or HIGH security flaws detected.",
                "security_error_feedback": None
            }

        # Case B: Max retries exceeded
        if retry_count >= self.max_retries:
            return {
                **state,
                "security_critic_decision": "max_retries_exceeded",
                "security_critic_message": f"Security flaws persist after {self.max_retries} re-audits.",
                "security_error_feedback": "\n".join(findings_summary)
            }

        # Case C: Security Flaws Detected -> Loop back to Security Agent
        return {
            **state,
            "security_retry_count": retry_count + 1,
            "security_critic_decision": "loop_security",
            "security_critic_message": f"Security vulnerabilities detected on attempt {retry_count + 1}. Routing back to Security Auditor.",
            "security_error_feedback": "\n".join(findings_summary)
        }


def security_critic_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node entrypoint for Security Critic."""
    critic = SecurityCritic(max_retries=3)
    return critic.evaluate_security(state)