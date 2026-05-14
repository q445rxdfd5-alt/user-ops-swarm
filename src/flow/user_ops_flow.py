"""
User Ops Swarm — Main Orchestration Flow

A 9-step CrewAI-based workflow that simulates a professional restaurant
user operations department as a bounded multi-agent decision system.

Steps:
    1. initialize        → set up run, read inputs
    2. load_context      → parse context + memory into summary
    3. opportunity_analysis → parallel: UserSceneAnalyst + ChannelAnalyst
    4. bull_bear_debate  → parallel: GrowthBullAgent + GrowthBearAgent
    5. strategy_manager  → StrategyManager absorbs debate
    6. execution_crew    → parallel: CampaignPlanner + ContentCreator + DeliverySpecialist + GroupBuyingStrategist + MembershipOperator
    7. risk_review       → RiskReviewer blocks / modifies / approves
    8. director_decision → User Ops Director final verdict
    9. reflection        → Memory candidate for human review
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, ValidationError

from src.schemas import RunState, RunMetadata, WorkflowProgress, StepStatus, ArtifactReference, ErrorInfo
from src.utils import (
    ensure_run_directory,
    generate_run_id,
    create_agent_from_yaml,
    create_task_from_yaml,
    load_yaml,
    save_artifact,
    save_state,
    update_step_status,
)

# Default LLM: MiniMax M2.5 (primary), Ollama (fallback)
_llm_instance = None


def _load_env(key: str, default: str = "") -> str:
    """Read env var, checking .env file if not in os.environ."""
    import os
    val = os.environ.get(key)
    if val:
        return val
    # Try dotenv — use absolute path to avoid CWD dependency
    # __file__ = .../src/flow/user_ops_flow.py
    # parent = .../src/flow
    # parent.parent = .../src
    # parent.parent.parent = project root (has .env)
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip().strip('"\'')
    return default


def _get_llm():
    """Get or create the LLM instance. Prefers MiniMax, falls back to Ollama."""
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    from crewai import LLM

    api_key = _load_env("MINIMAX_API_KEY")
    if api_key:
        base_url = _load_env("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
        model = _load_env("MINIMAX_MODEL", "MiniMax-M2.1")
        try:
            _llm_instance = LLM(
                model=model,
                base_url=base_url,
                api_key=api_key,
            )
            print(f"[LLM] Using MiniMax: {model}")
            return _llm_instance
        except Exception as e:
            print(f"[WARNING] Could not initialize MiniMax LLM: {e}")

    # Fallback to Ollama
    try:
        model = _load_env("OLLAMA_MODEL", "llama3.2")
        base_url = _load_env("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        _llm_instance = LLM(model=f"ollama/{model}", base_url=base_url)
        print(f"[LLM] Using Ollama: {model}")
        return _llm_instance
    except Exception as e:
        print(f"[WARNING] Could not initialize Ollama LLM: {e}")
        _llm_instance = None
    return _llm_instance


# ---------------------------------------------------------------------------
# Artifact filenames
# ---------------------------------------------------------------------------
ARTIFACTS = {
    "context_summary": "01_context_summary.md",
    "opportunity_analysis": "02_opportunity_analysis.md",
    "bull_bear_debate": "03_bull_bear_debate.md",
    "strategy_summary": "04_strategy_summary.md",
    "execution_plan": "05_execution_plan.md",
    "risk_review": "06_risk_review.md",
    "final_decision": "07_final_decision.md",
    "memory_candidate": "08_memory_candidate.md",
}

# ---------------------------------------------------------------------------
# Step ordering
# ---------------------------------------------------------------------------
WORKFLOW_STEPS = [
    "initialize",
    "load_context",
    "opportunity_analysis",
    "bull_bear_debate",
    "strategy_manager",
    "execution_crew",
    "risk_review",
    "director_decision",
    "reflection",
]


# ---------------------------------------------------------------------------
# Swarm State (lightweight, JSON-serializable)
# ---------------------------------------------------------------------------
class SwarmState(BaseModel):
    """Lightweight state passed through each workflow step."""
    run_id: str = ""
    run_dir: str = ""
    status: str = "initialized"
    current_step: str = "initialize"

    # Content from files
    input_content: str = ""
    context_content: str = ""
    memory_content: str = ""

    # Step outputs (as raw strings until validated)
    context_summary: Optional[str] = None
    opportunity_analysis: Optional[str] = None
    bull_bear_debate: Optional[str] = None
    strategy_summary: Optional[str] = None
    execution_plan: Optional[str] = None
    risk_review: Optional[str] = None
    final_decision: Optional[str] = None
    memory_candidate: Optional[str] = None

    # Risk review outcome
    risk_approved: bool = True

    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


# ---------------------------------------------------------------------------
# Agent Registry
# ---------------------------------------------------------------------------
AGENT_FILES = {
    "user_scene_analyst": "user_scene_analyst.yaml",
    "channel_analyst": "channel_analyst.yaml",
    "growth_bull_agent": "growth_bull_agent.yaml",
    "growth_bear_agent": "growth_bear_agent.yaml",
    "strategy_manager": "strategy_manager.yaml",
    # Execution Crew agents
    "campaign_planner": "campaign_planner.yaml",
    "content_creator": "content_creator.yaml",
    "delivery_specialist": "delivery_specialist.yaml",
    "group_buying_strategist": "group_buying_strategist.yaml",
    "membership_operator": "membership_operator.yaml",
    # Review and decision agents
    "risk_reviewer": "risk_reviewer.yaml",
    "director_agent": "director_agent.yaml",
    "reflection_agent": "reflection_agent.yaml",
}


def _load_agent(name: str) -> Any:
    """Load a CrewAI Agent from YAML definition, configured with Ollama LLM."""
    from crewai import Agent
    agents_dir = Path(__file__).parent.parent / "agents"
    path = agents_dir / AGENT_FILES[name]
    yaml_def = load_yaml(path)
    llm = _get_llm()
    return create_agent_from_yaml(yaml_def, llm=llm)


# ---------------------------------------------------------------------------
# Prompt Builder — assembles context for each step
# ---------------------------------------------------------------------------
def _build_context_prompt(state: SwarmState, step: str) -> str:
    """Build the context prompt for a given step."""
    lines = [
        f"# User Ops Swarm — Step: {step}",
        f"Run ID: {state.run_id}",
        "---",
        "## INPUT FILE",
        state.input_content or "(empty)",
        "---",
        "## CONTEXT",
        state.context_content or "(empty)",
        "---",
        "## MEMORY LOG",
        state.memory_content or "(no prior memory)",
    ]

    if step == "opportunity_analysis" and state.context_summary:
        lines += ["---", "## CONTEXT SUMMARY", state.context_summary]

    if step in ("bull_bear_debate", "strategy_manager") and state.opportunity_analysis:
        lines += ["---", "## OPPORTUNITY ANALYSIS", state.opportunity_analysis]

    if step == "strategy_manager" and state.bull_bear_debate:
        lines += ["---", "## BULL/BEAR DEBATE", state.bull_bear_debate]

    if step in ("risk_review", "director_decision", "execution_crew") and state.strategy_summary:
        lines += ["---", "## STRATEGY SUMMARY", state.strategy_summary]

    if step == "director_decision":
        if state.risk_review:
            lines += ["---", "## RISK REVIEW", state.risk_review]
        if state.bull_bear_debate:
            lines += ["---", "## BULL/BEAR DEBATE", state.bull_bear_debate]
        if state.opportunity_analysis:
            lines += ["---", "## OPPORTUNITY ANALYSIS", state.opportunity_analysis]

    if step == "reflection":
        parts = [
            state.final_decision,
            state.risk_review,
            state.strategy_summary,
            state.bull_bear_debate,
            state.opportunity_analysis,
        ]
        for i, p in enumerate(parts):
            if p:
                lines += ["---", f"## ARTIFACT {i+1}", p]

    return "\n\n".join(lines)


# ---------------------------------------------------------------------------
# Memory Log Reader — extracts only approved entries
# ---------------------------------------------------------------------------
def load_approved_memories(mem_path: Path) -> str:
    """
    Read memory_log.md and return only the approved entries as a text block.

    Entry format (approved):
        ### {entry_id} | {date} | operational_pattern
        **Timestamp**: {iso_ts}
        **Approved By**: {approver}
        **Scenario**: ...
        ...

    Returns "(no prior memory)" when file doesn't exist or no approved entries found.
    """
    if not mem_path.exists():
        return "(no prior memory)"

    raw = mem_path.read_text(encoding="utf-8")

    # Find the marker that separates approved section from archived/rejected
    # The approved entries live between "<!-- Approved memories go here -->" and "## Archived"
    marker = "<!-- Approved memories go here -->"
    archived_marker = "## Archived"

    start = raw.find(marker)
    if start == -1:
        # No marker — treat entire file as candidate pool, return empty
        return "(no prior memory)"

    start += len(marker)
    end = raw.find(archived_marker, start)
    if end == -1:
        end = len(raw)

    section = raw[start:end].strip()

    if not section:
        return "(no prior memory)"

    # Collect individual ### entries
    # Each approved entry starts with ### {entry_id}
    # Parse: extract the full entry block between consecutive ### headers
    entries = []
    # Split on ### headings (keep the heading with its body)
    parts = re.split(r'\n(?=### )', section)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Skip review log table rows (| Date | Entry ID | ...)
        if part.startswith("| Date |"):
            continue
        if part.startswith("| ---"):
            continue
        if part.startswith("| "):
            continue
        entries.append(part)

    if not entries:
        return "(no prior memory)"

    # Filter: skip any entry whose status is not approved.
    # Entries are markdown blocks; we check for "**Approved By**: HUMAN" or similar.
    approved = []
    for entry in entries:
        # Entries with approved_by field are considered approved
        # (rejected/pending entries would have different markers or no approved_by)
        if re.search(r'\*\*Approved By\*\*:', entry):
            approved.append(entry)
        # Fallback: if no status field at all but has timestamp+approved_by, include
        elif re.search(r'\*\*Timestamp\*\*:', entry):
            approved.append(entry)

    if not approved:
        return "(no prior memory)"

    return "\n\n---\n\n".join(approved)


# ---------------------------------------------------------------------------
# Output Parsing
# ---------------------------------------------------------------------------
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


def _text_to_markdown(text: str, title: str, step: str) -> str:
    """Convert raw agent output to a readable markdown artifact."""
    lines = [
        f"# {title}",
        f"**Step**: {step}",
        f"**Run ID**: `{datetime.now().strftime('%Y-%m-%d')}`",
        "",
        text.strip() if text else "(no output)",
        "",
        f"*Generated at {datetime.now().isoformat()} by User Ops Swarm*",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main Flow Class
# ---------------------------------------------------------------------------
class UserOpsFlow:
    """
    Orchestrates the full 9-step User Ops Swarm workflow.

    Usage:
        flow = UserOpsFlow()
        result = flow.kickoff(
            inputs={
                "input_file": "examples/summer-new-product.md",
                "context_file": "context/user_ops_context.md",
                "memory_file": "memory/memory_log.md",
                "run_id": None,  # auto-generate
            }
        )
        print(f"Run complete. Status: {flow.state.status}")
    """

    def __init__(self):
        self.state = SwarmState()
        self._run_state: Optional[RunState] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def kickoff(self, inputs: dict[str, Any]) -> SwarmState:
        """
        Execute the full workflow.

        Args:
            inputs: dict with keys:
                - input_file (str): path to task input .md
                - context_file (str): path to context .md
                - memory_file (str): path to memory log .md
                - run_id (str | None): custom run ID or None for auto

        Returns:
            Final SwarmState after all steps complete.
        """
        try:
            self._initialize(inputs)
            self._load_context()
            self._run_opportunity_analysis()
            self._run_bull_bear_debate()
            self._run_strategy_manager()
            self._run_execution_crew()
            self._run_risk_review()
            self._run_director_decision()
            self._run_reflection()
            self.state.status = "completed"
            self._persist_state()
        except Exception as e:
            self.state.status = "failed"
            self.state.error = str(e)
            self._persist_state()
            raise

        return self.state

    # ------------------------------------------------------------------
    # Step 1 — Initialize
    # ------------------------------------------------------------------
    def _initialize(self, inputs: dict[str, Any]) -> None:
        """Set up run directory and load input files."""
        self.state.run_id = inputs.get("run_id") or generate_run_id()
        self.state.run_dir = str(ensure_run_directory(self.state.run_id))
        self.state.current_step = "initialize"
        self.state.status = "running"

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

        # Read memory log — only approved entries
        mem_path = Path(inputs.get("memory_file", "memory/memory_log.md"))
        self.state.memory_content = load_approved_memories(mem_path)

        # Init RunState
        steps = [StepStatus(step_name=s) for s in WORKFLOW_STEPS]
        steps[0].status = "completed"
        steps[0].completed_at = datetime.now().isoformat()

        self._run_state = RunState(
            run_id=self.state.run_id,
            status="running",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            metadata=RunMetadata(
                input_file=inputs.get("input_file", ""),
                context_file=inputs.get("context_file", "context/user_ops_context.md"),
                memory_file=inputs.get("memory_file", "memory/memory_log.md"),
                output_directory=self.state.run_dir,
            ),
            progress=WorkflowProgress(
                current_step="initialize",
                completed_steps=["initialize"],
                pending_steps=WORKFLOW_STEPS[1:],
                step_details=steps,
            ),
        )
        self._persist_state()
        print(f"[Step 1/9] initialize — run_id={self.state.run_id}")

    # ------------------------------------------------------------------
    # Step 2 — Load Context
    # ------------------------------------------------------------------
    def _load_context(self) -> None:
        """Context Loader: synthesize input + context + memory into summary."""
        self.state.current_step = "load_context"
        self._update_run_state_step("load_context", "in_progress", agent_name="ContextLoader")

        try:
            from crewai import Agent, Task
            from crewai.agents.agent_builder.base_agent import BaseAgent

            # Use UserSceneAnalyst as the context loader
            loader_agent: BaseAgent = _load_agent("user_scene_analyst")

            prompt = _build_context_prompt(self.state, "load_context")
            prompt += """

