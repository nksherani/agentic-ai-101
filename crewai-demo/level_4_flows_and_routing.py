"""
LEVEL 4: Event-Driven Flows & Orchestration
├── Flows: Structured, stateful multi-step pipelines (CrewAI Flows)
├── Conditional routing: @router decorator branching execution dynamically
├── Human-in-the-loop: User input hooks / review gates before critical steps
└── State management: Typed state management with Pydantic across nodes
"""

from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

from crewai import Agent, Crew, Process, Task
from crewai.flow.flow import Flow, start, listen, router

load_dotenv(Path(__file__).parent.parent / ".env")


# ==========================================
# 1. Typed State Management
# ==========================================
class CodeReviewState(BaseModel):
    code_snippet: str = ""
    severity_level: str = "low"  # "low", "medium", "critical"
    analysis_notes: str = ""
    human_approved: bool = False
    remediation_plan: Optional[str] = None


# ==========================================
# 2. CrewAI Flow with Routing, State & Human-In-The-Loop
# ==========================================
class AutonomousSecurityFlow(Flow[CodeReviewState]):
    """
    Demonstrates:
    - @start: entry point initializing state
    - @router: conditional routing based on state
    - human-in-the-loop review for critical paths
    - crew kickoff inside flow nodes
    """

    @start()
    def ingest_code_submission(self):
        print("\n[FLOW STEP 1] Ingesting code & initializing state...")
        # In a real app this might come from a webhook or event queue
        self.state.code_snippet = (
            "import os\n"
            "def execute_cmd(user_input):\n"
            "    os.system('rm -rf ' + user_input)\n"
        )
        print(f"Code under review:\n{self.state.code_snippet}")
        return self.state.code_snippet

    @listen(ingest_code_submission)
    def evaluate_risk_level(self):
        print("\n[FLOW STEP 2] Evaluating Risk Level with Specialized Agent...")
        triage_agent = Agent(
            role="Static Analysis Triager",
            goal="Identify if code contains command injection or critical flaws",
            backstory="You quickly tag vulnerabilities into 'critical' or 'benign'.",
            verbose=False,
        )

        triage_task = Task(
            description=f"Analyze this snippet:\n{self.state.code_snippet}\nIs it 'critical' or 'low' risk? Output only one word: 'critical' or 'low'.",
            expected_output="Either 'critical' or 'low'.",
            agent=triage_agent,
        )

        crew = Crew(agents=[triage_agent], tasks=[triage_task], verbose=False)
        output = str(crew.kickoff()).strip().lower()

        if "critical" in output:
            self.state.severity_level = "critical"
        else:
            self.state.severity_level = "low"

        self.state.analysis_notes = f"Triage assessment output: {output}"
        print(f"Risk Severity Determined: [{self.state.severity_level.upper()}]")
        return self.state.severity_level

    # ==========================================
    # 3. Conditional Routing
    # ==========================================
    @router(evaluate_risk_level)
    def route_by_severity(self):
        print(f"\n[FLOW ROUTER] Routing execution based on severity: {self.state.severity_level}")
        if self.state.severity_level == "critical":
            return "handle_critical_vulnerability"
        return "handle_standard_review"

    @listen("handle_standard_review")
    def automated_merge(self):
        print("\n[BRANCH: LOW RISK] Automated review passed. Auto-merging code.")
        self.state.remediation_plan = "No remediation needed; automated merge approved."
        return self.state

    # ==========================================
    # 4. Human-in-the-Loop Gate for Critical Paths
    # ==========================================
    @listen("handle_critical_vulnerability")
    def human_review_gate(self):
        print("\n[BRANCH: CRITICAL RISK] ⚠️ High risk detected! Triggering Human-in-the-loop review...")
        print(f"Snippet:\n{self.state.code_snippet}")
        print("Note: In interactive mode, this prompts the engineer. (Simulating automated approval gate for demo)")

        # In production CLI:
        # response = input("Approve security remediation? (yes/no): ")
        # user_approved = response.strip().lower() == "yes"
        user_approved = True  # Simulated human approval

        self.state.human_approved = user_approved
        print(f"Human Gate Decision: {'APPROVED' if user_approved else 'REJECTED'}")

        if self.state.human_approved:
            return self.generate_remediation()
        else:
            self.state.remediation_plan = "Rejected by human reviewer. Pipeline halted."
            return self.state

    def generate_remediation(self):
        print("\n[FLOW REMEDIATION] Assembling Remediation Crew to fix code...")
        remediation_agent = Agent(
            role="AppSec Remediation Engineer",
            goal="Rewrite code securely replacing unsafe os.system calls with subprocess with sanitization",
            backstory="You rewrite vulnerable code patterns into production-grade secure equivalents.",
            verbose=False,
        )

        fix_task = Task(
            description=f"Rewrite this unsafe code securely:\n{self.state.code_snippet}",
            expected_output="Safe, refactored Python code snippet.",
            agent=remediation_agent,
        )

        crew = Crew(agents=[remediation_agent], tasks=[fix_task], verbose=False)
        result = crew.kickoff()
        self.state.remediation_plan = str(result)
        return self.state


def run_level_4():
    print("\n" + "=" * 60)
    print("LEVEL 4: FLOWS, CONDITIONAL ROUTING, HUMAN-IN-THE-LOOP & STATE")
    print("=" * 60)

    flow = AutonomousSecurityFlow()
    final_state = flow.kickoff()

    print("\n--- LEVEL 4 Final State ---")
    print(f"Severity Level: {flow.state.severity_level}")
    print(f"Human Approved: {flow.state.human_approved}")
    print(f"Remediation Plan:\n{flow.state.remediation_plan}")
    return final_state


if __name__ == "__main__":
    run_level_4()
