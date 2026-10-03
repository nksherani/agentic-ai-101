"""
LEVEL 3: Memory, Knowledge & Context Management
├── Memory: Short-Term, Long-Term, and Entity Memory configurations
├── Knowledge: Native StringKnowledgeSource / Text sources
├── RAG: Integrating retriever tools (e.g., custom embeddings / retrieval over docs)
└── Context management: task.context passing task dependencies explicitly
"""

from pathlib import Path
from dotenv import load_dotenv

from crewai import Agent, Crew, Process, Task
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.tools import tool

load_dotenv(Path(__file__).parent.parent / ".env")


# ==========================================
# 1. Native Knowledge Sources
# Supplies static or loaded corporate/domain context to the agent
# ==========================================
internal_handbook = """
ACME AI Robotics Policy 2026:
- Safety Tier 1: Any robotic agent operating above 45km/h must engage lidar fail-safe within 10ms.
- Safety Tier 2: Agent autonomous decisions involving human proximity under 1 meter require dual-sensor redundancy.
- Battery Standard: All field units use graphene-lithium packs requiring recharge at 18% reserve.
- Proprietary protocol name: 'Aegis-Sync'.
"""

knowledge_source = StringKnowledgeSource(
    content=internal_handbook,
    chunk_size=400,
    chunk_overlap=50,
)


# ==========================================
# 2. RAG Tool (Simulated Retriever Tool)
# For larger document corpuses or vector database lookups
# ==========================================
@tool("Vector Database RAG Retriever")
def incident_archive_rag_tool(query: str) -> str:
    """Searches past incident postmortems in the vector database given a query."""
    simulated_vector_db = {
        "failsafe": "Incident #402: Lidar sensor failed to trip within 10ms due to bus congestion; solved by Aegis-Sync v2.1.",
        "battery": "Incident #119: Cell degradation occurred when draining below 15%; policy updated to minimum 18% reserve.",
        "proximity": "Incident #304: Near miss with human operator resolved by adding dual ultrasonic backup.",
    }
    for key, doc in simulated_vector_db.items():
        if key in query.lower():
            return f"[Retrieved Chunk]: {doc}"
    return "[Retrieved Chunk]: Standard operating conditions maintained; no abnormal incident flags found."


def run_level_3():
    print("\n" + "=" * 60)
    print("LEVEL 3: MEMORY, KNOWLEDGE, RAG & CONTEXT MANAGEMENT")
    print("=" * 60)

    # 3. Agents with Knowledge and RAG Tool
    auditor = Agent(
        role="Corporate Safety Compliance Auditor",
        goal="Audit field operations against company policy knowledge and past incidents",
        backstory=(
            "You are an auditor with deep knowledge of ACME policies. You cross-reference "
            "internal knowledge guidelines with historical postmortems retrieved from the RAG store."
        ),
        tools=[incident_archive_rag_tool],
        knowledge_sources=[knowledge_source],
        verbose=True,
    )

    summarizer = Agent(
        role="Operations Executive",
        goal="Produce clear recommendations synthesizing findings",
        backstory="You convert detailed technical audit contexts into clean compliance action plans.",
        verbose=True,
    )

    # 4. Context Management: Task 2 explicitly specifies `context=[audit_task]`
    # Task 1: Audit
    audit_task = Task(
        description=(
            "Look up the ACME safety policy on robotic speed limits and failsafe requirements "
            "from your internal knowledge. Then use the Vector Database RAG Retriever to check past "
            "incidents related to 'failsafe'. List the policy rule and the related past incident."
        ),
        expected_output="Detailed findings comparing policy rule vs historical incident report.",
        agent=auditor,
    )

    # Task 2: Action Plan consuming audit_task context directly
    action_plan_task = Task(
        description=(
            "Based strictly on the audit findings provided in the context, create a 3-step "
            "verification checklist for field technicians."
        ),
        expected_output="A 3-step checklist for field operations.",
        agent=summarizer,
        context=[audit_task],  # Context Management: passes audit_task output directly into this task!
    )

    # 5. Crew with Memory Enabled
    # CrewAI integrates Short-Term (ChromaDB), Long-Term (SQLite), and Entity Memory
    crew = Crew(
        agents=[auditor, summarizer],
        tasks=[audit_task, action_plan_task],
        process=Process.sequential,
        memory=True,  # Enables CrewAI Memory System
        verbose=True,
    )

    result = crew.kickoff()

    print("\n--- LEVEL 3 Result ---")
    print(result)
    return result


if __name__ == "__main__":
    run_level_3()
