"""
Debate State Schema

Output from the Bull/Bear Debate CREW containing growth arguments vs. risk objections.
Contains bull thesis, bear thesis, arguments, and key conflicts.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class ExpectedImpact(BaseModel):
    """Expected impact metrics for a bull argument."""
    user_growth_pct: Optional[float] = Field(
        default=None, description="Expected user growth percentage"
    )
    revenue_impact: Optional[str] = Field(default=None, description="Expected revenue impact")
    market_share_delta: Optional[str] = Field(
        default=None, description="Expected market share change"
    )
    timeline_months: Optional[int] = Field(
        default=None, description="Timeline to realize impact in months"
    )


class ResourceRequirement(BaseModel):
    """Resources required to execute a bull opportunity."""
    budget: Optional[str] = Field(default=None, description="Budget requirement")
    headcount: Optional[int] = Field(default=None, description="Additional headcount needed")
    technology: Optional[str] = Field(default=None, description="Technology requirements")
    channel_investment: Optional[str] = Field(
        default=None, description="Channel-specific investment"
    )


class RiskConcession(BaseModel):
    """An acknowledged risk with mitigation strategy."""
    risk_description: str = Field(description="Description of the acknowledged risk")
    mitigation: str = Field(description="How this risk will be mitigated")
    residual_score: float = Field(
        default=5.0, ge=0.0, le=10.0, description="Remaining risk after mitigation"
    )


class BullArgument(BaseModel):
    """A single bull argument for an opportunity."""
    argument_id: str = Field(description="Unique identifier for this argument")
    opportunity_id: str = Field(description="Reference to the opportunity being argued")
    thesis_statement: str = Field(description="Compelling thesis for this opportunity")
    expected_impact: ExpectedImpact = Field(description="Expected impact metrics")
    supporting_evidence: list[str] = Field(
        default_factory=list, description="Evidence supporting this bull case"
    )
    required_resources: ResourceRequirement = Field(
        description="Resources needed to pursue this opportunity"
    )
    key_assumptions: list[str] = Field(
        default_factory=list, description="Assumptions underlying this bull case"
    )
    risk_concessions: list[RiskConcession] = Field(
        default_factory=list, description="Acknowledged risks with mitigations"
    )
    conviction_level: Literal["very_high", "high", "medium", "low"] = Field(
        description="Conviction in this bull argument"
    )


class BearObjection(BaseModel):
    """A single bear objection to an opportunity."""
    objection_id: str = Field(description="Unique identifier for this objection")
    opportunity_id: str = Field(description="Reference to the opportunity being objected")
    objection_statement: str = Field(description="Core objection statement")
    impact_assessment: Literal["critical", "high", "medium", "low"] = Field(
        description="Potential impact if ignored"
    )
    supporting_evidence: list[str] = Field(
        default_factory=list, description="Evidence supporting this objection"
    )
    precedent_cases: list[str] = Field(
        default_factory=list, description="Historical cases supporting this concern"
    )
    severity_reasoning: str = Field(description="Why this objection has weight")
    rebuttal_required: bool = Field(
        default=True, description="Whether this objection requires rebuttal"
    )


class KeyConflict(BaseModel):
    """A key conflict between bull and bear positions."""
    conflict_id: str = Field(description="Unique identifier for this conflict")
    topic: str = Field(description="The topic of disagreement")
    bull_position: str = Field(description="The bull position on this topic")
    bear_position: str = Field(description="The bear position on this topic")
    resolution_status: Literal["resolved", "pending", "unresolved"] = Field(
        default="pending", description="Current resolution status"
    )
    resolution_notes: Optional[str] = Field(
        default=None, description="How this conflict was resolved or why it remains"
    )
    priority: Literal["critical", "high", "medium", "low"] = Field(
        description="Priority of resolving this conflict"
    )


class DebateState(BaseModel):
    """
    State of the bull/bear debate for an opportunity.
    
    Contains both bull arguments advocating for growth and bear objections
    identifying risks, plus key conflicts that need resolution.
    """
    run_id: str = Field(description="Identifier of the run this debate belongs to")
    bull_arguments: list[BullArgument] = Field(
        default_factory=list, description="Bull arguments for growth"
    )
    bear_objections: list[BearObjection] = Field(
        default_factory=list, description="Bear objections identifying risks"
    )
    key_conflicts: list[KeyConflict] = Field(
        default_factory=list, description="Key conflicts between positions"
    )
    debate_summary: str = Field(
        description="High-level summary of the debate outcome"
    )
    net_sentiment: Literal["bullish", "neutral", "bearish"] = Field(
        default="neutral", description="Overall debate sentiment"
    )
    critical_issues_count: int = Field(
        default=0, description="Count of critical issues identified"
    )
    issues_requiring_resolution: list[str] = Field(
        default_factory=list, description="Conflict IDs that need resolution"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "2026-05-14-100000",
                "bull_arguments": [
                    {
                        "argument_id": "bull-1",
                        "opportunity_id": "opp-1",
                        "thesis_statement": "Summer promotion can drive 25% new customer acquisition",
                        "conviction_level": "high"
                    }
                ],
                "bear_objections": [
                    {
                        "objection_id": "bear-1",
                        "opportunity_id": "opp-1",
                        "objection_statement": "Margin compression risk exceeds acceptable threshold",
                        "impact_assessment": "critical"
                    }
                ],
                "key_conflicts": [
                    {
                        "conflict_id": "conflict-1",
                        "topic": "Margin vs. Growth tradeoff",
                        "bull_position": "Growth justifies 5% margin reduction",
                        "bear_position": "Margin protection is non-negotiable",
                        "resolution_status": "pending"
                    }
                ]
            }
        }
