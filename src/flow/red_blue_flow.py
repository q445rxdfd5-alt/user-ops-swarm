"""
Red/Blue Evaluation Flow — Orchestrator

A red-blue evaluation pattern that stress-tests decision quality through adversarial
scenarios and multi-dimensional blue team review.

Pattern:
    red agent → standard flow (UserOpsFlow) → blue agents (parallel) → report

Steps:
    1. initialize       → set up run, read inputs
    2. red_attack        → generate adversarial scenario based on input type
    3. user_ops_flow     → run the full 9-step UserOpsFlow with red scenario context
    4. blue_parallel     → run 3 blue agents in parallel: quality_blue + risk_blue + strategy_blue
    5. generate_report   → output red_blue_report.json with scores and verdict

Red agents available:
    - competitor_red     → price war, review attacks, platform bans, traffic hijack, public opinion
    - crisis_red         → food safety, public opinion explosions, algorithm changes, policy risks
    - boundary_red       → zero budget, time critical, single-person scale

Blue agents (run in parallel):
    - quality_blue       → structural, logical, execution quality review
    - risk_blue          → secondary risk review, kill_switch validation
    - strategy_blue      → brand alignment, long-term moat assessment
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel

# Import from user_ops_flow for LLM and utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.flow.user_ops_flow import (
    UserOpsFlow,
    _load_env,
    _get_llm,
    SwarmState,
    ensure_run_directory,
    generate_run_id,
    create_agent_from_yaml,
    create_task_from_yaml,
    load_yaml,
    save_artifact,
)
from src.utils import (
    ensure_run_directory as ensure_dir,
    generate_run_id as gen_run_id,
)


# -----------------------------------------------------------------------
# Report Schema
# -----------------------------------------------------------------------
class BlueScores(BaseModel):
    quality_score: float
    risk_score: float
    strategy_score: float


class RedBlueReport(BaseModel):
    run_id: str
    timestamp: str
    red_scenario: dict[str, Any]
    blue_scores: BlueScores
    pass_fail: str
    findings: dict[str, Any]
    artifacts: list[str]


# -----------------------------------------------------------------------
# Agent Registry
# -----------------------------------------------------------------------
RED_AGENT_FILES = {
    "competitor_red": "competitor_red.yaml",
    "crisis_red": "crisis_red.yaml",
    "boundary_red": "boundary_red.yaml",
}

BLUE_AGENT_FILES = {
    "quality_blue": "quality_blue.yaml",
    "risk_blue": "risk_blue.yaml",
    "strategy_blue": "strategy_blue.yaml",
}

TASK_FILES = {
    "red_attack": "red_attack.yaml",
    "blue_review": "blue_review.yaml",
    "risk_blue_task": "risk_blue_task.yaml",
    "strategy_blue_task": "strategy_blue_task.yaml",
}


# -----------------------------------------------------------------------
# Agent Loaders
# -----------------------------------------------------------------------
def _load_red_agent(name: str):
    """Load a red team CrewAI Agent from YAML definition."""
    from crewai import Agent
    agents_dir = Path(__file__).parent.parent / "agents"
    path = agents_dir / RED_AGENT_FILES[name]
    yaml_def = load_yaml(path)
    llm = _get_llm()
    return create_agent_from_yaml(yaml_def, llm=llm)


def _load_blue_agent(name: str):
    """Load a blue team CrewAI Agent from YAML definition."""
    from crewai import Agent
    agents_dir = Path(__file__).parent.parent / "agents"
    path = agents_dir / BLUE_AGENT_FILES[name]
    yaml_def = load_yaml(path)
    llm = _get_llm()
    return create_agent_from_yaml(yaml_def, llm=llm)


def _load_task(name: str):
    """Load a task definition from YAML."""
    tasks_dir = Path(__file__).parent.parent / "tasks"
    path = tasks_dir / TASK_FILES[name]
    return load_yaml(path)


# -----------------------------------------------------------------------
# Red Agent Selector
# -----------------------------------------------------------------------
def _select_red_agent(input_content: str, context_content: str = "") -> str:
    """
    Select the appropriate red team agent based on input scenario.
    
    Heuristics:
    - crisis_red: food safety, safety incident, public opinion, algorithm change, policy, personnel departure
    - boundary_red: zero budget, 24 hour, single person, constraint, limited resource
    - competitor_red: default for competitive scenarios (price war, review attack, platform ban, etc.)
    """
    combined = (input_content + " " + context_content).lower()
    
    # Crisis keywords
    crisis_keywords = [
        "food safety", "safety incident", "public opinion", "algorithm change",
        "policy risk", "personnel departure", "emergency", "crisis",
        "contamination", "recall", "outbreak"
    ]
    for kw in crisis_keywords:
        if kw in combined:
            return "crisis_red"
    
    # Boundary/constraint keywords
    boundary_keywords = [
        "zero budget", "no budget", "24 hour", "single person", "limited resource",
        "constraint", "tight timeline", "fast launch", "minimum resource"
    ]
    for kw in boundary_keywords:
        if kw in combined:
            return "boundary_red"
    
    # Default to competitor_red
    return "competitor_red"


# -----------------------------------------------------------------------
# Output Parsing
# -----------------------------------------------------------------------
def _parse_json_from_text(text: str) -> Optional[dict[str, Any]]:
    """Extract JSON object from text, return None if not found."""
    if not text:
        return None
    # Try finding first { ... } block
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    # Fallback: try whole text
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None


def _extract_score(text: str, field: str, default: float = 5.0) -> float:
    """Extract a numeric score from agent output."""
    data = _parse_json_from_text(text)
    if data and field in data:
        val = data[field]
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            try:
                return float(val)
            except ValueError:
                pass
    return default


# -----------------------------------------------------------------------
# Blue Team Verdict Aggregator
# -----------------------------------------------------------------------
def _compute_blue_scores(
    quality_result: str,
    risk_result: str,
    strategy_result: str,
) -> BlueScores:
    """Compute normalized 0-100 scores from blue team outputs."""
    # Quality scores: structural + logic + execution (0-10 each → normalize to 0-100)
    q_data = _parse_json_from_text(quality_result)
    if q_data:
        structural = float(q_data.get("structural_score", 5))
        logic = float(q_data.get("logic_score", 5))
        execution = float(q_data.get("execution_score", 5))
        quality_score = ((structural + logic + execution) / 3) * 10
    else:
        quality_score = 50.0
    
    # Risk: invert verdict (cleared=100, needs_work=60, high_risk=20)
    r_data = _parse_json_from_text(risk_result)
    if r_data:
        verdict = r_data.get("blue_team_verdict", "needs_work")
        risk_map = {"cleared": 100.0, "needs_work": 60.0, "high_risk": 20.0}
        risk_score = risk_map.get(verdict, 50.0)
    else:
        risk_score = 50.0
    
    # Strategy: brand_alignment_score (0-10 → 0-100) + moat defensibility
    s_data = _parse_json_from_text(strategy_result)
    if s_data:
        brand_score = float(s_data.get("brand_alignment_score", 5)) * 10
        moat_score = float(s_data.get("competitive_moat", {}).get("defensibility_score", 5)) * 10
        strategy_score = (brand_score + moat_score) / 2
    else:
        strategy_score = 50.0
    
    return BlueScores(
        quality_score=round(min(100, max(0, quality_score)), 1),
        risk_score=round(min(100, max(0, risk_score)), 1),
        strategy_score=round(min(100, max(0, strategy_score)), 1),
    )


def _compute_pass_fail(scores: BlueScores, thresholds: dict[str, float] = None) -> str:
    """
    Determine pass/fail based on blue team scores.
    
    Default thresholds:
    - quality_score >= 60: structural/logical/execution quality sufficient
    - risk_score >= 50: risks are manageable
    - strategy_score >= 50: brand alignment acceptable
    
    PASS: all scores above threshold
    CONDITIONAL: any score below threshold but >= 30
    FAIL: any score below 30
    """
    if thresholds is None:
        thresholds = {"quality": 60, "risk": 50, "strategy": 50}
    
    q_pass = scores.quality_score >= thresholds["quality"]
    r_pass = scores.risk_score >= thresholds["risk"]
    s_pass = scores.strategy_score >= thresholds["strategy"]
    
    min_scores = [scores.quality_score, scores.risk_score, scores.strategy_score]
    
    if all([q_pass, r_pass, s_pass]):
        return "PASS"
    elif any(s < 30 for s in min_scores):
        return "FAIL"
    else:
        return "CONDITIONAL"


# -----------------------------------------------------------------------
# Main Flow Class
# -----------------------------------------------------------------------
class RedBlueFlow:
    """
    Orchestrates the red-blue evaluation workflow.
    
    Usage:
        flow = RedBlueFlow()
        result = flow.kickoff(
            inputs={
                "input_file": "examples/summer-new-product.md",
                "context_file": "context/user_ops_context.md",
                "memory_file": "memory/memory_log.md",
                "run_id": None,  # auto-generate
            }
        )
        print(f"Evaluation complete. Verdict: {flow.report.pass_fail}")
    """

    def __init__(self):
        self.state = SwarmState()
        self.report: Optional[RedBlueReport] = None
        self._red_scenario: Optional[dict[str, Any]] = None
        self._blue_results: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def kickoff(self, inputs: dict[str, Any]) -> RedBlueReport:
        """
        Execute the full red-blue evaluation flow.

        Args:
            inputs: dict with keys:
                - input_file (str): path to task input .md
                - context_file (str): path to context .md
                - memory_file (str): path to memory log .md
                - run_id (str | None): custom run ID or None for auto
                - red_agent (str | None): force specific red agent

        Returns:
            RedBlueReport with evaluation results.
        """
        try:
            self._initialize(inputs)
            self._run_red_attack()
            self._run_user_ops_flow()
            self._run_blue_agents_parallel()
            self._generate_report()
            return self.report
        except Exception as e:
            if self.report:
                self.report.pass_fail = "ERROR"
                self.report.findings["error"] = str(e)
            raise

    # ------------------------------------------------------------------
    # Step 1 — Initialize
    # ------------------------------------------------------------------
    def _initialize(self, inputs: dict[str, Any]) -> None:
        """Set up run directory and load input files."""
        self.state.run_id = inputs.get("run_id") or generate_run_id()
        self.state.run_dir = str(ensure_run_directory(self.state.run_id))
        self.state.status = "running"
        self.state.current_step = "initialize"

        # Read input file
        input_path = Path(inputs["input_file"])
        if input_path.exists():
            self.state.input_content = input_path.read_text(encoding="utf-8")
        else:
            self.state.input_content = ""

        # Read context file
        ctx_path = Path(inputs.get("context_file", "context/user_ops_context.md"))
        if ctx_path.exists():
            self.state.context_content = ctx_path.read_text(encoding="utf-8")
        else:
            self.state.context_content = ""

        # Read memory file
        mem_path = Path(inputs.get("memory_file", "memory/memory_log.md"))
        if mem_path.exists():
            self.state.memory_content = mem_path.read_text(encoding="utf-8")
        else:
            self.state.memory_content = ""

        print(f"[Step 1/5] initialize — run_id={self.state.run_id}")

    # ------------------------------------------------------------------
    # Step 2 — Red Attack
    # ------------------------------------------------------------------
    def _run_red_attack(self) -> None:
        """Generate adversarial attack scenario using appropriate red agent."""
        self.state.current_step = "red_attack"
        print(f"[Step 2/5] red_attack — selecting agent...")

        try:
            from crewai import Agent, Task, Crew
            from crewai.agents.agent_builder.base_agent import BaseAgent

            # Select red agent based on scenario
            forced_agent = getattr(self, "_forced_red_agent", None)
            if forced_agent and forced_agent in RED_AGENT_FILES:
                red_agent_name = forced_agent
            else:
                red_agent_name = _select_red_agent(
                    self.state.input_content,
                    self.state.context_content,
                )
            print(f"[Red Agent] Selected: {red_agent_name}")

            red_agent: BaseAgent = _load_red_agent(red_agent_name)

            # Build prompt with input context
            prompt = self._build_red_prompt(red_agent_name)

            task = Task(
                description=prompt,
                expected_output="JSON object with attack details matching the agent's output_json_format",
                agent=red_agent,
            )

            crew = Crew(agents=[red_agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            raw_output = str(result) if result else ""

            # Parse and store red scenario
            self._red_scenario = _parse_json_from_text(raw_output) or {"raw": raw_output}

            # Save artifact
            self._save_artifact("red_attack", "red_attack.json", json.dumps(self._red_scenario, indent=2))
            print(f"[Step 2/5] red_attack — ✓ (severity: {self._red_scenario.get('severity', 'unknown')})")

        except Exception as e:
            print(f"[WARNING] Red attack step failed: {e}")
            self._red_scenario = {"error": str(e)}
            self._save_artifact("red_attack", "red_attack.json", json.dumps(self._red_scenario, indent=2))

    def _build_red_prompt(self, agent_name: str) -> str:
        """Build the context prompt for red team agent."""
        lines = [
            "# Red Team Attack Simulation",
            f"Run ID: {self.state.run_id}",
            "---",
            "## INPUT SCENARIO",
            self.state.input_content or "(empty)",
            "---",
            "## CONTEXT",
            self.state.context_content or "(empty)",
            "---",
        ]
        
        # Add agent-specific instructions
        if agent_name == "competitor_red":
            lines += [
                "## YOUR TASK: COMPETITOR RED TEAM",
                "Attack this strategy from a competitor's perspective. Identify fatal weaknesses across:",
                "- Price war scenarios",
                "- Negative review campaigns",
                "- Platform ban threats",
                "- Traffic hijacking tactics",
                "- Public opinion warfare",
                "",
                "Ground attacks in realistic competitor capabilities. Focus on lethal vulnerabilities.",
            ]
        elif agent_name == "crisis_red":
            lines += [
                "## YOUR TASK: CRISIS RED TEAM",
                "Simulate worst-case scenarios to test decision-making resilience:",
                "- Food safety incidents",
                "- Public opinion explosions",
                "- Platform algorithm changes",
                "- Policy risks",
                "- Key personnel departures",
                "",
                "Focus on survivable crises, not extinction events. Map where the chain slows down.",
            ]
        elif agent_name == "boundary_red":
            lines += [
                "## YOUR TASK: BOUNDARY RED TEAM",
                "Find asymmetric opportunities under extreme constraints:",
                "- Zero budget acquisition",
                "- 24-hour launch requirements",
                "- Single-person operation challenges",
                "- Resource rock-bottom scenarios",
                "",
                "Ground solutions in verifiable tactics. Distinguish 'clever hack' from 'scalable strategy'.",
            ]
        
        lines += [
            "",
            "Output a structured JSON object as specified in the agent's output_json_format.",
        ]
        
        return "\n\n".join(lines)

    # ------------------------------------------------------------------
    # Step 3 — User Ops Flow (Standard Swarm)
    # ------------------------------------------------------------------
    def _run_user_ops_flow(self) -> None:
        """Run the standard UserOpsFlow with red scenario context injected."""
        self.state.current_step = "user_ops_flow"
        print(f"[Step 3/5] user_ops_flow — running standard swarm...")

        try:
            # Prepare inputs for UserOpsFlow
            # We need to inject the red scenario into the context
            enhanced_context = self.state.context_content
            
            if self._red_scenario and "error" not in self._red_scenario:
                # Inject red team findings as part of context
                red_injection = f"""