## YOUR TASK
Analyze all input sources above and produce a structured context summary.
Output as markdown with these sections:
1. Task Classification
2. Key Objectives
3. Target User Segments
4. Business Constraints
5. Success Criteria
6. Relevant Memory / Past Learnings
7. Open Questions / Ambiguities

Then output the complete context summary as JSON in this exact format:
```json
{
  "task_classification": "...",
  "objectives": [...],
  "user_segments": [...],
  "constraints": [...],
  "success_criteria": [...],
  "memory_references": [...],
  "open_questions": [...]
}
```"""

            # Execute via a simple Crew (single agent, no crew needed here)
            loader_agent = Agent(
                role="Context Loader",
                goal="Synthesize all input files into a structured context summary for downstream agents.",
                backstory="You are a data integrator responsible for reading and synthesizing all available context—task input, brand context, and historical memory—into a coherent summary that every other agent in the swarm will use as their starting point.",
                verbose=True,
                allow_delegation=False,
                llm=_get_llm(),
            )

            task = Task(
                description=prompt,
                expected_output="Markdown context summary + JSON block",
                agent=loader_agent,
            )

            from crewai import Crew
            crew = Crew(agents=[loader_agent], tasks=[task], verbose=True)
            result = crew.kickoff()

            raw_output = str(result) if result else ""

            # Save markdown artifact
            self._save_artifact("context_summary", ARTIFACTS["context_summary"], raw_output, "Context Loader")

            # Update state
            self.state.context_summary = raw_output
            self._update_run_state_step("load_context", "completed",
                                        output_file=f"{self.state.run_dir}/{ARTIFACTS['context_summary']}")

            print(f"[Step 2/9] load_context — ✓")

        except Exception as e:
            self._handle_step_error("load_context", e)
            raise

    # ------------------------------------------------------------------
    # Step 3 — Opportunity Analysis (parallel: UserScene + Channel)
    # ------------------------------------------------------------------
    def _run_opportunity_analysis(self) -> None:
        """Run UserSceneAnalyst and ChannelAnalyst in parallel."""
        self.state.current_step = "opportunity_analysis"
        self._update_run_state_step("opportunity_analysis", "in_progress",
                                     agent_name="UserSceneAnalyst + ChannelAnalyst")

        try:
            from crewai import Agent, Task, Crew
            from crewai.agents.agent_builder.base_agent import BaseAgent

            scene_agent: BaseAgent = _load_agent("user_scene_analyst")
            channel_agent: BaseAgent = _load_agent("channel_analyst")

            prompt = _build_context_prompt(self.state, "opportunity_analysis")

            task_scene = Task(
                description=prompt + "\n\n## USER SCENE ANALYSIS\nAnalyze the user segments, consumption scenarios, and user opportunity. Output a structured JSON object.",
                expected_output="JSON with user_segments, priority_scenarios, opportunity, evidence, confidence_score",
                agent=scene_agent,
            )

            task_channel = Task(
                description=prompt + "\n\n## CHANNEL ANALYSIS\nAnalyze which channels should play which role. Output a structured JSON object.",
                expected_output="JSON with channel_roles, recommended_channel_mix, conversion_path, priority",
                agent=channel_agent,
            )

            # Run Scene and Channel as separate crews (no Process.parallel in crewai 1.14.4)
            crew_scene = Crew(agents=[scene_agent], tasks=[task_scene], verbose=True)
            crew_channel = Crew(agents=[channel_agent], tasks=[task_channel], verbose=True)
            result_scene = crew_scene.kickoff()
            result_channel = crew_channel.kickoff()
            raw_output = f"## USER SCENE ANALYSIS\n{str(result_scene)}\n\n## CHANNEL ANALYSIS\n{str(result_channel)}"

            self._save_artifact("opportunity_analysis", ARTIFACTS["opportunity_analysis"], raw_output,
                                "UserSceneAnalyst + ChannelAnalyst")
            self.state.opportunity_analysis = raw_output
            self._update_run_state_step("opportunity_analysis", "completed",
                                        output_file=f"{self.state.run_dir}/{ARTIFACTS['opportunity_analysis']}")
            print(f"[Step 3/9] opportunity_analysis — ✓")

        except Exception as e:
            self._handle_step_error("opportunity_analysis", e)
            raise

    # ------------------------------------------------------------------
    # Step 4 — Bull/Bear Debate (parallel)
    # ------------------------------------------------------------------
    def _run_bull_bear_debate(self) -> None:
        """Run GrowthBullAgent and GrowthBearAgent in parallel for structured debate."""
        self.state.current_step = "bull_bear_debate"
        self._update_run_state_step("bull_bear_debate", "in_progress",
                                     agent_name="GrowthBullAgent + GrowthBearAgent")

        try:
            from crewai import Agent, Task, Crew
            from crewai.agents.agent_builder.base_agent import BaseAgent

            bull_agent: BaseAgent = _load_agent("growth_bull_agent")
            bear_agent: BaseAgent = _load_agent("growth_bear_agent")

            prompt = _build_context_prompt(self.state, "bull_bear_debate")

            task_bull = Task(
                description=prompt + "\n\n## YOUR ROLE: GROWTH BULL\nArgue the aggressive growth case. Be specific, cite data where possible, and make your strongest recommendations. Output as JSON.",
                expected_output="JSON with growth_thesis, recommended_actions, expected_upside, required_resources, arguments_against_conservatism",
                agent=bull_agent,
            )

            task_bear = Task(
                description=prompt + "\n\n## YOUR ROLE: GROWTH BEAR\nChallenge the growth perspective. Be adversarial, identify risks, and propose specific blockers or modifications. Output as JSON.",
                expected_output="JSON with bear_thesis, key_objections, risk_scenarios, must_change_items, blockers",
                agent=bear_agent,
            )

            # Phase 1: Bull runs first
            crew_bull = Crew(
                agents=[bull_agent],
                tasks=[task_bull],
                verbose=True,
            )
            result_bull = crew_bull.kickoff()
            bull_output = str(result_bull)

            # Phase 2: Bear challenges Bull's specific points
            bear_prompt = (
                prompt
                + "\n\n## BULL POSITION (from your opponent)\n"
                + bull_output
                + "\n\n## YOUR ROLE: GROWTH BEAR\n"
                + "Your job is to DIRECTLY CHALLENGE the Bull's arguments above. "
                + "Do NOT write an independent analysis — quote specific Bull claims and refute them. "
                + "For each Bull claim: state what they said, why you disagree, and what should change. "
                + "Be adversarial. Output as JSON."
            )
            task_bear_challenge = Task(
                description=bear_prompt,
                expected_output="JSON with bear_thesis, key_objections (each quoting a specific Bull claim), "
                               "risk_scenarios, must_change_items, blockers",
                agent=bear_agent,
            )
            crew_bear = Crew(
                agents=[bear_agent],
                tasks=[task_bear_challenge],
                verbose=True,
            )
            result_bear = crew_bear.kickoff()
            bear_output = str(result_bear)

            raw_output = (
                "## BULL POSITION\n"
                + bull_output
                + "\n\n## BEAR COUNTER (directly challenges Bull above)\n"
                + bear_output
            )

            self._save_artifact("bull_bear_debate", ARTIFACTS["bull_bear_debate"], raw_output,
                                "GrowthBullAgent + GrowthBearAgent")
            self.state.bull_bear_debate = raw_output
            self._update_run_state_step("bull_bear_debate", "completed",
                                        output_file=f"{self.state.run_dir}/{ARTIFACTS['bull_bear_debate']}")
            print(f"[Step 4/9] bull_bear_debate — ✓")

        except Exception as e:
            self._handle_step_error("bull_bear_debate", e)
            raise

    # ------------------------------------------------------------------
    # Step 5 — Strategy Manager
    # ------------------------------------------------------------------
    def _run_strategy_manager(self) -> None:
        """StrategyManager absorbs both sides and produces revised strategy."""
        self.state.current_step = "strategy_manager"
        self._update_run_state_step("strategy_manager", "in_progress",
                                     agent_name="StrategyManager")

        try:
            from crewai import Agent, Task, Crew
            from crewai.agents.agent_builder.base_agent import BaseAgent

            manager_agent: BaseAgent = _load_agent("strategy_manager")
            prompt = _build_context_prompt(self.state, "strategy_manager")

            task = Task(
                description=(
                    prompt
                    + "\n\n## BULL/BEAR DEBATE OUTPUT\n"
                    + self.state.bull_bear_debate
                    + "\n\n## YOUR ROLE: STRATEGY MANAGER\n"
                    + "Synthesize the bull and bear arguments into a revised strategy. "
                    + "You MUST quote specific Bull claims and explain whether you adopt or reject each. "
                    + "You MUST quote specific Bear objections and explain how you address them. "
                    + "Be explicit: adopted_bull_points and adopted_bear_points must cite specific claims. "
                    + "Output as JSON."
                ),
                expected_output="JSON with strategy_summary, adopted_bull_points (with Bull quote), "
                               "adopted_bear_points (with Bear quote), rejected_points (with quote), "
                               "revised_strategy, recommended_scope, test_plan",
                agent=manager_agent,
            )

            crew = Crew(agents=[manager_agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            raw_output = str(result) if result else ""

            self._save_artifact("strategy_summary", ARTIFACTS["strategy_summary"], raw_output,
                                "StrategyManager")
            self.state.strategy_summary = raw_output
            self._update_run_state_step("strategy_manager", "completed",
                                        output_file=f"{self.state.run_dir}/{ARTIFACTS['strategy_summary']}")
            print(f"[Step 5/9] strategy_manager — ✓")

        except Exception as e:
            self._handle_step_error("strategy_manager", e)
            raise

    # ------------------------------------------------------------------
    # Step 6 — Execution Crew (Campaign Planner + Content Creator + 
    #           Delivery Specialist + Group-Buying Strategist + Membership Operator)
    # ------------------------------------------------------------------
    def _run_execution_crew(self) -> None:
        """Run 5 execution planning agents in parallel to produce the execution plan."""
        self.state.current_step = "execution_crew"
        self._update_run_state_step("execution_crew", "in_progress",
                                     agent_name="ExecutionCrew (5 agents)")

        try:
            from crewai import Agent, Task, Crew
            from crewai.agents.agent_builder.base_agent import BaseAgent

            # Load all 5 execution agents
            campaign_agent: BaseAgent = _load_agent("campaign_planner")
            content_agent: BaseAgent = _load_agent("content_creator")
            delivery_agent: BaseAgent = _load_agent("delivery_specialist")
            groupbuy_agent: BaseAgent = _load_agent("group_buying_strategist")
            membership_agent: BaseAgent = _load_agent("membership_operator")

            prompt = _build_context_prompt(self.state, "execution_crew")

            # Campaign Planner task
            task_campaign = Task(
                description=prompt + """

