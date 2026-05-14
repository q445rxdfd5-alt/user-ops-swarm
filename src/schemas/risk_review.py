"""
Risk Review Schema

Output from the Risk Reviewer agent containing risk assessment across 5 dimensions.
Documents overall risk score and blocking conditions if BLOCK authority is exercised.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class DimensionRisk(BaseModel):
    """Risk assessment for a single dimension."""
    dimension: Literal["financial", "operational", "legal_compliance", "reputational", 
                       "technical"] = Field(description="Risk dimension")
    score: float = Field(ge=0.0, le=10.0, description="Risk score (0=low, 10=high)")
    concerns: list[str] = Field(
        default_factory=list, description="Specific concerns in this dimension"
    )
    relevant_metrics: list[str] = Field(
        default_factory=list, description="Metrics relevant to this risk"
    )


class MitigationAction(BaseModel):
    """A required mitigation action."""
    mitigation_id: str = Field(description="Unique identifier for this mitigation")
    action: str = Field(description="Specific mitigation action required")
    responsible_party: str = Field(description="Who is responsible for this mitigation")
    verification_method: str = Field(description="How to verify mitigation was effective")
    deadline: str = Field(description="Deadline for completing this mitigation")
    status: Literal["pending", "in_progress", "completed", "overdue"] = Field(
        default="pending", description="Current status"
    )


class BlockingCondition(BaseModel):
    """A condition that triggered BLOCK authority."""
    condition_id: str = Field(description="Unique identifier for this condition")
    dimension: Literal["financial", "operational", "legal_compliance", "reputational", 
                       "technical"] = Field(description="Dimension where blocking occurred")
    description: str = Field(description="Specific blocking condition")
    severity: Literal["critical", "high"] = Field(
        default="high", description="Severity of the blocking condition"
    )
    remediation_requirements: list[str] = Field(
        default_factory=list, description="What must be done to unblock"
    )


class ApprovalCondition(BaseModel):
    """A condition for approval (if not blocked)."""
    condition_id: str = Field(description="Unique identifier for this condition")
    description: str = Field(description="Specific condition for approval")
    priority: Literal["critical", "high", "medium", "low"] = Field(
        default="medium", description="Priority of this condition"
    )
    verification: str = Field(description="How to verify this condition was met")


class StrategyRiskReview(BaseModel):
    """Risk review result for a single strategy."""
    review_id: str = Field(description="Unique identifier for this review")
    strategy_reference: str = Field(description="Reference to the strategy reviewed")
    review_status: Literal["approved", "blocked", "approved_with_conditions"] = Field(
        description="Overall review status"
    )
    block_exercised: bool = Field(
        default=False, description="Whether BLOCK authority was exercised"
    )
    risk_assessment: list[DimensionRisk] = Field(
        default_factory=list, description="Risk scores across all dimensions"
    )
    overall_risk_score: float = Field(
        ge=0.0, le=10.0, description="Weighted overall risk score"
    )
    risk_threshold_check: Literal["within_tolerance", "exceeds_tolerance"] = Field(
        description="Whether risk is within acceptable tolerance"
    )
    blocking_conditions: list[BlockingCondition] = Field(
        default_factory=list, description="Conditions that triggered blocking"
    )
    required_mitigations: list[MitigationAction] = Field(
        default_factory=list, description="Mitigations required to proceed"
    )
    approval_conditions: list[ApprovalCondition] = Field(
        default_factory=list, description="Conditions for approval if not blocked"
    )
    review_notes: Optional[str] = Field(
        default=None, description="Additional review notes"
    )
    reviewer_confidence: Literal["very_confident", "confident", "neutral", "uncertain"] = Field(
        default="confident", description="Reviewer's confidence in assessment"
    )


class RiskReview(BaseModel):
    """
    Complete risk review output for all strategies.
    
    Produced by the Risk Reviewer agent with authority to BLOCK strategies
    that exceed risk thresholds. Documents risk assessment across 5 dimensions.
    """
    run_id: str = Field(description="Identifier of the run this review belongs to")
    reviews: list[StrategyRiskReview] = Field(
        default_factory=list, description="Reviews for each strategy"
    )
    total_strategies_reviewed: int = Field(
        default=0, description="Total number of strategies reviewed"
    )
    approved_count: int = Field(default=0, description="Strategies approved")
    blocked_count: int = Field(default=0, description="Strategies blocked")
    approved_with_conditions_count: int = Field(
        default=0, description="Strategies approved with conditions"
    )
    total_blocking_conditions: int = Field(
        default=0, description="Total blocking conditions identified"
    )
    highest_risk_strategy: Optional[str] = Field(
        default=None, description="Strategy ID with highest overall risk"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Overall recommendations"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "2026-05-14-100000",
                "reviews": [
                    {
                        "review_id": "review-1",
                        "strategy_reference": "strat-1",
                        "review_status": "approved_with_conditions",
                        "block_exercised": False,
                        "risk_assessment": [
                            {
                                "dimension": "financial",
                                "score": 4.5,
                                "concerns": ["Margin compression risk"],
                                "relevant_metrics": ["gross_margin"]
                            }
                        ],
                        "overall_risk_score": 5.2,
                        "risk_threshold_check": "within_tolerance",
                        "approval_conditions": [
                            {
                                "condition_id": "cond-1",
                                "description": "Maintain minimum 40% gross margin",
                                "priority": "critical"
                            }
                        ]
                    }
                ]
            }
        }
