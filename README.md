# User Ops Swarm for QSR

> *A multi-agent AI system that thinks like a restaurant operations team — with built-in debate, risk review, and a director who makes the call.*

---

## The Premise

Restaurant marketing isn't a solo task. Your CMO wants reach. Your delivery lead wants conversions. Your store managers want operational sanity. Your finance lead wants margin protected. Someone has to synthesize all of that into a decision — with the clock ticking.

**User Ops Swarm** is an AI research prototype that models a real restaurant operations department as a swarm of specialized agents. Each agent has a distinct voice, a bounded mandate, and a job to do. They don't agree by default. They argue. The swarm forces the conflict, then synthesizes.

> **What it is:** A command-line decision engine for QSR (quick-service restaurant) user operations — campaign planning, channel strategy, risk review, and final recommendations.
> **What it is not:** A campaign launcher, a BI dashboard, or a SaaS product. It runs locally. It produces structured markdown artifacts. It doesn't push to live platforms.

---

## What It Actually Does

Drop in a task brief. Get back a structured argument — not a wall of text.

**One run produces 8 artifacts:**

| # | Artifact | Purpose |
|---|---------|---------|
| 1 | Context Summary | What are we actually solving? |
| 2 | Opportunity Analysis | Segments, scenarios, channel roles |
| 3 | Bull / Bear Debate | Two agents argue — growth case vs. risk case |
| 4 | Strategy Synthesis | Revised plan after absorbing both sides |
| 5 | Execution Plan | Campaign, content, delivery, group buying, membership — channel-by-channel |
| 6 | Risk Review | Five dimensions: profit, brand, fulfillment, platform, member asset |
| 7 | Final Decision | Director verdict: approve / revise / reject / test-only |
| 8 | Memory Candidate | What we learned — for human review before it goes to long-term memory |

Every artifact is markdown. Every run writes to a timestamped `runs/<run-id>/` directory with a `state.json` log. Human-readable. Diff-friendly. No lock-in.

---

## What It Looks Like in Practice

```
$ python main.py --input examples/stress-tests/st-001-delivery-decline.md

[STEP 1/9] Loading context... ✓
[STEP 2/9] User & Scene analysis... ✓
[STEP 3/9] Bull vs. Bear debate... ✓
[STEP 4/9] Strategy synthesis... ✓
[STEP 5/9] Execution Crew (5 agents)... ✓
[STEP 6/9] Risk review... ✓
[STEP 7/9] Director decision... ✓
[STEP 8/9] Memory candidate... ✓
[STEP 9/9] Writing artifacts... ✓

→ 8 artifacts written to runs/batch-0514-st-001/
```

The Bull/Bear debate is where the value emerges. The Growth Bull agent pushes for aggressive acquisition. The Growth Bear agent forces a margin reality check. They don't agree — that's the point. The Strategy Manager then synthesizes a plan that survives both perspectives before it ever reaches the Director's desk.

---

## The Evaluation Evidence

This project ships with a full evaluation harness: baseline single-agent vs. swarm comparison, scored against a 6-dimension rubric. Run it yourself:

```
$ python evaluations/batch_evaluation.py
```

**Latest batch results — MiniMax M2.1 (4 scenarios, May 2026):**

| Scenario | Baseline | Swarm | Δ | Result |
|----------|----------|-------|---|--------|
| Delivery volume crisis | 1.08 | **4.77** | +3.69 | ✅ Pass |
| Dormancy reactivation | 1.08 | **4.77** | +3.69 | ✅ Pass |
| New store opening | 1.08 | **4.77** | +3.69 | ✅ Pass |
| Social review crisis | 1.08 | **4.77** | +3.69 | ✅ Pass |
| **Average** | **1.08** | **4.77** | **+3.69** | **4/4 ✅** |

Per-dimension deltas (swarm vs. baseline):

| Dimension | Δ |
|-----------|---|
| business_insight_depth | +4.00 |
| execution_actionability | +4.00 |
| risk_identification_completeness | +4.00 |
| decision_clarity | +4.00 |
| conflict_quality | +3.00 |
| reflection_reusability | +3.00 |

> Full report: `evaluations/reports/batches/batch-20260514-150655-report.json`

---

## Architecture

