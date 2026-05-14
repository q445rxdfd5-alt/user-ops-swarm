"""
User Ops Swarm Utilities

Utility functions for YAML loading, state persistence, artifact management,
and agent/task creation from YAML definitions.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

import yaml
from pydantic import BaseModel, ValidationError

from src.schemas import RunState, StepStatus, ArtifactReference


# ============================================================================
# Path Configuration
# ============================================================================

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_runs_dir(run_id: Optional[str] = None) -> Path:
    """Get the runs directory, optionally with a specific run_id subdirectory."""
    runs_dir = get_project_root() / "runs"
    if run_id:
        return runs_dir / run_id
    return runs_dir


# ============================================================================
# Run ID and Directory Management
# ============================================================================

def generate_run_id() -> str:
    """Generate a unique run ID based on timestamp and UUID."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}-{unique_id}"


def ensure_run_directory(run_id: str) -> Path:
    """Ensure the run directory exists and return its path."""
    run_dir = get_runs_dir(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


# ============================================================================
# YAML Loading
# ============================================================================

def load_yaml(file_path: Union[str, Path]) -> dict[str, Any]:
    """
    Load and parse a YAML file.

    Args:
        file_path: Path to the YAML file

    Returns:
        Parsed YAML content as a dictionary

    Raises:
        FileNotFoundError: If the file doesn't exist
        yaml.YAMLError: If the YAML is invalid
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_agent_yaml(agent_name: str) -> dict[str, Any]:
    """
    Load an agent definition from YAML.

    Args:
        agent_name: Name of the agent (e.g., "growth_bull_agent" -> growth_bull_agent.yaml)

    Returns:
        Agent definition as a dictionary
    """
    agents_dir = get_project_root() / "src" / "agents"
    # Convert agent name to filename: GrowthBullAgent -> growth_bull_agent
    filename = f"{agent_name.lower().replace('_agent', '_agent')}.yaml"
    return load_yaml(agents_dir / filename)


def load_task_yaml(task_name: str) -> dict[str, Any]:
    """
    Load a task definition from YAML.

    Args:
        task_name: Name of the task (e.g., "context_loading" -> context_loading.yaml)

    Returns:
        Task definition as a dictionary
    """
    tasks_dir = get_project_root() / "src" / "tasks"
    filename = f"{task_name.lower()}.yaml"
    return load_yaml(tasks_dir / filename)


# ============================================================================
# Agent and Task Creation
# ============================================================================

def create_agent_from_yaml(
    yaml_def: dict[str, Any],
    tools: Optional[list[Any]] = None,
    llm: Optional[Any] = None,
) -> Any:
    """
    Create a CrewAI Agent from a YAML definition.

    Args:
        yaml_def: Agent definition from YAML
        tools: Optional list of tools to attach to the agent
        llm: Optional LLM instance to use

    Returns:
        CrewAI Agent instance
    """
    from crewai import Agent

    agent_config = {
        "role": yaml_def.get("role", "Agent"),
        "goal": yaml_def.get("goal", ""),
        "backstory": yaml_def.get("backstory", ""),
        "verbose": yaml_def.get("verbose", True),
        "allow_delegation": yaml_def.get("allow_delegation", False),
    }

    if tools:
        agent_config["tools"] = tools
    if llm:
        agent_config["llm"] = llm

    return Agent(**agent_config)


def create_task_from_yaml(
    yaml_def: dict[str, Any],
    agent: Any,
    output_file: Optional[str] = None,
    context: Optional[list[Any]] = None,
) -> Any:
    """
    Create a CrewAI Task from a YAML definition.

    Args:
        yaml_def: Task definition from YAML
        agent: CrewAI Agent to assign to this task
        output_file: Optional output file path (overrides YAML)
        context: Optional list of context tasks

    Returns:
        CrewAI Task instance
    """
    from crewai import Task

    task_config = {
        "description": yaml_def.get("description", ""),
        "expected_output": yaml_def.get("expected_output", ""),
        "agent": agent,
    }

    if output_file:
        task_config["output_file"] = output_file
    elif yaml_def.get("output_file"):
        task_config["output_file"] = yaml_def.get("output_file")

    if context:
        task_config["context"] = context

    return Task(**task_config)


# ============================================================================
# State Persistence
# ============================================================================

def save_state(run_state: RunState, run_id: Optional[str] = None) -> Path:
    """
    Save the run state to state.json.

    Args:
        run_state: RunState instance to save
        run_id: Optional run ID (uses run_state.run_id if not provided)

    Returns:
        Path to the saved state file
    """
    if run_id is None:
        run_id = run_state.run_id

    run_dir = ensure_run_directory(run_id)
    state_file = run_dir / "state.json"

    # Update timestamps
    run_state.updated_at = datetime.now().isoformat()
    if run_state.status == "completed" and not run_state.completed_at:
        run_state.completed_at = datetime.now().isoformat()

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(run_state.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    return state_file


def load_state(run_id: str) -> Optional[RunState]:
    """
    Load run state from state.json.

    Args:
        run_id: Run ID to load state for

    Returns:
        RunState instance if found, None otherwise
    """
    state_file = get_runs_dir(run_id) / "state.json"
    if not state_file.exists():
        return None

    with open(state_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return RunState.model_validate(data)


def update_step_status(
    run_state: RunState,
    step_name: str,
    status: str,
    agent_name: Optional[str] = None,
    output_file: Optional[str] = None,
    error_message: Optional[str] = None,
) -> RunState:
    """
    Update the status of a workflow step in the run state.

    Args:
        run_state: Current run state
        step_name: Name of the step to update
        status: New status (pending, in_progress, completed, failed, skipped)
        agent_name: Optional agent that executed this step
        output_file: Optional path to output file
        error_message: Optional error message if failed

    Returns:
        Updated RunState instance
    """
    now = datetime.now().isoformat()

    # Find or create step status
    step_status = None
    for s in run_state.progress.step_details:
        if s.step_name == step_name:
            step_status = s
            break

    if step_status is None:
        step_status = StepStatus(step_name=step_name)
        run_state.progress.step_details.append(step_status)

    step_status.status = status
    step_status.agent_name = agent_name

    if status == "in_progress":
        step_status.started_at = now
    elif status == "completed":
        step_status.completed_at = now
        step_status.output_file = output_file
        if step_name not in run_state.progress.completed_steps:
            run_state.progress.completed_steps.append(step_name)
        if step_name in run_state.progress.pending_steps:
            run_state.progress.pending_steps.remove(step_name)
    elif status == "failed":
        step_status.completed_at = now
        step_status.error_message = error_message
        run_state.progress.failed_steps.append(step_name)

    # Update current step
    run_state.progress.current_step = step_name

    return run_state


# ============================================================================
# Artifact Management
# ============================================================================

def save_artifact(
    run_id: str,
    content: str,
    filename: str,
    artifact_type: str,
    status: str = "draft",
) -> ArtifactReference:
    """
    Save an artifact and create an ArtifactReference.

    Args:
        run_id: Run ID
        content: Content to save
        filename: Filename for the artifact
        artifact_type: Type of artifact
        status: Status of the artifact (draft, validated, final, archived)

    Returns:
        ArtifactReference instance
    """
    run_dir = ensure_run_directory(run_id)
    file_path = run_dir / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    artifact = ArtifactReference(
        artifact_id=f"art-{uuid.uuid4().hex[:8]}",
        artifact_type=artifact_type,
        file_path=str(file_path),
        created_at=datetime.now().isoformat(),
        status=status,
    )

    return artifact


def save_artifact_from_data(
    run_id: str,
    data: dict[str, Any],
    filename: str,
    artifact_type: str,
    status: str = "draft",
) -> ArtifactReference:
    """
    Save an artifact from a dictionary and create an ArtifactReference.

    Args:
        run_id: Run ID
        data: Data to save as JSON
        filename: Filename for the artifact
        artifact_type: Type of artifact
        status: Status of the artifact

    Returns:
        ArtifactReference instance
    """
    content = json.dumps(data, indent=2, ensure_ascii=False)
    return save_artifact(run_id, content, filename, artifact_type, status)


def load_artifact(run_id: str, filename: str) -> Optional[str]:
    """
    Load an artifact's content.

    Args:
        run_id: Run ID
        filename: Filename to load

    Returns:
        Content of the artifact, or None if not found
    """
    file_path = get_runs_dir(run_id) / filename
    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_artifact_json(run_id: str, filename: str) -> Optional[dict[str, Any]]:
    """
    Load an artifact's content as JSON.

    Args:
        run_id: Run ID
        filename: Filename to load

    Returns:
        Parsed JSON content, or None if not found/invalid
    """
    content = load_artifact(run_id, filename)
    if content is None:
        return None

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


# ============================================================================
# Schema Validation
# ============================================================================

def validate_schema(
    data: dict[str, Any],
    schema_class: type[BaseModel],
    step_name: Optional[str] = None,
) -> BaseModel:
    """
    Validate data against a Pydantic schema.

    Args:
        data: Data to validate
        schema_class: Pydantic model class
        step_name: Optional step name for error messages

    Returns:
        Validated schema instance

    Raises:
        ValidationError: If validation fails
    """
    try:
        return schema_class.model_validate(data)
    except ValidationError as e:
        error_msg = f"Validation error in {step_name or 'unknown step'}: {e}"
        raise ValidationError(error_msg) from e


def parse_json_from_text(text: str) -> Optional[dict[str, Any]]:
    """
    Extract and parse JSON from text that may contain surrounding content.

    Args:
        text: Text containing JSON

    Returns:
        Parsed JSON dict, or None if parsing fails
    """
    import re

    # Try to find JSON in the text
    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Try parsing the whole text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


# ============================================================================
# Run Initialization
# ============================================================================

def initialize_run(
    run_id: Optional[str] = None,
    input_file: Optional[str] = None,
    context_file: str = "context/user_ops_context.md",
    memory_file: Optional[str] = None,
    user: Optional[str] = None,
) -> RunState:
    """
    Initialize a new run with the given parameters.

    Args:
        run_id: Optional custom run ID
        input_file: Path to input task file
        context_file: Path to context file
        memory_file: Optional path to memory log file
        user: Optional user who initiated the run

    Returns:
        Initialized RunState instance
    """
    if run_id is None:
        run_id = generate_run_id()

    # Ensure run directory exists
    run_dir = ensure_run_directory(run_id)

    # Define workflow steps
    steps = [
        "initialize",
        "load_context",
        "opportunity_analysis",
        "bull_bear_debate",
        "strategy_manager",
        "risk_review",
        "director_decision",
        "reflection",
    ]

    # Create initial step statuses
    step_details = [StepStatus(step_name=step) for step in steps]

    # Mark initialize as completed
    step_details[0].status = "completed"
    step_details[0].completed_at = datetime.now().isoformat()

    run_state = RunState(
        run_id=run_id,
        status="initialized",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        metadata={
            "input_file": input_file or "",
            "context_file": context_file,
            "memory_file": memory_file,
            "output_directory": str(run_dir),
            "user": user,
        },
        progress={
            "current_step": "initialize",
            "completed_steps": ["initialize"],
            "pending_steps": steps[1:],  # All except initialize
            "step_details": step_details,
        },
    )

    # Save initial state
    save_state(run_state)

    return run_state
