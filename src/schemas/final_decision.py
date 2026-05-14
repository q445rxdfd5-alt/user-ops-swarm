"""
Final Decision Schema

Output from the User Ops Director containing final decisions on strategies.
Documents approve/revise/reject/test-only decisions with success metrics.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class DeliberationSummary(BaseModel):
    """Summary of the deliberation process."""
    bull_consensus: str = Field(description="Consensus from bull arguments")
    bear_objections_addressed: list[str] = Field(
        default_factory=list, description="Bear objections that were addressed"
    )
    risk_review_outcome: str = Field(description="Outcome from risk review")
    outstanding_concerns: list[str] = Field(
        default_factory=list, description="Concerns that remain unaddressed"
    )


class RevisionRequirement(BaseModel):
    """A requirement for revision if decision is 'revise'."""
    requirement_id: str = Field(description="Unique identifier for this requirement")
    requirement: str = Field(description="Specific revision requirement")
    priority: Literal["critical", "high", "medium", "low"] = Field(
        description="Priority of this requirement"
    )
    suggestion: Optional[str] = Field(
        default=None, description="Suggestion for how to address"
    )


class TestParameters(BaseModel):
    """Parameters for a test-only decision."""
    test_scope: str = Field(description="Scope of the test")
    sample_size: str = Field(description="Required sample size")
    success_criteria: str = Field(description="Criteria for test success")
    go_threshold: str = Field(description="Metric value to proceed with full rollout")
    no_go_threshold: str = Field(description="Metric value to terminate")
    test_duration_weeks: int = Field(
        ge=1, description="Duration of test in weeks"
    )
    control_group: bool = Field(
        default=True, description="Whether to include a control group"
    )


class MemoryCandidateRef(BaseModel):
    """Reference to a memory candidate for potential preservation."""
    candidate_id: str = Field(description="Reference to the memory candidate")
    insight_type: Literal["strategic_pattern", "market_insight", "user_behavior",
                        "team_effectiveness", "process_improvement", "risk_lesson"] = Field(
        description="Type of insight"
    )
    content: str = Field(description="Summary of the insight")
    evidence_basis: list[str] = Field(
        default_factory=list, description="References supporting this insight"
    )
    preservation_priority: Literal["high", "medium", "low"] = Field(
        default="medium", description="Priority for memory preservation"
    )
    tags: list[str] = Field(default_factory=list, description="Categorization tags")


class NextSteps(BaseModel):
    """Next steps based on the decision."""
    immediate_actions: list[str] = Field(
        default_factory=list, description="Actions to take immediately"
    )
    follow_up_required: bool = Field(
        default=False, description="Whether follow-up is required"
    )
    follow_up_date: Optional[str] = Field(
        default=None, description="Date for follow-up"
    )
    escalation_required: bool = Field(
        default=False, description="Whether escalation is required"
    )


class StrategyDecision(BaseModel):
    """Final decision for a single strategy."""
    decision_id: str = Field(description="Unique identifier for this decision")
    strategy_reference: str = Field(description="Reference to the strategy")
    decision: Literal["approve", "revise", "reject", "test_only"] = Field(
        description="Director's decision"
    )
    decision_rationale: str = Field(
        description="Rationale for this decision, referencing deliberation"
    )
    deliberation: DeliberationSummary = Field(
        description="Summary of deliberation process"
    )
    revision_requirements: list[RevisionRequirement] = Field(
        default_factory=list, description="Requirements if decision is 'revise'"
    )
    test_parameters: Optional[TestParameters] = Field(
        default=None, description="Test parameters if decision is 'test_only'"
    )
    memory_candidates: list[MemoryCandidateRef] = Field(
        default_factory=list, description="Memory candidates from this decision"
    )
    next_steps: NextSteps = Field(description="Next steps based on decision")
    confidence: Literal["very_confident", "confident", "neutral", "uncertain"] = Field(
        description="Director's confidence in this decision"
    )


class FinalDecision(BaseModel):
    """
    Complete final decisions for all strategies.
    
    Produced by the User Ops Director as the final step in the deliberation process.
    Contains approve/revise/reject/test-only decisions with full rationale and metrics.
    """
    run_id: str = Field(description="Identifier of the run this decision belongs to")
    decisions: list[StrategyDecision] = Field(
        default_factory=list, description="Final decisions for each strategy"
    )
    total_strategies: int = Field(
        default=0, description="Total strategies reviewed"
    )
    approved_count: int = Field(default=0, description="Strategies approved")
    revise_count: int = Field(default=0, description="Strategies requiring revision")
    rejected_count: int = Field(default=0, description="Strategies rejected")
    test_only_count: int = Field(default=0, description="Strategies approved for testing only")
    memory_candidates_generated: int = Field(
        default=0, description="Total memory candidates created"
    )
    director_notes: Optional[str] = Field(
        default=None, description="Additional notes from the director"
    )
    decision_timestamp: str = Field(
        description="ISO timestamp of when decisions were made"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "2026-05-14-100000",
                "decisions": [
                    {
                        "decision_id": "dec-1",
                        "strategy_reference": "strat-1",
                        "decision": "approve",
                        "decision_rationale": "Strong growth potential with manageable risk. Bull case well-supported with data. Risk within tolerance.",
                        "deliberation": {
                            "bull_consensus": "High conviction on new customer acquisition",
                            "bear_objections_addressed": ["Margin compression mitigated by caps"],
                            "risk_review_outcome": "Approved with conditions"
                        },
                        "next_steps": {
                            "immediate_actions": ["Brief marketing team", "Set up tracking"],
                            "follow_up_required": True,
                            "follow_up_date": "2026-06-01"
                        },
                        "confidence": "confident"
                    }
                ],
                "decision_timestamp": "2026-05-14T10:30:00Z"
            }
        }
