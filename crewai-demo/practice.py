from crewai import Agent

researcher = Agent(
    role = "Senior Blog Content Researcher",
    goal = "research the latest AI trends",
    backstory = "You are a tech journalist known for finding obscure, interesting angles.",
    verbose = True
)

writer = Agent(
    role = "Tech Storyteller",
    goal = "Write engaging narratives about AI",
    backstory = "You write like Malcolm Gladwell meets a Python developer.",
    verbose = True,
    allow_delegation = False
)
