#!/usr/bin/env python3
"""
Memory Review Tool — User Ops Swarm
Human-in-the-loop gate for memory candidates.
Usage: python tools/memory_review.py --run-id <run-id> [--approve|--reject]
"""
import json
from datetime import date, datetime
import json, re, sys
from pathlib import Path

RUN_DIR = Path(__file__).parent.parent / "runs"
MEMORY_FILE = Path(__file__).parent.parent / "memory" / "memory_log.md"
MEMORY_BACKUP = Path(__file__).parent.parent / "memory" / "memory_log.backup.md"


def load_memory_candidate(run_id: str) -> dict:
    run_path = RUN_DIR / run_id
    mc_path = run_path / "08_memory_candidate.md"
    state_path = run_path / "state.json"
    decision_path = run_path / "07_final_decision.md"

    raw_text = mc_path.read_text() if mc_path.exists() else ""
    # Strip thinking tags that models sometimes wrap output in
    text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    decision_text = decision_path.read_text() if decision_path.exists() else ""

    # Extract decision from final_decision.md
    decision = "unknown"
    decision_m = re.search(r'"decision"\s*:\s*"([^"]+)"', decision_text)
    if decision_m:
        decision = decision_m.group(1).upper()

    # Parse memory candidate JSON — direct parse is most reliable
    candidates = []
    try:
        # Full parse works on clean output
        d = json.loads(text)
        raw_cands = d.get("memory_candidates", [])
        if raw_cands:
            candidates = raw_cands
    except Exception:
        # Fallback: try depth-counting bracket matching
        candidates = []
        try:
            first_brace = text.index("{")
            obj = text[first_brace:]
            depth = 0
            end = 0
            for i, ch in enumerate(obj):
                if ch == "[":
                    depth += 1
                elif ch == "]":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            if end > 0:
                d = json.loads(obj[:end])
                candidates = d.get("memory_candidates", [])
        except Exception:
            pass

    if not candidates:
        candidates = [{"raw": text[:1500], "confidence": "unknown"}]

    run_date = state.get("progress", {}).get("started_at", str(date.today()))
    scenario = candidates[0].get("scenario", "unknown") if candidates else "unknown"

    return {
        "run_id": run_id,
        "run_date": run_date,
        "decision": decision,
        "scenario": scenario,
        "candidates": candidates,
        "raw_text": text,
    }


def build_review_prompt(data: dict) -> str:
    lines = [
        "=" * 60,
        f"  Memory Candidate Review — {data['run_id']}",
        f"  Date: {data['run_date']}  |  Decision: {data['decision']}",
        "=" * 60,
        "",
        "## Scenario",
        data["scenario"][:500],
        "",
        "## Memory Candidates",
    ]

    for i, c in enumerate(data["candidates"], 1):
        lines.append(f"\n### Candidate {i}  [confidence: {c.get('confidence', 'N/A')}]")
        for field in ["scenario", "segment", "channel", "offer", "lesson", "risk", "reuse_condition"]:
            val = c.get(field, "")
            if val:
                lines.append(f"  **{field}:** {val[:300]}{'...' if len(str(val)) > 300 else ''}")
        if c.get("raw") and not c.get("lesson"):
            lines.append(f"  **raw:** {c['raw'][:300]}...")

    lines += [
        "",
        "=" * 60,
        "Actions:",
        "  python tools/memory_review.py --run-id {run_id} --approve",
        "  python tools/memory_review.py --run-id {run_id} --reject",
        "  python tools/memory_review.py --run-id {run_id} --edit    (opens editor)",
        "=".format(run_id=data["run_id"]),
    ]
    return "\n".join(lines)


def extract_memory_entry(data: dict, index: int = 0) -> str:
    """Build a memory_log.md entry from a memory candidate."""
    c = data["candidates"][index]
    entry_id = f"M{data['run_date'].replace('-', '')}-{data['run_id'][:8]}"
    today = date.today().isoformat()
    now_ts = datetime.now().isoformat()

    entry = f"""### {entry_id} | {today} | operational_pattern

**Timestamp**: {now_ts}
**Approved By**: HUMAN
**Scenario**: {c.get('scenario', data['scenario'])[:400]}
**Segment**: {c.get('segment', 'N/A')[:200]}
**Channel**: {c.get('channel', 'N/A')[:200]}
**Offer**: {c.get('offer', 'N/A')[:300]}
**Outcome**: Decision: **{data['decision']}** (see runs/{data['run_id']}/07_final_decision.md)
**Lesson**: {c.get('lesson', c.get('raw', ''))[:500]}
**Reuse Condition**: {c.get('reuse_condition', 'N/A')[:300]}
"""
    return entry


def write_to_memory_log(entry: str, run_id: str):
    """Append approved entry to memory_log.md."""
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing
    if MEMORY_FILE.exists():
        MEMORY_BACKUP.write_text(MEMORY_FILE.read_text())

    content = MEMORY_FILE.read_text()

    # Find insertion point: after "<!-- Approved memories go here -->"
    marker = "<!-- Approved memories go here -->"
    if marker in content:
        content = content.replace(marker, f"{marker}\n\n{entry}\n")
    else:
        # Fallback: before "## Archived"
        archived_marker = "## Archived"
        if archived_marker in content:
            content = content.replace(archived_marker, f"{entry}\n\n---\n\n{archived_marker}")
        else:
            content += f"\n\n{entry}\n"

    MEMORY_FILE.write_text(content)

    # Log in review log
    review_log_m = re.search(r'(\| Date \| Entry ID \|.*?\n)((?:\|.*?\n)*)', content)
    if review_log_m:
        new_row = f"| {date.today().isoformat()} | {entry.split('|')[1].strip()} | APPROVED | HUMAN | {run_id} |\n"
        content = content.replace(review_log_m.group(2).rstrip('\n'), review_log_m.group(2).rstrip('\n') + new_row)
        MEMORY_FILE.write_text(content)

    print(f"[OK] Written to {MEMORY_FILE}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Review and approve memory candidates")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--reject", action="store_true")
    parser.add_argument("--edit", action="store_true")
    parser.add_argument("--entry-index", type=int, default=0, help="Which candidate to approve (0-indexed)")
    parser.add_argument("--dry-run", action="store_true", help="Print entry without writing")
    args = parser.parse_args()

    data = load_memory_candidate(args.run_id)
    print(build_review_prompt(data))

    if args.dry_run:
        entry = extract_memory_entry(data, args.entry_index)
        print("\n[Dry run — entry to be written:]\n")
        print(entry)
        return

    if not args.approve and not args.reject and not args.edit:
        print("\n[No action. Use --approve, --reject, or --edit]")
        return

    if args.reject:
        print(f"[Rejected memory candidate for run: {args.run_id}]")
        return

    if args.approve:
        entry = extract_memory_entry(data, args.entry_index)
        write_to_memory_log(entry, args.run_id)
        return

    if args.edit:
        entry = extract_memory_entry(data, args.entry_index)
        import tempfile, subprocess, os
        fd, tmp = tempfile.mkstemp(suffix=".md", prefix="memory_edit_")
        os.write(fd, entry.encode())
        os.close(fd)
        editor = os.environ.get("EDITOR", "nano")
        subprocess.run([editor, tmp])
        edited = Path(tmp).read_text()
        os.unlink(tmp)
        if edited.strip() and edited.strip() != entry.strip():
            write_to_memory_log(edited, args.run_id)
        else:
            print("[No changes made]")


if __name__ == "__main__":
    main()