## YOUR ROLE: CAMPAIGN PLANNER
Design the comprehensive campaign structure that orchestrates all execution components.
Translate the approved strategy into an actionable campaign blueprint with phases, 
content schedule, group-buying windows, delivery timeline, and membership integration.
Output as JSON with campaign_id, campaign_phases, content_schedule, group_buying_window,
delivery_timeline, membership_integration, resource_requirements, success_metrics.""",
                expected_output="JSON with campaign_id, campaign_phases, content_schedule, group_buying_window, delivery_timeline, membership_integration",
                agent=campaign_agent,
            )

            # Content Creator task
            task_content = Task(
                description=prompt + """

## YOUR ROLE: CONTENT CREATOR
Design all content assets required for the campaign execution.
Be the voice and face of the campaign—design copy, visuals, video, and UGC templates
for all channels. Ensure content supports group-buying viral mechanics.
Output as JSON with content_plan_id, content_themes, content_assets, channel_content_map,
group_buying_content, content_calendar.""",
                expected_output="JSON with content_plan_id, content_assets, channel_content_map, group_buying_content, content_calendar",
                agent=content_agent,
            )

            # Delivery Specialist task
            task_delivery = Task(
                description=prompt + """

## YOUR ROLE: DELIVERY SPECIALIST
Design the end-to-end fulfillment and delivery experience.
Everything after the user clicks "buy" is your domain—fulfillment, packaging,
notifications, delivery windows, and post-delivery follow-up.
Output as JSON with delivery_plan_id, fulfillment_architecture, delivery_logistics,
packaging_design, notification_system, delivery_timeline.""",
                expected_output="JSON with delivery_plan_id, fulfillment_architecture, delivery_logistics, packaging_design, notification_system",
                agent=delivery_agent,
            )

            # Group-Buying Strategist task
            task_groupbuy = Task(
                description=prompt + """

