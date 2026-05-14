#!/usr/bin/env python3
"""
Evaluation Harness for User Ops Swarm

Runs both a single-agent baseline and the full swarm on the same input,
then scores each output against the evaluation rubric.

Usage:
    python evaluations/run_evaluation.py --input examples/summer-new-product.md
    python evaluations/run_evaluation.py --input examples/summer-new-product.md --baseline-only
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
EVAL_DIR = PROJECT_ROOT / "evaluations"
RUBRIC_FILE = EVAL_DIR / "rubrics" / "evaluation_rubric.json"
BASELINES_DIR = EVAL_DIR / "baselines"
RUNS_DIR = PROJECT_ROOT / "runs"


def load_rubric() -> dict:
    with open(RUBRIC_FILE) as f:
        return json.load(f)


def score_dimension(dimension: dict, artifact_content: str, is_baseline: bool) -> int:
    """
    Score a single dimension based on artifact content.
    This is a heuristic scorer — for production, replace with LLM-as-judge.
    """
    content_lower = artifact_content.lower()

    dim_name = dimension["name"]

    if is_baseline:
        # Single agent: typically scores 1-3 on most dimensions
        if dim_name == "conflict_quality":
            return 1  # No conflict in single-agent
        elif dim_name == "reflection_reusability":
            return 2  # Single agents rarely produce structured reflection

    # Simple keyword-based scoring
    score = 2  # default

    if dim_name == "business_insight_depth":
        qs_terms = ["delivery commission", "fulfillment", "store capacity", "qsr", "quick service",
                    "margin floor", "coupon chaser", "redemption rate", "ltv", "cac"]
        matches = sum(1 for t in qs_terms if t in content_lower)
        score = min(5, 1 + matches)

    elif dim_name == "conflict_quality":
        conflict_terms = ["objection", "risk", "concern", "challenge", "however", "but",
                          "tension", "trade-off", "despite", "although"]
        bull_terms = ["growth", "opportunity", "acquisition", "upside", "leverage"]
        bear_terms = ["risk", "margin", "concern", "block", "modify"]
        has_conflict = sum(1 for t in conflict_terms if t in content_lower) >= 3
        has_bull = any(t in content_lower for t in bull_terms)
        has_bear = any(t in content_lower for t in bear_terms)
        if has_conflict and has_bull and has_bear:
            score = 4
        elif has_conflict:
            score = 3

    elif dim_name == "risk_identification_completeness":
        risk_dims = {
            "profit": ["margin", "gross", "cpa", "cost", "revenue"],
            "brand": ["brand", "positioning", "tone", "messaging"],
            "fulfillment": ["store", "capacity", "prep", "kitchen", "staff"],
            "platform": ["platform", "delivery", "algorithm", "compliance"],
            "member": ["member", "loyalty", "dormant", "ltv", "points"]
        }
        found_dims = sum(1 for d, terms in risk_dims.items()
                        if any(t in content_lower for t in terms))
        score = min(5, found_dims + 1)

    elif dim_name == "execution_actionability":
        action_terms = ["timeline", "channel", "owner", "metric", "target", "launch",
                        "deadline", "responsibility", "kpi", "budget"]
        matches = sum(1 for t in action_terms if t in content_lower)
        score = min(5, matches)

    elif dim_name == "decision_clarity":
        decision_terms = ["approve", "revise", "reject", "test-only", "decision",
                          "rationale", "because", "metric", "condition"]
        matches = sum(1 for t in decision_terms if t in content_lower)
        score = min(5, matches)

    elif dim_name == "reflection_reusability":
        reflection_terms = ["lesson", "reusable", "condition", "confidence",
                           "reuse", "next time", "if this happens"]
        matches = sum(1 for t in reflection_terms if t in content_lower)
        score = min(5, matches)

    return max(1, min(5, score))


def score_run(run_dir: Path, rubric: dict, is_baseline: bool) -> dict:
    """Score all artifacts in a run directory."""
    scores = {}
    total_weighted = 0.0
    total_weight = 0.0

    # Map dimensions to artifact files
    dim_to_artifact = {
        "business_insight_depth": ["02_opportunity_analysis.md", "03_bull_bear_debate.md"],
        "conflict_quality": ["03_bull_bear_debate.md"],
        "risk_identification_completeness": ["05_risk_review.md"],
        "execution_actionability": ["04_strategy_summary.md", "06_final_decision.md"],
        "decision_clarity": ["06_final_decision.md"],
        "reflection_reusability": ["07_memory_candidate.md"],
    }

    artifact_contents = {}
    for artifact_file in run_dir.glob("*.md"):
        artifact_contents[artifact_file.name] = artifact_file.read_text(encoding="utf-8")

    for dim in rubric["dimensions"]:
        dim_name = dim["name"]
        files = dim_to_artifact.get(dim_name, [])
        combined = " ".join(artifact_contents.get(f, "") for f in files)
        raw_score = score_dimension(dim, combined, is_baseline)
        weighted = raw_score * dim["weight"]
        total_weighted += weighted
        total_weight += dim["weight"]
        scores[dim_name] = {
            "raw_score": raw_score,
            "weight": dim["weight"],
            "weighted_score": weighted,
        }

    final_score = total_weighted / total_weight if total_weight > 0 else 0
    return {
        "dimensions": scores,
        "total_score": round(final_score, 2),
        "max_score": rubric["max_score"] / len(rubric["dimensions"]),
        "is_baseline": is_baseline,
    }


def run_swarm(input_file: str, run_id: str) -> Path:
    """Execute the full swarm on an input file."""
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py"),
         "--input", str(input_file),
         "--run-id", run_id],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    if result.returncode != 0:
        print(f"[EVAL ERROR] Swarm run failed: {result.stderr}", file=sys.stderr)
    run_dir = RUNS_DIR / run_id
    return run_dir


def generate_baseline(input_file: str, run_id: str) -> Path:
    """
    Generate a single-agent baseline output.
    In Phase 1, this runs a single Director agent with all context.
    """
    from crewai import Agent, Task, Crew

    # Use Ollama LLM
    try:
        from crewai import LLM
        llm = LLM(model="ollama/llama3.2", base_url="http://localhost:11434/v1")
    except Exception:
        llm = None

    # Read all inputs
    input_path = Path(input_file)
    context_path = PROJECT_ROOT / "context" / "user_ops_context.md"
    memory_path = PROJECT_ROOT / "memory" / "memory_log.md"

    input_content = input_path.read_text() if input_path.exists() else ""
    context_content = context_path.read_text() if context_path.exists() else ""
    memory_content = memory_path.read_text() if memory_path.exists() else ""

    combined_context = f"""# TASK INPUT
{input_content}

