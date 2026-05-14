"""
Memory Candidate Schema

Output from the Reflection Agent containing insights extracted for potential memory preservation.
Documents scenario, segment, channel, offer, lesson, and reuse conditions for each candidate.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class EvidenceReference(BaseModel):
    """Reference to specific outputs that support an insight."""
    output_type: Literal["context_summary", "opportunity_analysis", "debate_state",
                        "strategy_summary", "risk_review", "final_decision"] = Field(
        description="Type of output this evidence comes from"
    )
    output_id: str = Field(description="Reference to the specific output file/section")
    specific_evidence: str = Field(
        description="Specific evidence from this output"
    )


class ReuseCondition(BaseModel):
    """Conditions under which this insight should be reused."""
    applicable_scenarios: list[str] = Field(
        default_factory=list, description="Scenarios where this insight applies"
    )
    segment_conditions: list[str] = Field(
        default_factory=list, description="Segment conditions for reuse"
    )
    channel_conditions: list[str] = Field(
        default_factory=list, description="Channel conditions for reuse"
    )
    seasonal_conditions: Optional[list[str]] = Field(
        default=None, description="Seasonal conditions for reuse"
    )
    contraindication: Optional[list[str]] = Field(
        default=None, description="Conditions where this should NOT be applied"
    )


class MemoryCandidate(BaseModel):
    """
    A single candidate insight extracted for potential memory preservation.
    
    Extracted from completed deliberation records. These are candidates only
    and require external validation before being written to the knowledge base.
    """
    candidate_id: str = Field(description="Unique identifier for this candidate")
    insight_type: Literal["strategic_pattern", "market_insight", "user_behavior",
                        "team_effectiveness", "process_improvement", "risk_lesson"] = Field(
        description="Type of insight"
    )
    insight_content: str = Field(
        description="The learning or observation in natural language"
    )
    scenario: Optional[str] = Field(
        default=None, description="The scenario context this insight emerged from"
    )
    segment: Optional[str] = Field(
        default=None, description="User segment this insight relates to"
    )
    channel: Optional[str] = Field(
        default=None, description="Channel this insight relates to"
    )
    offer: Optional[str] = Field(
        default=None, description="Offer/promotion this insight relates to"
    )
    lesson: Optional[str] = Field(
        default=None, description="Specific lesson learned"
    )
    evidence_basis: list[EvidenceReference] = Field(
        default_factory=list, description="References supporting this insight"
    )
    preservation_priority: Literal["high", "medium", "low"] = Field(
        default="medium", description="Priority for memory preservation"
    )
    tags: list[str] = Field(
        default_factory=list, description="Categorization tags for retrieval"
    )
    reuse_conditions: Optional[ReuseCondition] = Field(
        default=None, description="Conditions for reusing this insight"
    )
    memory_status: Literal["pending_review", "approved", "rejected", "archived"] = Field(
        default="pending_review", description="Current status in memory workflow"
    )
    source_decision_id: Optional[str] = Field(
        default=None, description="Decision ID this was extracted from"
    )


class MemorySummary(BaseModel):
    """Summary of all memory candidates identified."""
    total_candidates: int = Field(
        default=0, description="Total candidates identified"
    )
    high_priority_count: int = Field(
        default=0, description="Count of high-priority candidates"
    )
    candidates_by_type: dict[str, int] = Field(
        default_factory=dict, description="Count of candidates by insight type"
    )
    recommended_integration: str = Field(
        description="Recommended approach for memory integration"
    )


class MemoryCandidatesReport(BaseModel):
    """
    Complete memory candidates report for the run.
    
    Produced by the Reflection Agent from the Director's final decisions.
    Contains candidate insights that require external validation before
    being written to the organization's knowledge base.
    """
    run_id: str = Field(description="Identifier of the run this report belongs to")
    candidates: list[MemoryCandidate] = Field(
        default_factory=list, description="All memory candidates identified"
    )
    summary: MemorySummary = Field(description="Summary statistics")
    extraction_timestamp: str = Field(
        description="ISO timestamp of extraction"
    )
    extraction_notes: Optional[str] = Field(
        default=None, description="Notes on the extraction process"
    )
    validation_required: bool = Field(
        default=True, description="Whether external validation is required"
    )
    validation_instructions: str = Field(
        default="Human review required before writing to memory.",
        description="Instructions for memory validation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "2026-05-14-100000",
                "candidates": [
                    {
                        "candidate_id": "mem-1",
                        "insight_type": "risk_lesson",
                        "insight_content": "Summer promotions requiring store fulfillment beyond 50 orders/hour lead to quality complaints",
                        "scenario": "summer_new_product_launch",
                        "segment": "all_segments",
                        "lesson": "Capacity limits must be modeled before campaign launch",
                        "evidence_basis": [
                            {
                                "output_type": "risk_review",
                                "output_id": "review-1",
                                "specific_evidence": "Operational risk score 8.5 exceeded threshold"
                            }
                        ],
                        "preservation_priority": "high",
                        "tags": ["capacity", "fulfillment", "summer", "quality"],
                        "reuse_conditions": {
                            "applicable_scenarios": ["high_volume_campaigns"],
                            "contrainidication": ["low_volume_rollout"]
                        }
                    }
                ],
                "summary": {
                    "total_candidates": 5,
                    "high_priority_count": 2,
                    "candidates_by_type": {
                        "risk_lesson": 2,
                        "strategic_pattern": 1,
                        "user_behavior": 2
                    },
                    "recommended_integration": "Write high-priority candidates to memory_log.md with priority flag"
                }
            }
        }