## YOUR ROLE: GROUP-BUYING STRATEGIST
Design group-buying mechanics that drive viral user acquisition.
Design discount tiers, team formation dynamics, time pressure, and social proof
to maximize participation while maintaining healthy unit economics.
Output as JSON with group_buying_plan_id, discount_tier_structure, team_formation_mechanics,
time_pressure_design, viral_mechanics, participation_funnel, economics_analysis.""",
                expected_output="JSON with group_buying_plan_id, discount_tier_structure, team_formation_mechanics, economics_analysis",
                agent=groupbuy_agent,
            )

            # Membership Operator task
            task_membership = Task(
                description=prompt + """

## YOUR ROLE: MEMBERSHIP OPERATOR
Design membership engagement, retention, and upgrade mechanics.
Transform one-time buyers into long-term advocates with tier systems,
engagement loops, and exclusive access.
Output as JSON with membership_plan_id, tier_structure, engagement_loop_design,
loyalty_currency_system, exclusive_access_program, retention_mechanics.""",
                expected_output="JSON with membership_plan_id, tier_structure, engagement_loop_design, loyalty_currency_system",
                agent=membership_agent,
            )

            # Run all 5 agents in parallel (separate crews)
            crew_campaign = Crew(agents=[campaign_agent], tasks=[task_campaign], verbose=True)
            crew_content = Crew(agents=[content_agent], tasks=[task_content], verbose=True)
            crew_delivery = Crew(agents=[delivery_agent], tasks=[task_delivery], verbose=True)
            crew_groupbuy = Crew(agents=[groupbuy_agent], tasks=[task_groupbuy], verbose=True)
            crew_membership = Crew(agents=[membership_agent], tasks=[task_membership], verbose=True)

            result_campaign = crew_campaign.kickoff()
            result_content = crew_content.kickoff()
            result_delivery = crew_delivery.kickoff()
            result_groupbuy = crew_groupbuy.kickoff()
            result_membership = crew_membership.kickoff()

            # Combine all outputs into execution plan
            raw_output = "\n\n".join([
                "## CAMPAIGN PLANNING\n" + str(result_campaign),
                "## CONTENT CREATION\n" + str(result_content),
                "## DELIVERY PLANNING\n" + str(result_delivery),
                "## GROUP-BUYING PLANNING\n" + str(result_groupbuy),
                "## MEMBERSHIP PLANNING\n" + str(result_membership),
            ])

            self._save_artifact("execution_plan", ARTIFACTS["execution_plan"], raw_output,
                                "ExecutionCrew (5 agents)")
            self.state.execution_plan = raw_output
            self._update_run_state_step("execution_crew", "completed",
                                        output_file=f"{self.state.run_dir}/{ARTIFACTS['execution_plan']}")
            print(f"[Step 6/9] execution_crew — ✓")

        except Exception as e:
            self._handle_step_error("execution_crew", e)
            raise

    # ------------------------------------------------------------------
    # Step 7 — Risk Review
    # ------------------------------------------------------------------
    def _run_risk_review(self) -> None:
        """RiskReviewer assesses the execution plan and may BLOCK the run."""
        self.state.current_step = "risk_review"
        self._update_run_state_step("risk_review", "in_progress",
                                     agent_name="RiskReviewer")

        try:
            from crewai import Agent, Task, Crew
            from crewai.agents.agent_builder.base_agent import BaseAgent

            risk_agent: BaseAgent = _load_agent("risk_reviewer")
            prompt = _build_context_prompt(self.state, "risk_review")

            task = Task(
                description=prompt + "\n\n## YOUR ROLE: RISK REVIEWER\nReview the execution plan from every risk dimension: profit, brand, fulfillment, platform, member assets. Your BLOCK decision is absolute. Focus on the campaign_planning, content_creation, delivery_planning, group_buying_planning, and membership_planning outputs. Output as JSON with risk_level and required_changes.",
                expected_output="JSON with risk_level (low/medium/high/block), profit_risk, brand_risk, fulfillment_risk, platform_risk, member_asset_risk, required_changes, approval_condition, reviewer_recommendation",
                agent=risk_agent,
            )

            crew = Crew(agents=[risk_agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            raw_output = str(result) if result else ""

            # Parse risk level to decide if we continue
            parsed = _parse_json_from_text(raw_output)
            if parsed:
                risk_level = parsed.get("risk_level", "medium")
                if risk_level == "block":
                    self.state.risk_approved = False
                    self.state.error = f"BLOCK: Risk Reviewer blocked the run. Changes required: {parsed.get('required_changes', [])}"
                    print(f"[Step 7/9] risk_review — BLOCKED")
                else:
                    self.state.risk_approved = True
                    print(f"[Step 7/9] risk_review — {risk_level.upper()} (proceeding)")

            self._save_artifact("risk_review", ARTIFACTS["risk_review"], raw_output, "RiskReviewer")
            self.state.risk_review = raw_output
            self._update_run_state_step("risk_review", "completed",
                                        output_file=f"{self.state.run_dir}/{ARTIFACTS['risk_review']}")

        except Exception as e:
            self._handle_step_error("risk_review", e)
            raise

    # ------------------------------------------------------------------
    # Step 8 — Director Decision
    # ------------------------------------------------------------------
    def _run_director_decision(self) -> None:
        """Director makes the final verdict: approve / revise / reject / test-only."""
        self.state.current_step = "director_decision"
        self._update_run_state_step("director_decision", "in_progress",
                                     agent_name="UserOpsDirector")

        try:
            from crewai import Agent, Task, Crew
            from crewai.agents.agent_builder.base_agent import BaseAgent

            director_agent: BaseAgent = _load_agent("director_agent")
            prompt = _build_context_prompt(self.state, "director_decision")

            task = Task(
                description=prompt + f"""

