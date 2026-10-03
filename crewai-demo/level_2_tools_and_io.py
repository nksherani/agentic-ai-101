"""
LEVEL 2: Tools & Input/Output Engineering
├── Tools: Pre-built tools (SerperDevTool)
├── Custom tools: @tool decorator and BaseTool class subclassing
├── Dynamic inputs: Passing runtime parameters ({topic}, {target_audience}) into tasks
└── Structured outputs: Pydantic schemas enforcing output format
"""

import json
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.tools import tool, BaseTool
from crewai_tools import SerperDevTool

load_dotenv(Path(__file__).parent.parent / ".env")


# ==========================================
# 1. Structured Output Schema (Pydantic)
# ==========================================
class CompetitorMetric(BaseModel):
    name: str = Field(description="Name of the competitor")
    core_strength: str = Field(description="Main advantage/feature")
    threat_level: str = Field(description="Low, Medium, or High")


class MarketAnalysisReport(BaseModel):
    industry: str = Field(description="The sector analyzed")
    market_overview: str = Field(description="2-3 sentence overview of the industry state")
    top_competitors: List[CompetitorMetric] = Field(description="List of top analyzed competitors")
    key_recommendation: str = Field(description="Single top tactical recommendation")


# ==========================================
# 2. Custom Tools
# Approach A: Function-based using @tool decorator
# ==========================================
@tool("Market Growth Calculator")
def calculate_growth_rate(initial_value: float, final_value: float, years: int) -> str:
    """Calculates Compound Annual Growth Rate (CAGR) given initial value, final value, and number of years."""
    if initial_value <= 0 or years <= 0:
        return "Invalid parameters for CAGR calculation."
    cagr = ((final_value / initial_value) ** (1 / years) - 1) * 100
    return f"Calculated CAGR over {years} years: {cagr:.2f}% (Initial: ${initial_value}M -> Final: ${final_value}M)"


# Approach B: Class-based extending BaseTool (for tools requiring state/configs)
class ProfitabilityEstimatorTool(BaseTool):
    name: str = "Profitability Estimator"
    description: str = "Estimates profit margin based on projected revenue and operational costs."

    def _run(self, revenue: float, costs: float) -> str:
        margin = ((revenue - costs) / revenue) * 100 if revenue else 0
        return f"Projected Net Margin: {margin:.1f}% with net profit ${revenue - costs:.2f}M"


def run_level_2():
    print("\n" + "=" * 60)
    print("LEVEL 2: TOOLS, CUSTOM TOOLS, DYNAMIC INPUTS & STRUCTURED OUTPUTS")
    print("=" * 60)

    # 3. Ready-to-use Tools
    search_tool = SerperDevTool()
    calculator_tool = calculate_growth_rate
    profit_tool = ProfitabilityEstimatorTool()

    # 4. Agent equipped with diverse tools
    analyst = Agent(
        role="Senior Market Intelligence Specialist",
        goal="Analyze market data for {industry} catering to {target_audience}",
        backstory=(
            "You are a quant-oriented market analyst capable of searching live web data, "
            "calculating financial metrics, and producing strict structured intelligence."
        ),
        tools=[search_tool, calculator_tool, profit_tool],
        verbose=True,
    )

    # 5. Task with Dynamic Inputs ({industry}, {target_audience}) and output_pydantic
    analysis_task = Task(
        description=(
            "Analyze the current market landscape for '{industry}'. "
            "Tailor the depth and perspective for '{target_audience}'. "
            "Use search if needed to identify key active players. "
            "Compute financial metrics using available calculation tools when relevant. "
            "Ensure the final output strictly adheres to the requested schema."
        ),
        expected_output="A structured MarketAnalysisReport Pydantic object.",
        output_pydantic=MarketAnalysisReport,
        agent=analyst,
    )

    crew = Crew(
        agents=[analyst],
        tasks=[analysis_task],
        process=Process.sequential,
        verbose=True,
    )

    # 6. Dynamic Inputs passed at runtime into kickoff(inputs={...})
    runtime_inputs = {
        "industry": "Open-Source AI Agent Frameworks",
        "target_audience": "Series-A Venture Capital Investors",
    }

    print(f"\n[INFO] Kickoff with inputs: {runtime_inputs}\n")
    result = crew.kickoff(inputs=runtime_inputs)

    print("\n--- LEVEL 2 Result (Pydantic Structured Output) ---")
    if hasattr(result, "pydantic") and result.pydantic:
        report: MarketAnalysisReport = result.pydantic
        print("Raw Dict Representation:")
        print(json.dumps(report.model_dump(), indent=2))
    else:
        print(result)

    return result


if __name__ == "__main__":
    run_level_2()
