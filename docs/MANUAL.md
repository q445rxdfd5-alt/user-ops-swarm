# user-ops-swarm — Product & Usage Manual

## What It Is

A multi-agent AI system that replicates the decision-making workflow of a QSR restaurant operations team. Twelve specialized agents — each with a distinct role — collaborate through a structured 9-step flow to analyze situations, debate strategy, and produce day-level execution plans.

**Not a chatbot.** It takes a structured scenario as input and outputs eight production-ready artifacts.

---

## Architecture

```
INPUT: scenario file (.md)
    │
    ▼
Step 1 ─ Context Loader       → builds context from scenario + memory
Step 2 ─ Analyst Crew         → UserSceneAnalyst + ChannelAnalyst (parallel)
Step 3 ─ Bull/Bear Debate     → Bull runs first → Bear directly challenges Bull
Step 4 ─ Strategy Manager     → Synthesizes debate, quotes specific positions
Step 5 ─ Execution Crew       → Campaign + Content + Delivery + GroupBuy + Membership (parallel)
Step 6 ─ Risk Reviewer       → Independent review, can BLOCK
Step 7 ─ Director             → Final decision with provenance trace
Step 8 ─ Reflection Agent     → Generates memory candidates (NOT auto-written)
    │
    ▼
OUTPUT: 8 markdown artifacts
```

---

## Agents (12)

| Agent | Role |
|---|---|
| ContextLoaderAgent | Builds structured context from input |
| UserSceneAnalystAgent | User segments, pain points, demand drivers |
| ChannelAnalystAgent | Channel performance and gap analysis |
| GrowthBullAgent | Aggressive growth advocate |
| GrowthBearAgent | Adversarial challenger — directly rebuts Bull |
| StrategyManagerAgent | Synthesizes debate, adopts/rejects with quotes |
| CampaignPlannerAgent | Campaign structure and phases |
| ContentCreatorAgent | Content assets and channel copy |
| DeliverySpecialistAgent | Fulfillment and logistics design |
| GroupBuyingStrategistAgent | Group-buying mechanics and viral design |
| MembershipOperatorAgent | Loyalty, retention, tier mechanics |
| RiskReviewerAgent | Independent risk review, can BLOCK |
| DirectorAgent | Final authority with deliberation trace |
| ReflectionAgent | Generates reusable memory candidates |

---

## Artifacts (8 outputs)

| File | Content |
|---|---|
| `01_context_summary.md` | Structured context: situation, constraints, KPIs |
| `02_opportunity_analysis.md` | User segments, channels, gaps |
| `03_bull_bear_debate.md` | Bull thesis + Bear counter (directly challenges Bull) |
| `04_strategy_summary.md` | Synthesized strategies with quoted adoptions/rejections |
| `05_execution_plan.md` | Campaign + Content + Delivery + GroupBuy + Membership plans |
| `06_risk_review.md` | Independent risk review with BLOCK authority |
| `07_final_decision.md` | Director decision with Bull/Bear provenance trace |
| `08_memory_candidate.md` | Reusable insights (human review before approval) |

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/q445rxdfd5-alt/user-ops-swarm.git
cd user-ops-swarm
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Configure LLM

```bash
# Option A: MiniMax (recommended)
export MINIMAX_API_KEY=your_key
export MINIMAX_BASE_URL=https://api.minimax.chat/v1
export MINIMAX_MODEL=MiniMax-M2.1

# Option B: Ollama (local)
export OLLAMA_BASE_URL=http://localhost:11434/v1
export OLLAMA_MODEL=gemma4:e4b
```

### 3. Run

```bash
# From scenario file
python main.py --input examples/stress-tests/st-001-delivery-decline.md --run-id my-run

# From inline input
python main.py --input "Shanghai cluster: delivery volume down 14%, fulfillment rate 87%, ranking dropped #3 to #11" --run-id inline-test
```

### 4. Review outputs

```bash
ls runs/my-run/
```

---

## Workflow

### Memory — How the System Learns

```
Run → 08_memory_candidate.md (auto-generated)
         │
         ▼
    python tools/memory_review.py --run-id my-run
         │
    [approve / reject / dry-run]
         │
         ▼
    memory/memory_log.md (approved entries only)
         │
         ▼
    Next run reads approved memories → injected into context
```

Without memory: each run starts fresh.
With memory: system references past lessons from similar scenarios.

### Testing

```bash
# Run full batch (15 scenarios)
python evaluations/batch_evaluation.py --swarm-only

# Run single scenario with full evaluation
python evaluations/run_evaluation.py --run-id my-run

# Export run to executive brief
python tools/export_report.py --run-id my-run
```

---

## Configuration Files

| File | Purpose |
|---|---|
| `.env` | API keys and model selection |
| `context/user_ops_context.md` | Brand context template (fill in your QSR brand) |
| `src/agents/*.yaml` | Agent system prompts and output formats |
| `src/tasks/*.yaml` | Task definitions and expected outputs |
| `evaluations/rubrics/` | Evaluation criteria and scoring rubrics |
| `examples/stress-tests/` | Test scenarios |

---

## Evaluation Results

| Metric | Score |
|---|---|
| Swarm pass rate | 15/15 (100%) |
| Average quality score | 4.75/5 |
| Baseline vs Swarm delta | +3.69 |
| Test coverage | 15 scenarios, 7 categories |

---

## Project Structure

```
user-ops-swarm/
├── main.py                      # CLI entry point
├── src/
│   ├── agents/                   # 14 agent YAML definitions
│   ├── flow/
│   │   └── user_ops_flow.py     # 9-step orchestration
│   └── tasks/                   # 14 task YAML definitions
├── tools/
│   ├── memory_review.py          # Human memory approval
│   └── export_report.py          # Executive brief export
├── evaluations/
│   ├── batch_evaluation.py       # Multi-case batch runner
│   ├── run_evaluation.py         # Single-case evaluator
│   ├── rubrics/                  # Evaluation criteria
│   └── reports/                  # Batch run reports
├── context/
│   └── user_ops_context.md       # Brand context template
├── memory/
│   └── memory_log.md             # Approved memory entries
├── examples/
│   └── stress-tests/             # 15 test scenarios
└── runs/                         # Run outputs (gitignored)
```

---

## Development Status

| Phase | Status |
|---|---|
| Phase 1 — Core flow (9 steps) | ✅ Complete |
| Phase 2 — Evaluation harness | ✅ Complete |
| Phase 3 — MiniMax integration | ✅ Complete |
| Objective 2 — Bull/Bear hardening | ✅ Complete |
| Objective 3 — LangGraph migration | ⏸ Not started |

**Current system:** CrewAI framework, fully functional, 15/15 test cases passing.
