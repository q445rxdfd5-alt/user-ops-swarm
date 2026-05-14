"""
Strategy Summary Schema

Output from the Strategy Manager containing adopted/rejected points and revised strategy.
Documents explicit adopt/reject decisions with reasoning and implementation requirements.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class IntegratedConcern(BaseModel):
    """A bear concern that has been integrated into the strategy."""
    concern_id: str = Field(description="Reference to the original bear objection")
    concern_description: str = Field(description="Original concern from bear argument")
    resolution: str = Field(description="How this concern was addressed in strategy")
    residual_risk: str = Field(default="low", description="Remaining risk level")


class KeyTradeoff(BaseModel):
    """A tradeoff accepted in the strategy."""
    tradeoff_id: str = Field(description="Unique identifier for this tradeoff")
    description: str = Field(description="What was traded off")
    trade_for: str = Field(description="What was gained in exchange")
    rationale: str = Field(description="Why this tradeoff was accepted")
    accepted_by: Optional[str] = Field(
        default=None, description="Which stakeholder accepted this tradeoff"
    )


class ImplementationRequirement(BaseModel):
    """Implementation requirements for a strategy."""
    priority_rank: int = Field(ge=1, le=10, description="Priority rank (1=highest)")
    timeline_weeks: int = Field(ge=1, description="Implementation timeline in weeks")
    resource_requirements: str = Field(description="Resources needed")
    success_metrics: list[str] = Field(
        default_factory=list, description="Metrics to measure success"
    )


class StrategyDecision(BaseModel):
    """Decision status for a single opportunity within a strategy."""
    opportunity_id: str = Field(description="Reference to the opportunity")
    decision: Literal["adopted", "rejected", "merged", "deferred"] = Field(
        description="Decision on this opportunity"
    )
    reasoning: str = Field(description="Why this decision was made")


class StrategySummary(BaseModel):
    """
    Summary of synthesized strategies with adopt/reject decisions.
    
    Produced by the Strategy Manager after integrating bull and bear arguments.
    Documents explicit decisions and implementation requirements.
    """
    run_id: str = Field(description="Identifier of the run this summary belongs to")
    strategies: list["SingleStrategy"] = Field(
        default_factory=list, description="List of synthesized strategies"
    )
    total_opportunities: int = Field(
        default=0, description="Total opportunities considered"
    )
    adopted_count: int = Field(default=0, description="Count of adopted opportunities")
    rejected_count: int = Field(default=0, description="Count of rejected opportunities")
    merged_count: int = Field(default=0, description="Count of merged opportunities")
    deferred_count: int = Field(default=0, description="Count of deferred opportunities")


class SingleStrategy(BaseModel):
    """A single synthesized strategy."""
    strategy_id: str = Field(description="Unique identifier for this strategy")
    strategy_name: str = Field(description="Human-readable strategy name")
    source_opportunities: list[str] = Field(
        default_factory=list, description="Opportunity IDs incorporated"
    )
    problem_addressed: str = Field(description="Problem from scene analysis this addresses")
    decisions: list[StrategyDecision] = Field(
        default_factory=list, description="Adopt/reject decisions for each opportunity"
    )
    integrated_concerns: list[IntegratedConcern] = Field(
        default_factory=list, description="Bear concerns integrated into strategy"
    )
    tradeoffs: list[KeyTradeoff] = Field(
        default_factory=list, description="Key tradeoffs accepted"
    )
    implementation: ImplementationRequirement = Field(
        description="Implementation requirements and priorities"
    )
    risk_review_status: Literal["pending_review", "approved", "blocked", 
                                  "approved_with_conditions"] = Field(
        default="pending_review", description="Current risk review status"
    )
    confidence_score: float = Field(
        ge=0.0, le=10.0, description="Confidence in this strategy's success"
    )
    revision_notes: Optional[str] = Field(
        default=None, description="Notes for potential revisions"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "strategy_id": "strat-1",
                "strategy_name": "Summer Growth Push",
                "source_opportunities": ["opp-1", "opp-2"],
                "decisions": [
                    {
                        "opportunity_id": "opp-1",
                        "decision": "adopted",
                        "reasoning": "Strong growth potential with manageable risk"
                    }
                ],
                "implementation": {
                    "priority_rank": 1,
                    "timeline_weeks": 8,
                    "success_metrics": ["new_customers", "revenue_growth"]
                },
                "confidence_score": 7.5
            }
        }


# Update forward reference
StrategySummary.model_rebuild()