# BRAND CONTEXT
{context_content}

# MEMORY LOG
{memory_content}
"""

    # Single agent does everything
    director = Agent(
        role="User Operations Director",
        goal="Analyze the task and produce a complete user operations strategy, risk review, and decision in one pass.",
        backstory="You are a senior user operations director. You have full context. Generate a complete strategy without debate or deliberation.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    task = Task(
        description=combined_context + """

Generate a complete user operations strategy covering:
1. User segments and scenarios
2. Channel strategy
3. Growth recommendations
4. Risk assessment across 5 dimensions
5. Final decision (approve/revise/reject/test-only)
6. Memory candidate

Output all sections in detail.
""",
        expected_output="Full strategy, risk review, decision, and memory candidate",
        agent=director,
    )

    crew = Crew(agents=[director], tasks=[task], verbose=True)
    result = crew.kickoff()

    # Save to baseline directory
    run_dir = BASELINES_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "input.md").write_text(input_content, encoding="utf-8")
    (run_dir / "baseline_output.md").write_text(str(result), encoding="utf-8")
    (run_dir / "state.json").write_text(json.dumps({
        "run_id": run_id,
        "type": "single_agent_baseline",
        "timestamp": datetime.now().isoformat(),
    }, indent=2), encoding="utf-8")

    print(f"[BASELINE] Written to {run_dir}")
    return run_dir


def main():
    parser = argparse.ArgumentParser(description="User Ops Swarm Evaluation Harness")
    parser.add_argument("--input", type=str, required=True, help="Input task file")
    parser.add_argument("--run-id", type=str, default=None, help="Run ID prefix")
    parser.add_argument("--baseline-only", action="store_true", help="Only run baseline")
    parser.add_argument("--swarm-only", action="store_true", help="Only run swarm")
    args = parser.parse_args()

    run_prefix = args.run_id or datetime.now().strftime("%Y-%m-%d-%H%M%S")
    baseline_id = f"{run_prefix}-baseline"
    swarm_id = f"{run_prefix}-swarm"

    rubric = load_rubric()

    # Ensure directories exist
    BASELINES_DIR.mkdir(parents=True, exist_ok=True)
    (EVAL_DIR / "reports").mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("User Ops Swarm — Evaluation Harness")
    print("=" * 60)

    # Run baseline
    if not args.swarm_only:
        print(f"\n[1/2] Generating single-agent baseline...")
        baseline_dir = generate_baseline(args.input, baseline_id)
        baseline_scores = score_run(baseline_dir, rubric, is_baseline=True)
        print(f"[BASELINE SCORE] {baseline_scores['total_score']}")
    else:
        baseline_dir = BASELINES_DIR / baseline_id
        if not baseline_dir.exists():
            print("[ERROR] Baseline run not found. Run without --swarm-only first.")
            sys.exit(1)
        baseline_scores = score_run(baseline_dir, rubric, is_baseline=True)

    # Run swarm
    if not args.baseline_only:
        print(f"\n[2/2] Running swarm...")
        swarm_dir = run_swarm(args.input, swarm_id)
        if not swarm_dir.exists():
            print("[ERROR] Swarm run failed.", file=sys.stderr)
            sys.exit(1)
        swarm_scores = score_run(swarm_dir, rubric, is_baseline=False)
        print(f"[SWARM SCORE] {swarm_scores['total_score']}")
    else:
        swarm_scores = None

    # Compare
    print("\n" + "=" * 60)
    print("Evaluation Report")
    print("=" * 60)
    print(f"\n{'Dimension':<35} {'Baseline':>10} {'Swarm':>10} {'Δ':>8}")
    print("-" * 65)

    comparison = {}
    for dim in rubric["dimensions"]:
        name = dim["name"]
        b = baseline_scores["dimensions"][name]["raw_score"]
        s = swarm_scores["dimensions"][name]["raw_score"] if swarm_scores else "-"
        delta = s - b if swarm_scores else 0
        s_str = str(s) if swarm_scores else "-"
        comparison[name] = {"baseline": b, "swarm": s, "delta": delta}
        print(f"{name:<35} {b:>10} {s_str:>10} {delta:>+8}")

    print("-" * 65)
    b_total = baseline_scores["total_score"]
    s_total = swarm_scores["total_score"] if swarm_scores else 0
    delta_total = s_total - b_total if swarm_scores else 0
    print(f"{'TOTAL (weighted avg)':<35} {b_total:>10.2f} {s_total:>10.2f} {delta_total:>+8.2f}")

    if swarm_scores:
        passing = rubric["passing_score"]
        bonus = rubric["swarm_bonus_threshold"]
        print(f"\nPassing score: {passing}")
        print(f"Swarm bonus threshold: {bonus} pts above baseline")
        if s_total >= passing and delta_total >= bonus:
            print("✓ Swarm PASSES evaluation criteria")
        elif s_total >= passing:
            print("⚠ Swarm score is adequate but not sufficiently better than baseline")
        else:
            print("✗ Swarm does not meet minimum quality threshold")

    # Save report
    report = {
        "run_id": run_prefix,
        "timestamp": datetime.now().isoformat(),
        "input_file": args.input,
        "baseline": baseline_scores,
        "swarm": swarm_scores,
        "comparison": comparison,
    }
    report_file = EVAL_DIR / "reports" / f"{run_prefix}-report.json"
    report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport saved: {report_file}")


if __name__ == "__main__":
    main()