## YOUR ROLE: USER OPS DIRECTOR
Review all artifacts and make a binding decision.
Decision options: approve / revise / reject / test-only
If blocked by Risk Reviewer (risk_level=block), your only options are revise or reject.

Output as JSON:
```json
{{
  "decision": "approve|revise|reject|test-only",
  "rationale": "...",
  "final_plan": {{...}},
  "execution_scope": "...",
  "success_metrics": [...],
  "risk_controls": [...]
}}
```""",
                expected_output="JSON with decision (approve/revise/reject/test-only), rationale, final_plan, execution_scope, success_metrics, risk_controls",
                agent=director_agent,
            )

            crew = Crew(agents=[director_agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            raw_output = str(result) if result else ""

            self._save_artifact("final_decision", ARTIFACTS["final_decision"], raw_output, "UserOpsDirector")
            self.state.final_decision = raw_output
            self._update_run_state_step("director_decision", "completed",
                                        output_file=f"{self.state.run_dir}/{ARTIFACTS['final_decision']}")

            # Print the decision
            parsed = _parse_json_from_text(raw_output)
            decision = parsed.get("decision", "unknown") if parsed else "unknown"
            print(f"[Step 8/9] director_decision — {decision.upper()}")

        except Exception as e:
            self._handle_step_error("director_decision", e)
            raise

    # ------------------------------------------------------------------
    # Step 9 — Reflection / Memory Candidate
    # ------------------------------------------------------------------
    def _run_reflection(self) -> None:
        """Reflection Agent extracts reusable learnings. NOT auto-written to memory."""
        self.state.current_step = "reflection"
        self._update_run_state_step("reflection", "in_progress",
                                    agent_name="ReflectionAgent")

        try:
            from crewai import Agent, Task, Crew
            from crewai.agents.agent_builder.base_agent import BaseAgent

            reflection_agent: BaseAgent = _load_agent("reflection_agent")
            prompt = _build_context_prompt(self.state, "reflection")

            task = Task(
                description=prompt + """

