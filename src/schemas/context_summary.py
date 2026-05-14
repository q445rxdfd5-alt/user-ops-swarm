"""
Context Summary Schema

Output from the Context Loader agent containing brand/channel/constraints/memory context.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class TaskClassification(BaseModel):
    """Classification of the input task type."""
    category: str = Field(description="Task category (e.g., new_product_launch, feature_request, market_expansion)")
    subcategory: Optional[str] = Field(default=None, description="More specific task subtype")
    priority: Literal["critical", "high", "medium", "low"] = Field(description="Task priority level")


class Objective(BaseModel):
    """A specific objective extracted from the input."""
    id: str = Field(description="Unique identifier for this objective")
    description: str = Field(description="Human-readable objective description")
    target_metric: Optional[str] = Field(default=None, description="Quantitative target if specified")
    timeline_weeks: Optional[int] = Field(default=None, description="Expected timeline in weeks")


class UserSegment(BaseModel):
    """A user segment mentioned in the input."""
    segment_id: str = Field(description="Unique identifier for this segment")
    name: str = Field(description="Segment name or description")
    size_estimate: Optional[str] = Field(default=None, description="Estimated segment size")
    source: Literal["explicit", "inferred"] = Field(description="Whether mentioned explicitly or inferred")


class BusinessConstraint(BaseModel):
    """A business constraint or requirement extracted from input."""
    constraint_id: str = Field(description="Unique identifier for this constraint")
    category: Literal["margin", "brand", "operational", "compliance", "timeline", "other"] = Field(
        description="Category of constraint"
    )
    description: str = Field(description="Human-readable constraint description")
    severity: Literal["hard", "soft"] = Field(description="Whether this is a hard or soft constraint")
    source: Optional[str] = Field(default=None, description="Source reference (context/memory/input)")


class ExternalReference(BaseModel):
    """An external file or URL referenced in the input."""
    reference_id: str = Field(description="Unique identifier for this reference")
    url_or_path: str = Field(description="URL or file path referenced")
    description: Optional[str] = Field(default=None, description="What this reference contains")
    status: Literal["pending", "verified", "unavailable"] = Field(
        default="pending", description="Verification status"
    )


class AmbiguityFlag(BaseModel):
    """An ambiguity or unclear section flagged for downstream clarification."""
    ambiguity_id: str = Field(description="Unique identifier for this ambiguity")
    location: str = Field(description="Where in the input this ambiguity appears")
    description: str = Field(description="Description of the ambiguity")
    impact: Literal["high", "medium", "low"] = Field(description="Potential impact if unresolved")
    suggestion: Optional[str] = Field(default=None, description="Suggested way to resolve")


class ContextSummary(BaseModel):
    """
    Structured context summary produced by the Context Loader agent.
    
    Consolidates input file content with brand context and historical memory
    to produce a unified context for downstream agents.
    """
    run_id: str = Field(description="Identifier of the run this context belongs to")
    task_classification: TaskClassification = Field(description="Classification of the input task")
    objectives: list[Objective] = Field(
        default_factory=list, description="Key objectives extracted from input"
    )
    target_segments: list[UserSegment] = Field(
        default_factory=list, description="User segments mentioned or inferred"
    )
    constraints: list[BusinessConstraint] = Field(
        default_factory=list, description="Business constraints and requirements"
    )
    success_criteria: Optional[list[str]] = Field(
        default=None, description="Success criteria if specified in input"
    )
    external_references: list[ExternalReference] = Field(
        default_factory=list, description="External files/URLs referenced"
    )
    ambiguities: list[AmbiguityFlag] = Field(
        default_factory=list, description="Ambiguities flagged for downstream clarification"
    )
    input_source: str = Field(description="Original input file path or content reference")
    context_source: str = Field(description="Brand context file used")
    memory_source: Optional[str] = Field(default=None, description="Historical memory file if used")
    confidence_score: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Confidence in context completeness"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "2026-05-14-100000",
                "task_classification": {
                    "category": "new_product_launch",
                    "subcategory": "seasonal_campaign",
                    "priority": "high"
                },
                "objectives": [
                    {
                        "id": "obj-1",
                        "description": "Drive 20% new customer acquisition",
                        "target_metric": "20%",
                        "timeline_weeks": 8
                    }
                ],
                "constraints": [
                    {
                        "constraint_id": "c-1",
                        "category": "margin",
                        "description": "Minimum gross margin of 40%",
                        "severity": "hard"
                    }
                ]
            }
        }
