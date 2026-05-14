#!/usr/bin/env python3
"""
Artifact Export Tool — User Ops Swarm
Converts run artifacts into a deliverable report.
Usage: python tools/export_report.py --run-id <run-id> [--format pdf|md|all]
"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime

RUN_DIR = Path(__file__).parent.parent / "runs"
OUTPUT_DIR = Path(__file__).parent.parent / "reports"


def load_artifacts(run_id: str) -> dict:
    run_path = RUN_DIR / run_id
    if not run_path.exists():
        raise FileNotFoundError(f"Run not found: {run_id}")
    artifacts = {}
    for md in run_path.glob("*.md"):
        artifacts[md.stem] = md.read_text()
    state_path = run_path / "state.json"
    if state_path.exists():
        artifacts["state"] = json.loads(state_path.read_text())
    return artifacts


def extract_final_decision(text: str) -> dict:
    """Extract structured decision from 07_final_decision.md."""
    result = {}
    # Extract JSON from markdown
    try:
        json_match = re.search(r'\{.*"decision".*\}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
    except Exception:
        pass
    # budget and discount_limit live at top level of final_plan
    fp = result.get("final_plan", {})
    if isinstance(fp, dict):
        result.setdefault("budget", fp.get("budget", ""))
        result.setdefault("risk_level", fp.get("risk_level", ""))
        result.setdefault("discount_limit", fp.get("discount_limit", ""))
    # Fallback: extract budget and timeline from raw text
    if not result.get("budget"):
        bm = re.search(r'"budget"\s*:\s*"([^"]{20,500})"', text)
        if bm:
            result["budget"] = bm.group(1)
    if not result.get("budget"):
        bm = re.search(r'(¥[\d,]+[K]?\s+[A-Z][^"\n]{10,200})', text)
        if bm:
            result["budget"] = bm.group(1)
    result.setdefault("decision", "unknown")
    result.setdefault("rationale", "")
    return result


def extract_memory_candidate(text: str) -> dict:
    """Extract reusable memory from 08_memory_candidate.md."""
    try:
        json_match = re.search(r'\{.*"memory_candidates".*\}', text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            if data.get("memory_candidates"):
                m = data["memory_candidates"][0]
                return {k: m[k] for k in ["scenario", "segment", "channel", "offer", "lesson", "risk", "reuse_condition", "confidence"]}
    except Exception:
        pass
    return {}


def extract_execution_phases(text: str) -> list:
    """Find phase sections from execution_plan.md."""
    phases = []
    phase_pattern = re.compile(r"(?:^|\n)(?:stage|phase|step)\s*[:\-]?\s*(\d+).*?\n(.*?)(?=\n(?:stage|phase|step|day)|\Z)", re.I | re.DOTALL)
    for m in phase_pattern.finditer(text):
        phases.append({"name": f"Stage {m.group(1)}", "content": m.group(2)[:300].strip()})
    return phases


def extract_budget(text: str) -> list:
    """Extract budget line items from final decision."""
    items = []
    budget_pattern = re.compile(r"¥[\d,]+[K]?\s*[:\-]?\s*(.*?)(?=\n|$)")
    for m in budget_pattern.finditer(text):
        line = m.group().strip()
        if line and "¥" in line:
            items.append(line)
    return items


def build_executive_summary(run_id: str, artifacts: dict) -> str:
    """Build executive brief from artifacts."""
    state = artifacts.get("state", {})
    decision_data = extract_final_decision(artifacts.get("07_final_decision", ""))
    memory = extract_memory_candidate(artifacts.get("08_memory_candidate", ""))
    execution = artifacts.get("05_execution_plan", "")[:3000]
    risk_data = artifacts.get("06_risk_review", "")[:2000]

    decision = decision_data.get("decision", "unknown").upper()
    rationale = decision_data.get("rationale", "")[:400]
    final_plan = decision_data.get("final_plan", {})
    # Budget — use top-level budget_allocation.total first, then budget field
    budget_alloc = final_plan.get("budget_allocation", {})
    if isinstance(budget_alloc, dict) and budget_alloc.get("total"):
        budget_text = f"总预算：{budget_alloc.get('total', '')}"
        items = budget_alloc.get("itemized", [])
        if items:
            budget_lines = [f"- {i.get('item','')}: {i.get('amount','')} ({i.get('percentage','')})"
                           for i in items if isinstance(i, dict)]
            budget_text += "\n" + "\n".join(budget_lines[:6])
    elif final_plan.get("budget"):
        budget_text = str(final_plan.get("budget", ""))[:300]
    else:
        budget_text = "未明确预算"

    # Risk level from 06_risk_review.md (primary source)
    risk_text = artifacts.get("06_risk_review", "")
    risk_match = re.search(r'"risk_level"\s*:\s*"([^"]+)"', risk_text)
    risk_level = risk_match.group(1) if risk_match else "unknown"
    # Fallback: from final decision
    if risk_level == "unknown":
        risk_match2 = re.search(r'"risk_level"\s*:\s*"([^"]+)"', risk_text)
        risk_level = risk_match2.group(1) if risk_match2 else "unknown"

    # Risk controls
    controls = final_plan.get("risk_controls", [])[-5:] if isinstance(final_plan.get("risk_controls"), list) else []

    # Phases — try staged_milestones first, fall back to phase_1/2/3
    phase_list = final_plan.get("staged_milestones", final_plan.get("final_plan", final_plan))
    phases = []
    if isinstance(phase_list, dict):
        for key, p in phase_list.items():
            if isinstance(p, dict):
                phases.append({
                    "name": p.get("name", p.get("date", p.get("target", key))),
                    "timeline": p.get("timeline", p.get("criteria", p.get("date", ""))),
                    "objective": p.get("objective", p.get("target", p.get("pass_criteria", "")))[:100]
                })
    if not phases:
        for key in ["phase_1", "phase_2", "phase_3"]:
            p = final_plan.get(key, {})
            if isinstance(p, dict):
                phases.append({
                    "name": p.get("name", key),
                    "timeline": p.get("timeline", ""),
                    "objective": p.get("primary_objective", "")[:100]
                })

    run_date = state.get("progress", {}).get("started_at", datetime.now().isoformat()[:10])

    lines = [
        "# User Ops Swarm — Executive Decision Report",
        f"**Run ID:** `{run_id}`  |  **Date:** {run_date}  |  **Decision:** {decision}",
        "",
        "---",
        "",
        "## Verdict",
        f"**{decision}**",
        "",
        f"{rationale}",
        "",
        "---",
        "",
        "## Execution Phases",
    ]

    for p in phases:
        lines.append(f"### {p['name']} — {p['timeline']}")
        lines.append(f"**Objective:** {p['objective']}")
        lines.append("")

    lines += [
        "---",
        "",
        "## Budget",
        f"{budget_text}",
        "",
        "---",
        "",
        f"## Risk Level: {risk_level.upper()}",
    ]

    if controls:
        lines.append("")
        lines.append("**Risk Controls:**")
        for c in controls:
            if isinstance(c, dict):
                lines.append(f"- **{c.get('control', 'Control')}:** {c.get('description', '')}")

    if memory:
        lines += [
            "",
            "---",
            "",
            "## Memory Candidate (Pending Human Review)",
            f"- **Scenario:** {memory.get('scenario', '')[:200]}",
            f"- **Lesson:** {memory.get('lesson', '')[:300]}",
            f"- **Reuse Condition:** {memory.get('reuse_condition', '')[:200]}",
            f"- **Confidence:** {memory.get('confidence', 'N/A')}",
        ]

    lines += [
        "",
        "---",
        "",
        f"*Generated by User Ops Swarm · Full artifacts: `runs/{run_id}/`*",
    ]

    return "\n".join(lines)


def export_markdown(run_id: str, artifacts: dict) -> Path:
    """Export as markdown report."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    summary = build_executive_summary(run_id, artifacts)
    out_path = OUTPUT_DIR / f"{run_id}-report.md"
    out_path.write_text(summary)
    return out_path