```
Input (task brief)
        │
  ┌─────▼─────┐
  │  Context   │  ← Brand config, memory log, run history
  │  Loader   │
  └─────┬─────┘
        │
  ┌─────▼─────┐
  │ User Ops  │  ← Scene + Channel analysis
  │  Flow     │
  └─────┬─────┘
        │
  ┌─────▼─────┐         ┌──────────┐
  │   Bull    │◄────────►│   Bear   │  ← Structured adversarial debate
  │  Agent    │  conflict │  Agent   │
  └─────┬─────┘         └────┬─────┘
        │                     │
  ┌─────▼─────────────────────▼─────┐
  │     Strategy Manager          │  ← Synthesizes, absorbs both sides
  └────────────┬──────────────────┘
               │
  ┌────────────▼──────────┐
  │  Execution Crew (5)  │  ← Campaign / Content / Delivery / Group Buying / Membership
  └────────────┬──────────┘
               │
  ┌────────────▼──────────┐
  │    Risk Reviewer     │  ← 5 risk dimensions
  └────────────┬──────────┘
               │
  ┌────────────▼──────────┐
  │   User Ops Director   │  ← Final verdict
  └────────────┬──────────┘
               │
  ┌────────────▼──────────┐
  │  Reflection Agent    │  ← Memory candidate (human review gate)
  └───────────────────────┘
```

**12 agents total:**
- **Decision layer (7):** User & Scene Analyst, Channel Analyst, Growth Bull, Growth Bear, Strategy Manager, Risk Reviewer, User Ops Director
- **Execution layer (5):** Campaign Planner, Content Creator, Delivery Specialist, Group Buying Strategist, Membership Strategist

All agents defined in YAML. All outputs validated by Pydantic schemas. All state tracked in `state.json`.

---

## Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Runtime | CrewAI 1.14.4 | Structured agent orchestration with Flow primitives |
| LLM | Ollama + llama3.2 | Local, no API keys, fast iteration |
| Schemas | Pydantic 2.0+ | Validated outputs at every step |
| Artifacts | Markdown | Human-readable, git-diffable, platform-agnostic |
| State | JSON + filesystem | No database required in Phase 1–3 |

**No external APIs. No API keys. No vendor lock-in.** This runs on a laptop.

---

## Project Structure

```
user-ops-swarm/
├── src/
│   ├── flow/           # Orchestration (CrewAI Flow, 9 steps)
│   ├── agents/          # 12 YAML agent definitions
│   ├── tasks/           # 13 YAML task definitions
│   ├── schemas/         # Pydantic models per artifact
│   ├── protocols/       # Inter-agent debate, risk, memory protocols
│   └── utils.py         # YAML loader, run directory, CLI
├── context/            # Brand config (Wok & Roll template)
├── memory/             # Human-reviewed long-term memory
├── examples/
│   ├── stress-tests/   # 4 scenario-based test cases
│   └── summer-new-product.md
├── evaluations/        # Evaluation harness + rubrics + failure library
├── runs/               # All run outputs (gitignored)
└── README.md
```

---

## Getting Started

```bash
# 1. Clone and install
git clone https://github.com/q445rxdfd5-alt/user-ops-swarm.git
cd user-ops-swarm
pip install -e .

# 2. Make sure Ollama is running with llama3.2
ollama serve &
ollama pull llama3.2

# 3. Run the swarm on a stress-test scenario
python main.py --input examples/stress-tests/st-001-delivery-decline.md

# 4. Run the evaluation harness
python evaluations/batch_evaluation.py

# 5. Check the report
cat evaluations/reports/batches/batch-*/report.json
```

---

## Roadmap

### Phase 1 ✅ — Core Swarm (Local, CrewAI)
9-step workflow, 12 agents, YAML-based, Ollama LLM, fully operational.

### Phase 2 ✅ — Evaluation Infrastructure
Baseline vs. swarm comparison, 6-dimension rubric, failure case library, human review templates. First evaluation: swarm scores 3.85/5 vs. baseline 1.08/5 (+2.77 delta).

### Phase 3 ✅ — Execution Crew
Five specialized execution agents: Campaign, Content, Delivery, Group Buying, Membership. Execution plans are now full channel-by-channel artifacts with timelines and owners.

### Phase 4 — LangGraph Migration *(planned)*
If CrewAI control proves insufficient for pause/resume/rollback, migrate orchestration to LangGraph while preserving all agent specs, schemas, and artifact formats.

### Phase 5 — Control Plane *(planned)*
Local web viewer for reviewing runs, approving memory candidates, triggering new tasks, and browsing the long-term memory store.

---

## Contributing Stress-Test Scenarios

Add a new `.md` file to `examples/stress-tests/`. The file should include:

```
# ST-XXX: [Short Title]

## Situation          ← What's happening right now
## Goals (Ranked)     ← What success looks like
## Constraints        ← Non-negotiables
## Options Under Debate ← 2-4 specific alternatives
## Critical Question  ← The one question the swarm must answer
## Success Metrics    ← How we measure success
## Anti-Goals         ← What NOT to do
```

See existing scenarios in `examples/stress-tests/` for the full format and level of detail expected.

---

## License

MIT
