#!/usr/bin/env python3
"""
User Ops Swarm for QSR — Main Entry Point

Usage:
    python main.py --input examples/summer-new-product.md
    python main.py --input <your-task-file.md> --run-id <custom-id>
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml


def main():
    parser = argparse.ArgumentParser(description="User Ops Swarm for QSR")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to input task file (.md)",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Custom run identifier (default: auto-generated)",
    )
    parser.add_argument(
        "--context",
        type=str,
        default="context/user_ops_context.md",
        help="Path to context file",
    )
    parser.add_argument(
        "--memory",
        type=str,
        default="memory/memory_log.md",
        help="Path to memory log file",
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Generate run ID
    run_id = args.run_id or f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"

    print(f"Starting run: {run_id}")
    print(f"Input: {input_path}")
    print()
    print("User Ops Swarm for QSR — Prototype v0.1")
    print("=" * 50)
    print()
    print("This is a CrewAI-based agent swarm prototype.")
    print("Full implementation coming in Phase 1.")
    print()
    print(f"Run ID: {run_id}")
    print(f"Status: Ready")

    # Create run directory
    run_dir = Path("runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Initialize state
    state = {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(),
        "input_file": str(input_path),
        "status": "initialized",
    }

    # Write initial state
    state_file = run_dir / "state.json"
    state_file.write_text(json.dumps(state, indent=2))
    print(f"State file: {state_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
