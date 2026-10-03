from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool

# 1. Tool Definition
search_tool = SerperDevTool()

# 2. Agent Definitions
researcher = Agent(
    role="Senior Blog Content Researcher",
    goal="Research the latest AI trends",
    backstory="You are a tech journalist known for finding obscure, interesting angles.",
    verbose=True,
    allow_delegation=True,
    tools=[search_tool]
)

writer = Agent(
    role="Tech Storyteller",
    goal="Write engaging narratives about AI",
    backstory="You write like Malcolm Gladwell meets a Python developer.",
    verbose=True,
    allow_delegation=False
)

# 3. Task Definitions
task1 = Task(
    description="Research the most surprising AI breakthrough of the last 6 months.",
    expected_output="A 5-bullet list of surprising facts.",
    agent=researcher
)

task2 = Task(
    description="Write a compelling blog introduction based on the researcher's findings.",
    expected_output="A 300-word blog intro.",
    agent=writer
)

# 4. Crew Definition
crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
    process=Process.sequential
)

# 5. Execution
if __name__ == "__main__":
    result = crew.kickoff()
    print(result)
