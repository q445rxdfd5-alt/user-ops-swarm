#!/usr/bin/env python3
"""
User Ops Swarm for QSR — Entry Point

Usage:
    python main.py --input examples/summer-new-product.md
    python main.py --input <task-file.md> --run-id <custom-id> --context <context.md>

The swarm executes an 8-step workflow:
    1. Initialize run
    2. Load and synthesize context
    3. Opportunity analysis (User Scene + Channel analysts, in parallel)
    4. Bull vs. Bear debate (in parallel)
    5. Strategy synthesis (Manager absorbs both sides)
    6. Risk review (Reviewer may block)
    7. Director decision (approve / revise / reject / test-only)
    8. Reflection (memory candidate for human review)

All outputs are written to runs/<run_id>/.
"""

import argparse
import sys
from pathlib import Path

from src.flow import UserOpsFlow


def main() -> int:
    parser = argparse.ArgumentParser(
        description="User Ops Swarm for QSR — Phase 1 Prototype",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input examples/summer-new-product.md
  python main.py --input tasks/my-campaign.md --run-id summer-001
  python main.py --input tasks/my-campaign.md --context context/my-brand.md
        """,
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to the task input .md file",
    )
    parser.add_argument(
        "--context", "-c",
        type=str,
        default="context/user_ops_context.md",
        help="Path to context file (default: context/user_ops_context.md)",
    )
    parser.add_argument(
        "--memory", "-m",
        type=str,
        default="memory/memory_log.md",
        help="Path to memory log (default: memory/memory_log.md)",
    )
    parser.add_argument(
        "--run-id", "-r",
        type=str,
        default=None,
        help="Custom run ID (default: auto-generated)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate setup without executing the flow",
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}", file=sys.stderr)
        return 1

    ctx_path = Path(args.context)
    if not ctx_path.exists():
        print(f"[WARNING] Context file not found: {ctx_path} — continuing without it", file=sys.stderr)

    print("=" * 60)
    print("User Ops Swarm for QSR — Phase 1 Prototype")
    print("=" * 60)
    print(f"Input:    {input_path}")
    print(f"Context:  {ctx_path}")
    print(f"Memory:   {args.memory}")
    print(f"Run ID:   {args.run_id or '(auto-generated)'}")
    print("=" * 60)

    if args.dry_run:
        print("\n[dry-run] Setup validated. Exiting without running flow.")
        return 0

    flow = UserOpsFlow()
    try:
        result = flow.kickoff(
            inputs={
                "input_file": str(input_path),
                "context_file": str(ctx_path),
                "memory_file": args.memory,
                "run_id": args.run_id,
            }
        )
    except Exception as e:
        print(f"\n[ERROR] Flow failed: {e}", file=sys.stderr)
        return 1

    print()
    print("=" * 60)
    print("Run Complete")
    print("=" * 60)
    print(f"Run ID:   {result.run_id}")
    print(f"Status:   {result.status}")
    print(f"Output:   {result.run_dir}/")
    print(f"Risk:     {'BLOCKED' if not result.risk_approved else 'Approved by RiskReviewer'}")

    artifacts = [
        "01_context_summary.md",
        "02_opportunity_analysis.md",
        "03_bull_bear_debate.md",
        "04_strategy_summary.md",
        "05_risk_review.md",
        "06_final_decision.md",
        "07_memory_candidate.md",
    ]
    print("\nArtifacts:")
    for a in artifacts:
        path = Path(result.run_dir) / a
        status = "✓" if path.exists() else "✗"
        print(f"  [{status}] {a}")

    print()
    if result.error and result.status == "failed":
        print(f"[FAILED] {result.error}")
        return 1

    print("[SUCCESS] Swarm run completed. Review artifacts before approving memory candidates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
