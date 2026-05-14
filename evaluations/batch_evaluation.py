#!/usr/bin/env python3
"""
Batch Evaluation Harness for User Ops Swarm

Runs multiple stress-test scenarios sequentially (baseline + swarm for each),
aggregates results, and generates a comparative batch report.

Usage:
    python evaluations/batch_evaluation.py
    python evaluations/batch_evaluation.py --cases st-001 st-002
    python evaluations/batch_evaluation.py --swarm-only  # skip baselines (faster retest)
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import os

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
EVAL_DIR = PROJECT_ROOT / "evaluations"
RUBRIC_FILE = EVAL_DIR / "rubrics" / "evaluation_rubric.json"
BASELINES_DIR = EVAL_DIR / "baselines"
RUNS_DIR = PROJECT_ROOT / "runs"
CASES_DIR = PROJECT_ROOT / "examples" / "stress-tests"
STRESS_TESTS_DIR = PROJECT_ROOT / "examples" / "stress-tests"
REPORTS_DIR = EVAL_DIR / "reports"
BATCH_DIR = REPORTS_DIR / "batches"


def load_rubric() -> dict:
    with open(RUBRIC_FILE) as f:
        return json.load(f)


def score_dimension(dimension: dict, artifact_content: str, is_baseline: bool) -> int:
    """Keyword-based heuristic scorer — matches the same logic in run_evaluation.py."""
    content_lower = artifact_content.lower()
    dim_name = dimension["name"]

    if is_baseline:
        if dim_name == "conflict_quality":
            return 1
        elif dim_name == "reflection_reusability":
            return 2

    score = 2

    if dim_name == "business_insight_depth":
        qs_terms = ["delivery commission", "fulfillment", "store capacity", "qsr", "quick service",
                    "margin floor", "coupon chaser", "redemption rate", "ltv", "cac",
                    "dormant", "reactivation", "campus", "dormancy", "ranking", "fulfillment"]
        matches = sum(1 for t in qs_terms if t in content_lower)
        score = min(5, 1 + matches)

    elif dim_name == "conflict_quality":
        conflict_terms = ["objection", "risk", "concern", "challenge", "however", "but",
                          "tension", "trade-off", "despite", "although", "whereas", "on the other hand"]
        bull_terms = ["growth", "opportunity", "acquisition", "upside", "leverage", "expand"]
        bear_terms = ["risk", "margin", "concern", "block", "modify", "caution", "slow"]
        has_conflict = sum(1 for t in conflict_terms if t in content_lower) >= 3
        has_bull = any(t in content_lower for t in bull_terms)
        has_bear = any(t in content_lower for t in bear_terms)
        if has_conflict and has_bull and has_bear:
            score = 4
        elif has_conflict:
            score = 3

    elif dim_name == "risk_identification_completeness":
        risk_dims = {
            "profit": ["margin", "gross", "cpa", "cost", "revenue", "budget"],
            "brand": ["brand", "positioning", "tone", "messaging", "reputation", "crisis"],
            "fulfillment": ["store", "capacity", "prep", "kitchen", "staff", "kitchen"],
            "platform": ["platform", "delivery", "algorithm", "compliance", "ranking", "meituan", "ele.me"],
            "member": ["member", "loyalty", "dormant", "ltv", "points", "reactivation"]
        }
        found_dims = sum(1 for d, terms in risk_dims.items()
                        if any(t in content_lower for t in terms))
        score = min(5, found_dims + 1)

    elif dim_name == "execution_actionability":
        action_terms = ["timeline", "channel", "owner", "metric", "target", "launch",
                        "deadline", "responsibility", "kpi", "budget", "day", "week",
                        "responsible", "assign", "measure", "monitor", "track", "review"]
        matches = sum(1 for t in action_terms if t in content_lower)
        score = min(5, matches)

    elif dim_name == "decision_clarity":
        decision_terms = ["approve", "revise", "reject", "test-only", "decision",
                          "rationale", "because", "metric", "condition", "if", "when",
                          "recommend", "proceed", "not proceed", "conclusion"]
        matches = sum(1 for t in decision_terms if t in content_lower)
        score = min(5, matches)

    elif dim_name == "reflection_reusability":
        reflection_terms = ["lesson", "reusable", "condition", "confidence",
                           "reuse", "next time", "if this happens", "trigger", "pattern",
                           "similar situation", "apply this"]
        matches = sum(1 for t in reflection_terms if t in content_lower)
        score = min(5, matches)

    return max(1, min(5, score))


def score_run(run_dir: Path, rubric: dict, is_baseline: bool) -> dict:
    """Score all artifacts in a run directory."""
    scores = {}
    total_weighted = 0.0
    total_weight = 0.0

    dim_to_artifact = {
        "business_insight_depth": ["02_opportunity_analysis.md", "03_bull_bear_debate.md"],
        "conflict_quality": ["03_bull_bear_debate.md"],
        "risk_identification_completeness": ["06_risk_review.md"],
        "execution_actionability": ["04_strategy_summary.md", "05_execution_plan.md", "07_final_decision.md"],
        "decision_clarity": ["07_final_decision.md"],
        "reflection_reusability": ["08_memory_candidate.md"],
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
        "is_baseline": is_baseline,
    }


def run_swarm(input_file: str, run_id: str) -> Path:
    """Execute the full swarm on an input file."""
    print(f"  → Running swarm...")
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py"),
         "--input", str(input_file),
         "--run-id", run_id],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    if result.returncode != 0:
        print(f"  [WARN] Swarm run {run_id} returned non-zero: {result.stderr[:200]}", file=sys.stderr)
    run_dir = RUNS_DIR / run_id
    return run_dir


def generate_baseline(input_file: str, run_id: str) -> Path:
    """Generate a single-agent baseline output."""
    from crewai import Agent, Task, Crew

    # Use MiniMax M2.5 if available, else Ollama fallback
    llm = None
    try:
        from crewai import LLM
        # Try MiniMax first
        try:
            llm = LLM(
                model="MiniMax-M2.1",
                base_url=os.environ.get("MINIMAX_BASE_URL", "https://api.minimax.chat/v1"),
                api_key=os.environ.get("MINIMAX_API_KEY", ""),
            )
        except Exception:
            # Fall back to Ollama
            llm = LLM(model="ollama/llama3.2", base_url="http://localhost:11434/v1")
    except Exception:
        pass

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

    director = Agent(
        role="User Operations Director",
        goal="Analyze the task and produce a complete user operations strategy, risk review, and decision in one pass.",
        backstory="You are a senior user operations director. You have full context. Generate a complete strategy without debate or deliberation.",
        verbose=False,
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

    crew = Crew(agents=[director], tasks=[task], verbose=False)
    result = crew.kickoff()

    run_dir = BASELINES_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "input.md").write_text(input_content, encoding="utf-8")
    (run_dir / "baseline_output.md").write_text(str(result), encoding="utf-8")
    (run_dir / "state.json").write_text(json.dumps({
        "run_id": run_id,
        "type": "single_agent_baseline",
        "timestamp": datetime.now().isoformat(),
    }, indent=2), encoding="utf-8")

    print(f"  ✓ Baseline written to {run_dir}")
    return run_dir


def run_case(case_id: str, case_file: Path, rubric: dict, swarm_only: bool, baseline_only: bool) -> dict:
    """Run a single test case: baseline + swarm, then score both."""
    print(f"\n{'='*60}")
    print(f"  Case: {case_id}")
    print(f"  Input: {case_file}")
    print(f"{'='*60}")

    run_prefix = f"batch-{datetime.now().strftime('%m%d')}-{case_id}"
    baseline_id = f"{run_prefix}-baseline"
    swarm_id = f"{run_prefix}-swarm"

    BASELINES_DIR.mkdir(parents=True, exist_ok=True)
    BATCH_DIR.mkdir(parents=True, exist_ok=True)

    # Baseline
    if not swarm_only:
        baseline_dir = generate_baseline(str(case_file), baseline_id)
        baseline_scores = score_run(baseline_dir, rubric, is_baseline=True)
        print(f"  Baseline score: {baseline_scores['total_score']:.2f}/5")
    else:
        baseline_dir = BASELINES_DIR / baseline_id
        if baseline_dir.exists():
            baseline_scores = score_run(baseline_dir, rubric, is_baseline=True)
            print(f"  Baseline score (cached): {baseline_scores['total_score']:.2f}/5")
        else:
            print("  [WARN] Baseline not found. Run without --swarm-only first.")
            baseline_scores = None

    # Swarm
    if not baseline_only:
        swarm_dir = run_swarm(str(case_file), swarm_id)
        if swarm_dir.exists():
            swarm_scores = score_run(swarm_dir, rubric, is_baseline=False)
            print(f"  Swarm score:   {swarm_scores['total_score']:.2f}/5")
        else:
            print("  [ERROR] Swarm run failed.")
            swarm_scores = None
    else:
        swarm_scores = None

    # Per-dimension comparison
    print(f"\n  {'Dimension':<35} {'Baseline':>10} {'Swarm':>10} {'Δ':>8}")
    print(f"  {'-'*65}")

    dim_results = {}
    for dim in rubric["dimensions"]:
        name = dim["name"]
        b = baseline_scores["dimensions"][name]["raw_score"] if baseline_scores else 0
        s = swarm_scores["dimensions"][name]["raw_score"] if swarm_scores else 0
        delta = s - b if (baseline_scores and swarm_scores) else 0
        dim_results[name] = {"baseline": b, "swarm": s, "delta": delta}
        b_str = f"{b:.0f}" if b else "—"
        s_str = f"{s:.0f}" if s else "—"
        print(f"  {name:<35} {b_str:>10} {s_str:>10} {delta:>+8}")

    total_b = baseline_scores["total_score"] if baseline_scores else 0
    total_s = swarm_scores["total_score"] if swarm_scores else 0
    total_delta = total_s - total_b if (baseline_scores and swarm_scores) else 0
    print(f"  {'-'*65}")
    print(f"  {'TOTAL (weighted avg)':<35} {total_b:>10.2f} {total_s:>10.2f} {total_delta:>+8.2f}")

    passing_normalized = rubric["passing_score"] / len(rubric["dimensions"])
    pass_mark = "✓ PASS" if total_s >= passing_normalized else "✗ FAIL"
    print(f"  Passing threshold: {passing_normalized:.2f}/5 → {pass_mark}")

    return {
        "case_id": case_id,
        "input_file": str(case_file),
        "baseline": baseline_scores,
        "swarm": swarm_scores,
        "comparison": dim_results,
        "total_baseline": total_b,
        "total_swarm": total_s,
        "total_delta": total_delta,
        "passing_normalized": passing_normalized,
        "pass": total_s >= passing_normalized if swarm_scores else None,
    }


def aggregate_results(results: list, rubric: dict) -> dict:
    """Aggregate results across all cases."""
    passing_normalized = rubric["passing_score"] / len(rubric["dimensions"])

    total_cases = len(results)
    swarm_pass_count = sum(1 for r in results if r["pass"])
    baseline_beats_threshold = sum(1 for r in results if r["total_baseline"] >= passing_normalized)

    # Per-dimension averages
    dim_avg = {}
    for dim in rubric["dimensions"]:
        name = dim["name"]
        avg_b = sum(r["comparison"][name]["baseline"] for r in results if r["comparison"][name]["baseline"]) / max(1, sum(1 for r in results if r["comparison"][name]["baseline"]))
        avg_s = sum(r["comparison"][name]["swarm"] for r in results if r["comparison"][name]["swarm"]) / max(1, sum(1 for r in results if r["comparison"][name]["swarm"]))
        avg_d = sum(r["comparison"][name]["delta"] for r in results if r["comparison"][name]["delta"]) / max(1, sum(1 for r in results if r["comparison"][name]["delta"]))
        dim_avg[name] = {"avg_baseline": round(avg_b, 2), "avg_swarm": round(avg_s, 2), "avg_delta": round(avg_d, 2)}

    overall_b = sum(r["total_baseline"] for r in results) / total_cases
    overall_s = sum(r["total_swarm"] for r in results) / total_cases
    overall_delta = sum(r["total_delta"] for r in results) / total_cases

    return {
        "total_cases": total_cases,
        "swarm_pass_count": swarm_pass_count,
        "swarm_pass_rate": round(swarm_pass_count / total_cases * 100, 1),
        "baseline_beats_threshold": baseline_beats_threshold,
        "overall_avg_baseline": round(overall_b, 2),
        "overall_avg_swarm": round(overall_s, 2),
        "overall_avg_delta": round(overall_delta, 2),
        "passing_normalized": passing_normalized,
        "dimension_averages": dim_avg,
    }


def print_summary(agg: dict, rubric: dict):
    """Print aggregate summary."""
    print(f"\n{'='*60}")
    print("  BATCH SUMMARY — All Cases")
    print(f"{'='*60}")

    print(f"\n  Overall:")
    print(f"    Swarm pass rate: {agg['swarm_pass_count']}/{agg['total_cases']} ({agg['swarm_pass_rate']}%)")
    print(f"    Baseline beats threshold: {agg['baseline_beats_threshold']}/{agg['total_cases']}")
    print(f"    Avg scores: baseline={agg['overall_avg_baseline']:.2f}  swarm={agg['overall_avg_swarm']:.2f}  Δ={agg['overall_avg_delta']:+.2f}")
    print(f"    Passing threshold: {agg['passing_normalized']:.2f}/5")

    print(f"\n  Per-Dimension Averages:")
    print(f"  {'Dimension':<35} {'Baseline':>10} {'Swarm':>10} {'Δ':>8}")
    print(f"  {'-'*65}")
    for name, vals in agg["dimension_averages"].items():
        print(f"  {name:<35} {vals['avg_baseline']:>10.2f} {vals['avg_swarm']:>10.2f} {vals['avg_delta']:>+8.2f}")
    print(f"  {'-'*65}")
    print(f"  {'AVERAGE':<35} {agg['overall_avg_baseline']:>10.2f} {agg['overall_avg_swarm']:>10.2f} {agg['overall_avg_delta']:>+8.2f}")

    # Find best and worst dimensions
    sorted_dims = sorted(agg["dimension_averages"].items(), key=lambda x: x[1]["avg_delta"], reverse=True)
    best_dim = sorted_dims[0]
    worst_dim = sorted_dims[-1]
    print(f"\n  Swarm's biggest win: {best_dim[0]} (Δ={best_dim[1]['avg_delta']:+.2f})")
    print(f"  Swarm's weakest gap:  {worst_dim[0]} (Δ={worst_dim[1]['avg_delta']:+.2f})")


def main():
    parser = argparse.ArgumentParser(description="Batch Evaluation Harness")
    parser.add_argument("--cases", nargs="+", help="Specific case IDs to run (e.g., st-001 st-002)")
    parser.add_argument("--swarm-only", action="store_true", help="Skip baselines (use cached)")
    parser.add_argument("--baseline-only", action="store_true", help="Skip swarm runs")
    parser.add_argument("--dry", action="store_true", help="Dry run: list cases without executing")
    args = parser.parse_args()

    rubric = load_rubric()
    BATCH_DIR.mkdir(parents=True, exist_ok=True)

    # Discover available cases
    all_cases = sorted(CASES_DIR.glob("st-*.md"))
    if not all_cases:
        print(f"[ERROR] No stress-test cases found in {CASES_DIR}", file=sys.stderr)
        sys.exit(1)

    # Filter by --cases if specified
    if args.cases:
        cases = [f for f in all_cases if any(c in f.name for c in args.cases)]
        if not cases:
            print(f"[ERROR] None of {args.cases} found in {CASES_DIR}", file=sys.stderr)
            sys.exit(1)
    else:
        cases = all_cases

    print(f"{'='*60}")
    print("User Ops Swarm — Batch Evaluation")
    print(f"{'='*60}")
    print(f"Cases: {', '.join(f.name for f in cases)}")
    print(f"Mode: {'swarm-only' if args.swarm_only else 'baseline+swarm'}")
    print(f"Total cases: {len(cases)}")

    if args.dry:
        print("\n[Dry run] Would execute:")
        for f in cases:
            print(f"  - {f.name}")
        return

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    batch_id = f"batch-{timestamp}"

    results = []
    for case_file in cases:
        case_id = case_file.stem  # e.g. st-001-delivery-decline
        result = run_case(case_id, case_file, rubric, args.swarm_only, args.baseline_only)
        results.append(result)

    # Aggregate
    agg = aggregate_results(results, rubric)
    print_summary(agg, rubric)

    # Save batch report
    report = {
        "batch_id": batch_id,
        "timestamp": datetime.now().isoformat(),
        "rubric_version": rubric.get("version", "unknown"),
        "aggregate": agg,
        "cases": results,
    }
    report_file = BATCH_DIR / f"{batch_id}-report.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nBatch report saved: {report_file}")

    # Key findings
    print(f"\n{'='*60}")
    print("  KEY FINDINGS")
    print(f"{'='*60}")
    passing_normalized = rubric["passing_score"] / len(rubric["dimensions"])
    fails = [r for r in results if not r["pass"]]
    passes = [r for r in results if r["pass"]]
    if fails:
        print(f"\n  Cases where swarm does NOT pass ({passing_normalized:.2f}/5 threshold):")
        for r in fails:
            gap = passing_normalized - r["total_swarm"]
            print(f"    {r['case_id']}: {r['total_swarm']:.2f} (need +{gap:.2f})")
    if passes:
        print(f"\n  Cases where swarm PASSES:")
        for r in passes:
            print(f"    {r['case_id']}: {r['total_swarm']:.2f} ✓")


if __name__ == "__main__":
    main()