## RED TEAM ATTACK SCENARIO
The following adversarial scenario has been identified:

```json
{json.dumps(self._red_scenario, indent=2, ensure_ascii=False)}
```

Consider this adversarial context when developing strategy and execution plans.
"""
                enhanced_context = (enhanced_context or "") + red_injection

            # Run UserOpsFlow
            flow = UserOpsFlow()
            result_state = flow.kickoff(
                inputs={
                    "input_file": "",  # Will use state.input_content
                    "context_file": "",  # Will use enhanced context
                    "memory_file": "",  # Will use state.memory_content
                    "run_id": f"{self.state.run_id}-swarm",
                }
            )

            # Store outputs for blue team
            self.state.final_decision = result_state.final_decision or ""
            self.state.execution_plan = result_state.execution_plan or ""
            self.state.strategy_summary = result_state.strategy_summary or ""

            print(f"[Step 3/5] user_ops_flow — ✓ (status: {result_state.status})")

        except Exception as e:
            print(f"[WARNING] User ops flow failed: {e}")
            # Continue with evaluation even if swarm fails
            self.state.final_decision = self.state.input_content

    # ------------------------------------------------------------------
    # Step 4 — Blue Agents (Parallel)
    # ------------------------------------------------------------------
    def _run_blue_agents_parallel(self) -> None:
        """Run all three blue team agents in parallel using separate crews."""
        self.state.current_step = "blue_parallel"
        print(f"[Step 4/5] blue_parallel — running 3 agents in parallel...")

        try:
            from crewai import Agent, Task, Crew
            from crewai.agents.agent_builder.base_agent import BaseAgent

            # Load blue agents
            quality_agent: BaseAgent = _load_blue_agent("quality_blue")
            risk_agent: BaseAgent = _load_blue_agent("risk_blue")
            strategy_agent: BaseAgent = _load_blue_agent("strategy_blue")

            # Build context for blue team
            blue_context = self._build_blue_context()

            # Create tasks
            task_quality = Task(
                description=blue_context + "\n\n## QUALITY REVIEW TASK\nConduct a multi-dimension quality review: structural integrity, logical consistency, execution feasibility. Output JSON.",
                expected_output="JSON with structural_score, logic_score, execution_score, quality_issues, improvement_suggestions, overall_quality_verdict, summary",
                agent=quality_agent,
            )

            task_risk = Task(
                description=blue_context + "\n\n## RISK BLUE TEAM TASK\nPerform secondary risk review: verify mitigations, identify blind spots, assess kill_switch effectiveness. Output JSON.",
                expected_output="JSON with known_risk_adequate, known_risk_gaps, unknown_blind_spots, kill_switch_effective, additional_mitigations, blue_team_verdict, summary",
                agent=risk_agent,
            )

            task_strategy = Task(
                description=blue_context + "\n\n## STRATEGIC BLUE TEAM TASK\nAssess brand alignment, distinguish short-term from long-term, evaluate competitive moat durability. Output JSON.",
                expected_output="JSON with brand_alignment_score, brand_alignment_analysis, short_vs_long_term, competitive_moat, strategic_gaps, blue_team_verdict, summary",
                agent=strategy_agent,
            )

            # Run all three crews (sequential due to crewai 1.14.4 limitations)
            # In production, these could run in threads/processes
            crew_quality = Crew(agents=[quality_agent], tasks=[task_quality], verbose=True)
            crew_risk = Crew(agents=[risk_agent], tasks=[task_risk], verbose=True)
            crew_strategy = Crew(agents=[strategy_agent], tasks=[task_strategy], verbose=True)

            result_quality = crew_quality.kickoff()
            self._blue_results["quality"] = str(result_quality) if result_quality else ""

            result_risk = crew_risk.kickoff()
            self._blue_results["risk"] = str(result_risk) if result_risk else ""

            result_strategy = crew_strategy.kickoff()
            self._blue_results["strategy"] = str(result_strategy) if result_strategy else ""

            # Save blue team outputs
            self._save_artifact("blue_quality", "blue_quality_review.json", self._blue_results["quality"])
            self._save_artifact("blue_risk", "blue_risk_review.json", self._blue_results["risk"])
            self._save_artifact("blue_strategy", "blue_strategy_review.json", self._blue_results["strategy"])

            print(f"[Step 4/5] blue_parallel — ✓ (quality: {len(self._blue_results['quality'])} chars, risk: {len(self._blue_results['risk'])} chars, strategy: {len(self._blue_results['strategy'])} chars)")

        except Exception as e:
            print(f"[ERROR] Blue team parallel execution failed: {e}")
            self._blue_results = {
                "quality": '{"error": "execution failed"}',
                "risk": '{"error": "execution failed"}',
                "strategy": '{"error": "execution failed"}',
            }

    def _build_blue_context(self) -> str:
        """Build context prompt for blue team agents."""
        lines = [
            "# Blue Team Review — Decision Evaluation",
            f"Run ID: {self.state.run_id}",
            "---",
            "## FINAL DECISION OUTPUT",
            self.state.final_decision or "(no decision output)",
            "---",
            "## EXECUTION PLAN",
            self.state.execution_plan or "(no execution plan)",
            "---",
            "## STRATEGY SUMMARY",
            self.state.strategy_summary or "(no strategy summary)",
            "---",
            "## RED TEAM ATTACK SCENARIO (Context)",
            json.dumps(self._red_scenario, indent=2, ensure_ascii=False) if self._red_scenario else "(no red scenario)",
            "---",
            "## YOUR ROLE",
            "You are the Blue Team conducting post-decision review.",
            "Evaluate whether the decision adequately addresses the adversarial context",
            "and meets quality, risk, and strategic standards.",
            "",
        ]
        return "\n\n".join(lines)

    # ------------------------------------------------------------------
    # Step 5 — Generate Report
    # ------------------------------------------------------------------
    def _generate_report(self) -> None:
        """Generate the final red_blue_report.json."""
        self.state.current_step = "generate_report"
        print(f"[Step 5/5] generate_report — computing scores...")

        # Compute blue scores
        scores = _compute_blue_scores(
            self._blue_results.get("quality", ""),
            self._blue_results.get("risk", ""),
            self._blue_results.get("strategy", ""),
        )

        # Determine pass/fail
        verdict = _compute_pass_fail(scores)

        # Extract findings from blue outputs
        quality_data = _parse_json_from_text(self._blue_results.get("quality", ""))
        risk_data = _parse_json_from_text(self._blue_results.get("risk", ""))
        strategy_data = _parse_json_from_text(self._blue_results.get("strategy", ""))

        findings = {
            "quality_review": {
                "verdict": quality_data.get("overall_quality_verdict", "unknown") if quality_data else "unknown",
                "issues": quality_data.get("quality_issues", []) if quality_data else [],
                "summary": quality_data.get("summary", "") if quality_data else "",
            },
            "risk_review": {
                "verdict": risk_data.get("blue_team_verdict", "unknown") if risk_data else "unknown",
                "kill_switch_effective": risk_data.get("kill_switch_effective", False) if risk_data else False,
                "blind_spots": risk_data.get("unknown_blind_spots", []) if risk_data else [],
                "summary": risk_data.get("summary", "") if risk_data else "",
            },
            "strategy_review": {
                "verdict": strategy_data.get("blue_team_verdict", "unknown") if strategy_data else "unknown",
                "brand_alignment": strategy_data.get("brand_alignment_score", 0) if strategy_data else 0,
                "moat_durability": strategy_data.get("competitive_moat", {}).get("moat_durability", "unknown") if strategy_data else "unknown",
                "summary": strategy_data.get("summary", "") if strategy_data else "",
            },
        }

        # Build report
        self.report = RedBlueReport(
            run_id=self.state.run_id,
            timestamp=datetime.now().isoformat(),
            red_scenario=self._red_scenario or {},
            blue_scores=scores,
            pass_fail=verdict,
            findings=findings,
            artifacts=[
                f"{self.state.run_dir}/red_attack.json",
                f"{self.state.run_dir}/blue_quality_review.json",
                f"{self.state.run_dir}/blue_risk_review.json",
                f"{self.state.run_dir}/blue_strategy_review.json",
            ],
        )

        # Save report
        report_path = Path(self.state.run_dir) / "red_blue_report.json"
        report_path.write_text(
            json.dumps(self.report.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        self.state.status = "completed"
        print(f"[Step 5/5] generate_report — ✓")
        print(f"\n{'='*60}")
        print(f"RED-BLUE EVALUATION COMPLETE")
        print(f"{'='*60}")
        print(f"Run ID: {self.report.run_id}")
        print(f"Pass/Fail: {self.report.pass_fail}")
        print(f"Quality Score: {self.report.blue_scores.quality_score}/100")
        print(f"Risk Score: {self.report.blue_scores.risk_score}/100")
        print(f"Strategy Score: {self.report.blue_scores.strategy_score}/100")
        print(f"Report: {report_path}")
        print(f"{'='*60}\n")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _save_artifact(self, artifact_type: str, filename: str, content: str) -> None:
        """Save an artifact to the run directory."""
        run_dir = Path(self.state.run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        file_path = run_dir / filename
        file_path.write_text(content, encoding="utf-8")


# -----------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------
def main():
    """CLI entry point for running red-blue evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="Run Red-Blue Evaluation Flow")
    parser.add_argument("--input", "-i", required=True, help="Input scenario file")
    parser.add_argument("--context", "-c", default="context/user_ops_context.md", help="Context file")
    parser.add_argument("--memory", "-m", default="memory/memory_log.md", help="Memory log file")
    parser.add_argument("--run-id", "-r", help="Custom run ID")
    parser.add_argument("--red-agent", choices=["competitor_red", "crisis_red", "boundary_red"], 
                        help="Force specific red agent")

    args = parser.parse_args()

    flow = RedBlueFlow()
    if args.red_agent:
        flow._forced_red_agent = args.red_agent

    report = flow.kickoff(inputs={
        "input_file": args.input,
        "context_file": args.context,
        "memory_file": args.memory,
        "run_id": args.run_id,
    })

    print(f"\nFinal Verdict: {report.pass_fail}")


if __name__ == "__main__":
    main()