def export_json(run_id: str, artifacts: dict) -> Path:
    """Export structured decision as JSON."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    decision = extract_final_decision(artifacts.get("07_final_decision", ""))
    memory = extract_memory_candidate(artifacts.get("08_memory_candidate", ""))
    state = artifacts.get("state", {})
    out = {
        "run_id": run_id,
        "run_date": state.get("progress", {}).get("started_at", ""),
        "decision": decision,
        "memory_candidate": memory,
        "completed_steps": state.get("progress", {}).get("completed_steps", []),
    }
    out_path = OUTPUT_DIR / f"{run_id}-decision.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    return out_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Export User Ops Swarm run as report")
    parser.add_argument("--run-id", required=True, help="Run ID to export")
    parser.add_argument("--format", choices=["md", "json", "all"], default="all")
    args = parser.parse_args()

    artifacts = load_artifacts(args.run_id)
    print(f"Loaded {len(artifacts)} artifacts from run: {args.run_id}")
    print(f"Available: {list(artifacts.keys())}")

    outputs = []
    if args.format in ("md", "all"):
        p = export_markdown(args.run_id, artifacts)
        outputs.append(str(p))
        print(f"Markdown report: {p}")
    if args.format in ("json", "all"):
        p = export_json(args.run_id, artifacts)
        outputs.append(str(p))
        print(f"JSON decision: {p}")

    print(f"\nExported {len(outputs)} file(s) to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()