"""
LEVEL 5: Enterprise Multi-Agent Systems & Production Operations
├── Multi-agent architecture: Tiered specialist agents with clear boundaries
├── Guardrails: Pre/Post task validation, content moderation & safety filters
├── Evaluation: Automated scoring against objective quality rubrics
├── Observability: Telemetry, token usage tracking, execution timing, step callbacks
└── Production deployment: Containerization, health endpoints, environment gating
"""

import time
import json
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from crewai import Agent, Crew, Process, Task

load_dotenv(Path(__file__).parent.parent / ".env")


# ==========================================
# 1. Guardrails & Output Validation
# ==========================================
class ComplianceEvaluation(BaseModel):
    passes_safety: bool = Field(description="True if content complies with enterprise policies")
    quality_score: int = Field(description="Score from 1 to 10 on accuracy and tone")
    rubric_feedback: str = Field(description="Justification for the evaluation score")


def enterprise_safety_guardrail(output: str) -> bool:
    """
    Simulates deterministic enterprise policy check (PII, secret leak, profanity).
    Returns True if passed, raises or returns False if violated.
    """
    forbidden_terms = ["sk-proj-", "password", "DROP TABLE"]
    for term in forbidden_terms:
        if term in output:
            print(f"[GUARDRAIL ALERT] Forbidden pattern '{term}' detected!")
            return False
    return True


# ==========================================
# 2. Observability & Telemetry Callbacks
# ==========================================
class ProductionTelemetry:
    def __init__(self):
        self.step_logs = []
        self.start_time = None

    def start_run(self):
        self.start_time = time.time()
        print("\n[TELEMETRY] Run started. Monitoring traces & latency...")

    def step_callback(self, step_output):
        """CrewAI step callback invoked after every agent reasoning step."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        log_entry = {
            "timestamp": time.strftime("%H:%M:%S"),
            "elapsed_seconds": round(elapsed, 2),
            "step_preview": str(step_output)[:120] + "...",
        }
        self.step_logs.append(log_entry)
        print(f"[TRACE +{log_entry['elapsed_seconds']}s] Step logged: {log_entry['step_preview']}")

    def task_callback(self, task_output):
        """CrewAI task callback invoked when a full task completes."""
        print(f"[TELEMETRY] Task Completed. Output length: {len(str(task_output))} chars.")


telemetry = ProductionTelemetry()


# ==========================================
# 3. Multi-Agent Architecture
# ==========================================
def run_level_5():
    print("\n" + "=" * 60)
    print("LEVEL 5: MULTI-AGENT ARCHITECTURE, GUARDRAILS, EVALUATION & OBSERVABILITY")
    print("=" * 60)

    telemetry.start_run()

    # Agent A: Specialist Producer
    architect = Agent(
        role="Cloud Infrastructure Architect",
        goal="Design a resilient architecture for deploying autonomous agents in production",
        backstory="Expert in Kubernetes, API gateways, secret vaults, and high availability.",
        verbose=True,
        step_callback=telemetry.step_callback,
    )

    # Agent B: Specialist Evaluator & Guardrail Inspector
    evaluator = Agent(
        role="Enterprise Quality & Safety Evaluator",
        goal="Evaluate architectures against SLA and security benchmarks",
        backstory="Strict enterprise auditor reviewing technical proposals against quality rubrics.",
        verbose=True,
    )

    # Task 1: Architecture Blueprint
    blueprint_task = Task(
        description=(
            "Create a concise 3-pillar production architecture plan for AI agent systems: "
            "1. Ingestion & API Gateway, 2. Worker Execution Sandbox, 3. Vault & Observability."
        ),
        expected_output="3-pillar architecture proposal.",
        agent=architect,
        callback=telemetry.task_callback,
    )

    # Task 2: Automated Evaluation against Quality Rubric
    evaluation_task = Task(
        description=(
            "Review the architecture proposal from the context. "
            "Evaluate whether it meets safety standards, assign an objective quality score (1-10), "
            "and provide rubric feedback in the required structured schema."
        ),
        expected_output="A structured ComplianceEvaluation object.",
        output_pydantic=ComplianceEvaluation,
        agent=evaluator,
        context=[blueprint_task],
    )

    # Crew Assembly
    enterprise_crew = Crew(
        agents=[architect, evaluator],
        tasks=[blueprint_task, evaluation_task],
        process=Process.sequential,
        verbose=True,
    )

    result = enterprise_crew.kickoff()

    # Post-Execution Guardrail Check
    raw_str = str(result)
    is_safe = enterprise_safety_guardrail(raw_str)
    print(f"\n[POST-EXECUTION GUARDRAIL] Content Safety Check: {'PASSED' if is_safe else 'FAILED'}")

    # Output Evaluation Schema
    print("\n--- LEVEL 5 Evaluation & Quality Score ---")
    if hasattr(result, "pydantic") and result.pydantic:
        eval_data: ComplianceEvaluation = result.pydantic
        print(json.dumps(eval_data.model_dump(), indent=2))
    else:
        print(result)

    # Observability Summary
    print("\n--- Observability Telemetry Summary ---")
    print(f"Total steps tracked: {len(telemetry.step_logs)}")
    print(f"Total run time: {round(time.time() - telemetry.start_time, 2)} seconds")
    return result


if __name__ == "__main__":
    run_level_5()
