"""
Opportunity Analysis Schema

Output from parallel User Scene Analyst and Channel Analyst agents.
Contains user segments analysis and channel effectiveness evaluation.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class PainPoint(BaseModel):
    """A user pain point identified in scene analysis."""
    pain_id: str = Field(description="Unique identifier for this pain point")
    description: str = Field(description="Human-readable pain point description")
    severity: Literal["critical", "high", "medium", "low"] = Field(description="Impact severity")
    frequency: Literal["constant", "frequent", "occasional", "rare"] = Field(
        description="How often this pain occurs"
    )
    evidence_source: Optional[str] = Field(default=None, description="Source of evidence")
    assumption_flag: bool = Field(default=False, description="Whether this is an inferred assumption")


class UserSceneAnalysis(BaseModel):
    """Analysis output from the User Scene Analyst agent."""
    scene_id: str = Field(description="Unique identifier for this scene")
    problem_statement: str = Field(description="Core problem being addressed")
    user_segments: list[str] = Field(
        default_factory=list, description="List of user segment IDs affected"
    )
    pain_points: list[PainPoint] = Field(
        default_factory=list, description="Identified pain points with severity"
    )
    confidence_level: Literal["very_high", "high", "medium", "low"] = Field(
        description="Confidence in scene analysis"
    )
    flagged_assumptions: list[str] = Field(
        default_factory=list, description="Explicitly flagged assumptions"
    )


class ChannelMetrics(BaseModel):
    """Performance metrics for a channel."""
    reach: Optional[str] = Field(default=None, description="Estimated reach")
    conversion_rate: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Conversion rate as decimal"
    )
    cac: Optional[str] = Field(default=None, description="Customer acquisition cost")
    ltv: Optional[str] = Field(default=None, description="Lifetime value estimate")
    roi: Optional[str] = Field(default=None, description="Return on investment")
    organic_vs_paid: Literal["organic", "paid", "mixed"] = Field(
        default="mixed", description="Channel traffic mix"
    )


class ChannelAnalysisEntry(BaseModel):
    """Analysis for a single channel."""
    channel_id: str = Field(description="Unique identifier for this channel")
    channel_name: str = Field(description="Human-readable channel name")
    channel_type: Literal["social", "search", "display", "email", "delivery_platform", 
                          "group_buying", "membership", "in_store", "other"] = Field(
        description="Type of channel"
    )
    target_segments: list[str] = Field(
        default_factory=list, description="Segment IDs most likely to convert"
    )
    metrics: ChannelMetrics = Field(description="Channel performance metrics")
    fit_score: float = Field(default=5.0, ge=0.0, le=10.0, description="Fit score with objective")
    risks: list[str] = Field(default_factory=list, description="Channel-specific risks")
    recommendations: list[str] = Field(
        default_factory=list, description="Channel-specific recommendations"
    )


class ChannelAnalysis(BaseModel):
    """Analysis output from the Channel Analyst agent."""
    channels: list[ChannelAnalysisEntry] = Field(
        default_factory=list, description="Analysis for each channel evaluated"
    )
    priority_channels: list[str] = Field(
        default_factory=list, description="Channel IDs ranked by priority"
    )


class OpportunityAnalysis(BaseModel):
    """
    Combined opportunity analysis from parallel User Scene and Channel analysis.
    
    Produced by the opportunity_analysis CREW containing outputs from both
    UserSceneAnalyst and ChannelAnalyst agents working in parallel.
    """
    run_id: str = Field(description="Identifier of the run this analysis belongs to")
    user_scene: UserSceneAnalysis = Field(description="User scene analysis output")
    channel_analysis: ChannelAnalysis = Field(description="Channel analysis output")
    total_opportunities_identified: int = Field(
        default=0, description="Count of opportunities surfaced"
    )
    high_priority_opportunities: list[str] = Field(
        default_factory=list, description="Opportunity IDs with highest potential"
    )
    cross_segment_opportunities: list[str] = Field(
        default_factory=list, description="Opportunities targeting multiple segments"
    )
    confidence_score: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Confidence in analysis completeness"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "2026-05-14-100000",
                "user_scene": {
                    "scene_id": "scene-1",
                    "problem_statement": "New customers not aware of summer products",
                    "pain_points": [
                        {
                            "pain_id": "pp-1",
                            "description": "Low awareness among Gen Z",
                            "severity": "high",
                            "frequency": "frequent"
                        }
                    ]
                },
                "channel_analysis": {
                    "channels": [
                        {
                            "channel_id": "ch-1",
                            "channel_name": "Xiaohongshu",
                            "channel_type": "social",
                            "fit_score": 8.5
                        }
                    ]
                }
            }
        }
