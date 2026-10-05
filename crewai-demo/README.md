# CrewAI Project Architecture Showcase

This directory contains standalone, runnable examples demonstrating each level of the Agentic AI maturation roadmap as well as official declarative YAML configurations.

---

## 🗺️ Project Structure

```
crewai-demo/
├── config/
│   ├── agents.yaml                     # Declarative agent personas & prompt definitions
│   └── tasks.yaml                      # Declarative task objectives & expected outputs
├── yaml_crew_example.py                # Production pattern with @CrewBase & YAML injection
├── level_1_fundamentals.py             # Level 1: Agent, Task, Crew, Sequential & Hierarchical Process
├── level_2_tools_and_io.py             # Level 2: Tools, Custom Tools, Inputs, Structured Outputs
├── level_3_memory_knowledge_rag.py     # Level 3: Unified Memory, Knowledge, RAG & Context
├── level_3_advanced_memory_storage.py  # Advanced Memory: LanceDB, custom StorageBackend, composite scoring
├── level_4_flows_and_routing.py        # Level 4: Flows, Routing, Human-in-the-Loop, State
└── level_5_enterprise_production.py    # Level 5: Multi-agent systems, Guardrails, Evaluation, Observability
```

---

## ⚡ YAML Configuration Pattern (`@CrewBase`)

CrewAI's recommended enterprise and CLI pattern decouples prompt engineering from Python code using declarative YAML files:

* **[config/agents.yaml](file:///Volumes/Lexar/GitHub/agentic-ai-101/crewai-demo/config/agents.yaml)**: Defines `role`, `goal`, and `backstory` cleanly without cluttering Python code.
* **[config/tasks.yaml](file:///Volumes/Lexar/GitHub/agentic-ai-101/crewai-demo/config/tasks.yaml)**: Defines `description`, `expected_output`, and default agent mappings.
* **[yaml_crew_example.py](file:///Volumes/Lexar/GitHub/agentic-ai-101/crewai-demo/yaml_crew_example.py)**: Uses `@CrewBase`, `@agent`, `@task`, and `@crew` to bind the YAML files into an executable pipeline.

**Run the YAML Crew:**
```bash
uv run yaml_crew_example.py
```

---

## 📚 Maturation Roadmap Examples

* **Level 1**: `uv run level_1_fundamentals.py`
* **Level 2**: `uv run level_2_tools_and_io.py`
* **Level 3**: `uv run level_3_memory_knowledge_rag.py`
* **Level 3 (Advanced Memory)**: `uv run level_3_advanced_memory_storage.py`
* **Level 4**: `uv run level_4_flows_and_routing.py`
* **Level 5**: `uv run level_5_enterprise_production.py`
