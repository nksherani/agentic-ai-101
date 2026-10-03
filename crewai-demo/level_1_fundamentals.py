"""
LEVEL 1: Core Fundamentals
├── Agent: Persona, role, goal, backstory
├── Task: Description, expected output, agent assignment
├── Crew: Assembling agents and tasks
└── Process: Sequential vs Hierarchical execution
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task

# Load environment variables from parent workspace root or local .env
load_dotenv(Path(__file__).parent.parent / ".env")


def run_sequential_crew():
    print("\n" + "=" * 60)
    print("LEVEL 1: SEQUENTIAL PROCESS CREW")
    print("=" * 60)

    # 1. Agents
    researcher = Agent(
        role="Tech Trend Scout",
        goal="Identify 3 key developments in Agentic AI in 2026",
        backstory="You are a veteran technology analyst specializing in AI agent frameworks.",
        verbose=True,
    )

    writer = Agent(
        role="Executive Briefing Specialist",
        goal="Synthesize research findings into an actionable executive summary",
        backstory="You turn complex engineering and AI research into clear executive briefings.",
        verbose=True,
    )

    # 2. Tasks
    research_task = Task(
        description="List top 3 developments in Agentic AI frameworks with a 1-line reason each.",
        expected_output="A bulleted list of 3 items with brief descriptions.",
        agent=researcher,
    )

    writing_task = Task(
        description="Review the research findings and write a concise 1-paragraph executive summary.",
        expected_output="A single paragraph executive summary for CTOs.",
        agent=writer,
    )

    # 3. Crew with Sequential Process
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,  # Outputs flow from task 1 -> task 2
        verbose=True,
    )

    result = crew.kickoff()
    print("\n--- LEVEL 1 (Sequential) Result ---")
    print(result)
    return result


def run_hierarchical_crew():
    print("\n" + "=" * 60)
    print("LEVEL 1: HIERARCHICAL PROCESS CREW (Manager delegates to workers)")
    print("=" * 60)

    analyst = Agent(
        role="Risk Analyst",
        goal="Identify potential security risks of autonomous AI agents",
        backstory="You specialize in AI red-teaming and safety compliance.",
        verbose=True,
    )

    strategist = Agent(
        role="Mitigation Strategist",
        goal="Develop safeguards for identified risks",
        backstory="You design governance protocols and sandboxes for enterprise AI deployments.",
        verbose=True,
    )

    risk_task = Task(
        description="Identify the top 2 enterprise risks of agentic tool execution.",
        expected_output="Two specific risks explained briefly.",
    )

    mitigation_task = Task(
        description="Propose mitigation policies for the identified risks.",
        expected_output="Two mitigation strategies corresponding to the risks.",
    )

    # Hierarchical process requires a manager_llm (or default manager agent)
    crew = Crew(
        agents=[analyst, strategist],
        tasks=[risk_task, mitigation_task],
        process=Process.hierarchical,  # Manager delegates and evaluates completion
        manager_llm="gpt-4o-mini",
        verbose=True,
    )

    result = crew.kickoff()
    print("\n--- LEVEL 1 (Hierarchical) Result ---")
    print(result)
    return result


if __name__ == "__main__":
    # run_sequential_crew()
    # Uncomment to test hierarchical:
    run_hierarchical_crew()
