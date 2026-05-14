"""
User Ops Swarm Schemas

Pydantic models for all structured outputs in the User Ops Swarm workflow.

Schemas:
    - ContextSummary: Brand/channel/constraints/memory context summary
    - OpportunityAnalysis: User segments + channel analysis output
    - DebateState: Bull/bear thesis, arguments, key_conflicts
    - StrategySummary: Adopted/rejected points, revised strategy
    - RiskReview: Risk assessment across 5 dimensions
    - FinalDecision: Decision (approve/revise/reject/test-only), success metrics
    - MemoryCandidate: Scenario/segment/channel/offer/lesson/reuse_condition
    - RunState: Master state: run_id/status/current_step/artifacts

Usage:
    from src.schemas import ContextSummary, RunState, StrategySummary
    
    # Validate and load
    context = ContextSummary.model_validate(data)
    
    # Serialize to dict
    data = context.model_dump()
    
    # Serialize to JSON
    json_str = context.model_dump_json()
"""

# Context Summary
from src.schemas.context_summary import (
    TaskClassification,
    Objective,
    UserSegment,
    BusinessConstraint,
    ExternalReference,
    AmbiguityFlag,
    ContextSummary,
)

# Opportunity Analysis
from src.schemas.opportunity_analysis import (
    PainPoint,
    UserSceneAnalysis,
    ChannelMetrics,
    ChannelAnalysisEntry,
    ChannelAnalysis,
    OpportunityAnalysis,
)

# Debate State
from src.schemas.debate_state import (
    ExpectedImpact,
    ResourceRequirement,
    RiskConcession,
    BullArgument,
    BearObjection,
    KeyConflict,
    DebateState,
)

# Strategy Summary
from src.schemas.strategy_summary import (
    IntegratedConcern,
    KeyTradeoff,
    ImplementationRequirement,
    StrategyDecision,
    SingleStrategy,
    StrategySummary,
)

# Risk Review
from src.schemas.risk_review import (
    DimensionRisk,
    MitigationAction,
    BlockingCondition,
    ApprovalCondition,
    StrategyRiskReview,
    RiskReview,
)

# Final Decision
from src.schemas.final_decision import (
    DeliberationSummary,
    RevisionRequirement,
    TestParameters,
    MemoryCandidateRef,
    NextSteps,
    StrategyDecision as FinalStrategyDecision,
    FinalDecision,
)

# Memory Candidate
from src.schemas.memory_candidate import (
    EvidenceReference,
    ReuseCondition,
    MemoryCandidate,
    MemorySummary,
    MemoryCandidatesReport,
)

# Run State
from src.schemas.run_state import (
    StepStatus,
    ArtifactReference,
    WorkflowProgress,
    RunMetadata,
    ErrorInfo,
    RunState,
)

__all__ = [
    # Context Summary
    "TaskClassification",
    "Objective",
    "UserSegment",
    "BusinessConstraint",
    "ExternalReference",
    "AmbiguityFlag",
    "ContextSummary",
    # Opportunity Analysis
    "PainPoint",
    "UserSceneAnalysis",
    "ChannelMetrics",
    "ChannelAnalysisEntry",
    "ChannelAnalysis",
    "OpportunityAnalysis",
    # Debate State
    "ExpectedImpact",
    "ResourceRequirement",
    "RiskConcession",
    "BullArgument",
    "BearObjection",
    "KeyConflict",
    "DebateState",
    # Strategy Summary
    "IntegratedConcern",
    "KeyTradeoff",
    "ImplementationRequirement",
    "StrategyDecision",
    "SingleStrategy",
    "StrategySummary",
    # Risk Review
    "DimensionRisk",
    "MitigationAction",
    "BlockingCondition",
    "ApprovalCondition",
    "StrategyRiskReview",
    "RiskReview",
    # Final Decision
    "DeliberationSummary",
    "RevisionRequirement",
    "TestParameters",
    "MemoryCandidateRef",
    "NextSteps",
    "FinalStrategyDecision",
    "FinalDecision",
    # Memory Candidate
    "EvidenceReference",
    "ReuseCondition",
    "MemoryCandidate",
    "MemorySummary",
    "MemoryCandidatesReport",
    # Run State
    "StepStatus",
    "ArtifactReference",
    "WorkflowProgress",
    "RunMetadata",
    "ErrorInfo",
    "RunState",
]
