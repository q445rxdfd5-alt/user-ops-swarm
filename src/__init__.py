"""
User Ops Swarm

A CrewAI-based agent swarm for systematic user operations strategy development.
Implements an 8-step workflow: initialize, load_context, opportunity_analysis,
bull_bear_debate, strategy_manager, risk_review, director_decision, reflection.

Usage:
    from src.flow.user_ops_flow import UserOpsFlow
    from src.utils import initialize_run

    flow = UserOpsFlow()
    result = flow.kickoff(inputs={"task_file": "examples/summer-new-product.md"})
"""

__version__ = "0.1.0"

# Flow imports
from src.flow.user_ops_flow import UserOpsFlow

# Schema imports for validation
from src.schemas import (
    ContextSummary,
    OpportunityAnalysis,
    DebateState,
    StrategySummary,
    RiskReview,
    FinalDecision,
    MemoryCandidatesReport,
    RunState,
)

# Utility imports
from src.utils import (
    initialize_run,
    load_yaml,
    save_state,
    save_artifact,
    load_artifact,
    create_agent_from_yaml,
    create_task_from_yaml,
    generate_run_id,
    ensure_run_directory,
)

__all__ = [
    # Version
    "__version__",
    # Flow
    "UserOpsFlow",
    # Schemas
    "ContextSummary",
    "OpportunityAnalysis",
    "DebateState",
    "StrategySummary",
    "RiskReview",
    "FinalDecision",
    "MemoryCandidatesReport",
    "RunState",
    # Utilities
    "initialize_run",
    "load_yaml",
    "save_state",
    "save_artifact",
    "load_artifact",
    "create_agent_from_yaml",
    "create_task_from_yaml",
    "generate_run_id",
    "ensure_run_directory",
]