## YOUR ROLE: REFLECTION AGENT
Extract reusable learnings from this entire run. Do NOT write to the memory log.
Output memory candidates for human review. Format as JSON:

```json
{
  "scenario": "...",
  "segment": "...",
  "channel": "...",
  "offer": "...",
  "lesson": "...",
  "risk": "...",
  "reuse_condition": "...",
  "confidence": 0.0
}
```""",
                expected_output="JSON memory_candidate with scenario/segment/channel/offer/lesson/risk/reuse_condition/confidence. Does NOT write to memory_log.md.",
                agent=reflection_agent,
            )

            crew = Crew(agents=[reflection_agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            raw_output = str(result) if result else ""

            self._save_artifact("memory_candidate", ARTIFACTS["memory_candidate"], raw_output,
                                "ReflectionAgent", status="draft")
            self.state.memory_candidate = raw_output
            self._update_run_state_step("reflection", "completed",
                                        output_file=f"{self.state.run_dir}/{ARTIFACTS['memory_candidate']}")
            print(f"[Step 9/9] reflection — ✓ (memory_candidate ready for human review)")

        except Exception as e:
            self._handle_step_error("reflection", e)
            raise

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _save_artifact(
        self,
        artifact_type: str,
        filename: str,
        content: str,
        agent_name: str,
        status: str = "validated",
    ) -> None:
        """Write a markdown artifact and register it in the RunState."""
        run_dir = Path(self.state.run_dir)
        file_path = run_dir / filename
        file_path.write_text(content, encoding="utf-8")

        if self._run_state:
            artifact = ArtifactReference(
                artifact_id=f"art-{len(self._run_state.artifacts):03d}",
                artifact_type=artifact_type,
                file_path=str(file_path),
                created_at=datetime.now().isoformat(),
                status=status,
            )
            self._run_state.artifacts.append(artifact)

    def _update_run_state_step(
        self,
        step_name: str,
        status: str,
        agent_name: Optional[str] = None,
        output_file: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Update step status in RunState and persist."""
        if self._run_state is None:
            return
        self._run_state = update_step_status(
            self._run_state,
            step_name,
            status,
            agent_name=agent_name,
            output_file=output_file,
            error_message=error_message,
        )
        self._run_state.updated_at = datetime.now().isoformat()
        self._persist_state()

    def _handle_step_error(self, step_name: str, error: Exception) -> None:
        """Record step failure in state."""
        self.state.error = f"{step_name}: {str(error)}"
        if self._run_state:
            err = ErrorInfo(
                step_name=step_name,
                error_type=type(error).__name__,
                error_message=str(error),
                timestamp=datetime.now().isoformat(),
            )
            self._run_state.errors.append(err)
        self._update_run_state_step(step_name, "failed", error_message=str(error))

    def _persist_state(self) -> None:
        """Write RunState to state.json."""
        if self._run_state:
            self._run_state.status = self.state.status
            self._run_state.updated_at = datetime.now().isoformat()
            if self.state.status == "completed":
                self._run_state.completed_at = datetime.now().isoformat()
            save_state(self._run_state, self.state.run_id)
