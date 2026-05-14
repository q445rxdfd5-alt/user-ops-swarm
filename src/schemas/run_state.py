"""
Run State Schema

Master state tracking for the entire swarm run.
Contains run_id, status, current_step, and all artifacts produced.
"""

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class StepStatus(BaseModel):
    """Status of a single step in the workflow."""
    step_name: str = Field(description="Name of the workflow step")
    status: Literal["pending", "in_progress", "completed", "failed", "skipped"] = Field(
        default="pending", description="Current status of this step"
    )
    started_at: Optional[str] = Field(default=None, description="ISO timestamp when started")
    completed_at: Optional[str] = Field(default=None, description="ISO timestamp when completed")
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    agent_name: Optional[str] = Field(
        default=None, description="Agent that executed this step"
    )
    output_file: Optional[str] = Field(
        default=None, description="Path to output file if completed"
    )


class ArtifactReference(BaseModel):
    """Reference to an artifact produced during the run."""
    artifact_id: str = Field(description="Unique identifier for this artifact")
    artifact_type: Literal["context_summary", "opportunity_analysis", "debate_state",
                         "strategy_summary", "risk_review", "final_decision", 
                         "memory_candidate", "execution_plan", "other"] = Field(
        description="Type of artifact"
    )
    file_path: str = Field(description="Path to the artifact file")
    created_at: str = Field(description="ISO timestamp when created")
    status: Literal["draft", "validated", "final", "archived"] = Field(
        default="draft", description="Status of this artifact"
    )


class WorkflowProgress(BaseModel):
    """Progress tracking for the workflow."""
    current_step: str = Field(
        description="Name of the currently executing step"
    )
    completed_steps: list[str] = Field(
        default_factory=list, description="Names of completed steps"
    )
    pending_steps: list[str] = Field(
        default_factory=list, description="Names of pending steps"
    )
    failed_steps: list[str] = Field(
        default_factory=list, description="Names of failed steps"
    )
    step_details: list[StepStatus] = Field(
        default_factory=list, description="Detailed status of each step"
    )


class RunMetadata(BaseModel):
    """Metadata about the run."""
    input_file: str = Field(description="Path to input task file")
    context_file: str = Field(description="Path to context file used")
    memory_file: Optional[str] = Field(
        default=None, description="Path to memory file used"
    )
    output_directory: str = Field(description="Base directory for outputs")
    user: Optional[str] = Field(
        default=None, description="User who initiated the run"
    )
    model: Optional[str] = Field(
        default=None, description="Model used for agent execution"
    )


class ErrorInfo(BaseModel):
    """Information about an error that occurred."""
    step_name: str = Field(description="Step where error occurred")
    error_type: str = Field(description="Type/category of error")
    error_message: str = Field(description="Human-readable error message")
    timestamp: str = Field(description="ISO timestamp when error occurred")
    stack_trace: Optional[str] = Field(
        default=None, description="Stack trace if available"
    )
    recovery_action: Optional[str] = Field(
        default=None, description="Suggested recovery action"
    )


class RunState(BaseModel):
    """
    Master state for the entire User Ops Swarm run.
    
    Tracks run_id, status, current workflow step, and all artifacts produced.
    This state is persisted and updated throughout the run for auditability.
    """
    run_id: str = Field(description="Unique identifier for this run")
    status: Literal["initialized", "running", "paused", "completed", "failed", "cancelled"] = Field(
        default="initialized", description="Overall run status"
    )
    created_at: str = Field(description="ISO timestamp when run was created")
    updated_at: str = Field(description="ISO timestamp of last update")
    completed_at: Optional[str] = Field(
        default=None, description="ISO timestamp when run completed"
    )
    metadata: RunMetadata = Field(description="Run metadata")
    progress: WorkflowProgress = Field(description="Workflow progress tracking")
    artifacts: list[ArtifactReference] = Field(
        default_factory=list, description="All artifacts produced"
    )
    errors: list[ErrorInfo] = Field(
        default_factory=list, description="Errors encountered during run"
    )
    retry_count: int = Field(
        default=0, description="Number of times run has been retried"
    )
    parent_run_id: Optional[str] = Field(
        default=None, description="Parent run ID if this is a retry"
    )
    run_summary: Optional[str] = Field(
        default=None, description="High-level summary of run outcome"
    )
    decision_summary: Optional[dict] = Field(
        default=None, description="Summary of final decisions made"
    )
    memory_candidates_count: int = Field(
        default=0, description="Number of memory candidates generated"
    )

    def get_current_step_name(self) -> Optional[str]:
        """Get the name of the currently executing step."""
        return self.progress.current_step if self.progress else None

    def is_completed(self) -> bool:
        """Check if the run has completed (successfully or not)."""
        return self.status in ["completed", "failed", "cancelled"]

    def has_errors(self) -> bool:
        """Check if the run encountered any errors."""
        return len(self.errors) > 0

    def get_artifact(self, artifact_type: str) -> Optional[ArtifactReference]:
        """Get the most recent artifact of a specific type."""
        matching = [a for a in self.artifacts if a.artifact_type == artifact_type]
        return matching[-1] if matching else None

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "2026-05-14-100000",
                "status": "completed",
                "created_at": "2026-05-14T10:00:00Z",
                "updated_at": "2026-05-14T10:45:00Z",
                "completed_at": "2026-05-14T10:45:00Z",
                "metadata": {
                    "input_file": "examples/summer-new-product.md",
                    "context_file": "context/user_ops_context.md",
                    "output_directory": "runs/2026-05-14-100000"
                },
                "progress": {
                    "current_step": "memory_candidate",
                    "completed_steps": [
                        "context_loading",
                        "opportunity_analysis",
                        "bull_bear_debate",
                        "strategy_synthesis",
                        "risk_review",
                        "final_decision"
                    ],
                    "pending_steps": [],
                    "step_details": [
                        {
                            "step_name": "context_loading",
                            "status": "completed",
                            "started_at": "2026-05-14T10:00:05Z",
                            "completed_at": "2026-05-14T10:02:30Z",
                            "output_file": "runs/2026-05-14-100000/01_context_summary.md"
                        }
                    ]
                },
                "artifacts": [
                    {
                        "artifact_id": "art-1",
                        "artifact_type": "context_summary",
                        "file_path": "runs/2026-05-14-100000/01_context_summary.md",
                        "created_at": "2026-05-14T10:02:30Z",
                        "status": "validated"
                    }
                ],
                "decision_summary": {
                    "total_strategies": 3,
                    "approved": 2,
                    "revise": 1,
                    "rejected": 0,
                    "test_only": 0
                }
            }
        }
