"""
CREWAI WITH YAML CONFIGURATION (PRODUCTION PATTERN)
===================================================
In real-world projects and the official CrewAI CLI (`crewai create crew`),
agents and tasks are defined in declarative YAML files:
- `config/agents.yaml`: Personas, roles, goals, backstories
- `config/tasks.yaml`: Task descriptions, expectations, and agent assignments

The `@CrewBase` decorator connects these YAML files to Python using `@agent`,
`@task`, and `@crew` decorators.
"""

from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")


@CrewBase
class ResearchBriefingCrew:
    """Enterprise Research & Executive Briefing Crew configured via YAML."""

    # Relative paths to the YAML config files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ==========================================
    # Agents (Keys match names in agents.yaml)
    # ==========================================
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            # You can inject tools or specific LLMs here alongside YAML config:
            # tools=[...],
            # llm="gpt-4o",
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config["writer"],
        )

    # ==========================================
    # Tasks (Keys match names in tasks.yaml)
    # ==========================================
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config["reporting_task"],
            context=[self.research_task()],  # Explicit context dependency
        )

    # ==========================================
    # Crew Definition
    # ==========================================
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically collected by @agent decorators
            tasks=self.tasks,    # Automatically collected by @task decorators
            process=Process.sequential,
            verbose=True,
        )


def run_yaml_crew():
    print("\n" + "=" * 65)
    print("RUNNING CREWAI WITH DECLARATIVE YAML CONFIGURATIONS")
    print("=" * 65)

    # Dynamic inputs injected into YAML placeholders ({topic}, {target_audience})
    inputs = {
        "topic": "Autonomous Multi-Agent AI Frameworks in 2026",
        "target_audience": "Chief Information & Security Officers (CISOs)",
    }

    print(f"\n[INFO] Starting kickoff with runtime inputs: {inputs}\n")
    
    # Instantiate and kickoff
    research_crew = ResearchBriefingCrew()
    result = research_crew.crew().kickoff(inputs=inputs)

    print("\n--- FINAL YAML CREW OUTPUT ---")
    print(result)
    return result


if __name__ == "__main__":
    run_yaml_crew()
