# User Ops Swarm for QSR

> A bounded multi-agent prototype that simulates a professional restaurant user operations department — as a swarm of specialized AI agents with distinct roles, competing views, and a structured decision process.

---

## What This Is

**User Ops Swarm for QSR** is a local, command-line prototype that models a quick-service restaurant (QSR) user operations team as an AI agent system.

Most AI tools for marketing operations give you one answer. This project tests a different premise: a team of agents — each with a different perspective, mandate, and area of expertise — arguing, challenging, and synthesizing their way toward a better decision than any single agent could reach alone.

It is **not** a SaaS dashboard, a campaign launcher, or a BI tool. It does not connect to live POS systems, delivery platforms, or CRM databases. It is a research prototype for evaluating whether multi-agent organizational mechanics can improve the quality of user operations decision-making.

---

## The Problem It Addresses

Restaurant user operations is not a single-threaded task. A real campaign involves built-in tension:

```
Marketing wants reach.
Content wants organic spread.
Delivery wants immediate conversion.
Group buying wants acquisition at scale.
Membership wants long-term asset value.
Stores worry about execution capacity.
Finance watches margin.
The director has to decide.
```

Traditional AI tools collapse all of that into one prompt. This prototype keeps those perspectives separate — and forces them to argue.

---

## What It Produces

Given a plain-text task input, the swarm runs through 9 structured steps and produces 8 artifacts per run:

| # | Artifact | What It Contains |
|---|----------|-----------------|
| 1 | Context Summary | Task classification, objectives, constraints, open questions |
| 2 | Opportunity Analysis | User segments, consumption scenarios, channel roles |
| 3 | Bull / Bear Debate | Growth case vs. risk case — genuine adversarial positions |
| 4 | Strategy Synthesis | Revised plan after absorbing both sides |
| 5 | Execution Crew Plans | Campaign, content, delivery, group buying, and membership plans |
| 6 | Risk Review | Profit, brand, fulfillment, platform, and member asset risks |
| 7 | Final Decision | Director verdict — approve / revise / reject / test-only |
| 8 | Memory Candidate | Structured lesson learned for future runs |

All artifacts are written to a dated `runs/` directory alongside a `state.json` that tracks the full run history. Output is markdown — human-readable and diff-friendly.

---

## Example Scenario

> **Input:** Launch a summer new-product acquisition campaign. Goals: new customers, delivery orders, member signups. Constraints: protect margin, keep store operations simple.

> **Output:** The swarm identifies priority user segments and consumption scenarios, assigns roles to delivery platforms, social media, group buying, and the membership program, generates an aggressive growth case alongside a detailed risk case, synthesizes a revised strategy that balances both, reviews risks across five dimensions, produces a final director decision with success metrics and budget boundaries, and flags key learnings as a memory candidate for human review.

---

## Architecture

```
                    user_ops_context.md
                    memory_log.md
                    runs/<run_id>/input.md
                               │
                    ┌──────────▼──────────┐
                    │   Context Loader     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                                 ▼
    ┌──────────────────┐              ┌──────────────────┐
    │ User & Scene     │              │  Channel         │
    │ Analyst          │              │  Analyst         │
    └────────┬─────────┘              └────────┬─────────┘
              └────────────────┼────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                                 ▼
    ┌──────────────────┐              ┌──────────────────┐
    │  Growth Bull     │              │  Growth Bear     │
    │  Agent           │              │  Agent           │
    └────────┬─────────┘              └────────┬─────────┘
              └────────────────┼────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Strategy Manager    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Risk Reviewer       │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  User Ops Director   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Reflection Agent   │
                    └─────────────────────┘
```

**Design principles:**

- **Flow controls sequence.** A central orchestrator runs steps in order — no free-form agent calling.
- **State is explicit.** Every step writes to a shared state object and exports to `state.json`. Nothing lives only in a chat context.
- **Agents have bounded roles.** Each agent has a defined input, a defined output schema, and nothing else.
- **Memory requires human review.** The Reflection Agent only generates candidates — it never writes to long-term memory automatically.
- **Execution Crew is Phase 2.** Phase 1 deliberately stops at the Director's decision. Campaign execution is a separate concern.

---

## Current Status: Phase 1 Complete

Phase 1 (CrewAI Local Prototype) is implemented and verified:

- 7 agents operational
- 8-step workflow fully wired and tested
- 7 artifacts produced per run
- JSON schemas validate step outputs
- Runs produce structured markdown + `state.json`
- Ollama / llama3.2 as default LLM (no API key required)

One test run has been completed (`runs/test-002`). The swarm successfully generated a full debate, produced a director decision, and output a memory candidate.

---

## Tech Stack

```
Python 3.11+
CrewAI
Pydantic
YAML
Markdown (input/output)
Ollama + llama3.2 (default LLM)
Local filesystem
```

No database, no web frontend, no external API integrations in Phase 1.

---

## Roadmap

### Phase 2 — Evaluation Harness
- Single-agent vs. swarm comparison framework
- Structured scoring rubrics for quality assessment
- Failure case library
- Human review templates for memory candidates

### Phase 3 — Execution Crew
- Split execution phase into sub-agents: Campaign Planner, Content Creator, Delivery Specialist, Membership Strategist
- Structured execution plans per channel
- Timeline and owner notes per artifact

### Phase 4 — Runtime Evaluation
- Migrate orchestration to LangGraph if CrewAI control proves insufficient
- Preserve all agent specs, schemas, and artifact formats
- Add pause / resume / rollback at step boundaries

### Phase 5 — Control Plane (optional)
- Lightweight local web UI for reviewing runs, approving memory, and triggering new tasks
- Multi-user session management
- Long-term memory store with retrieval

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/<your-handle>/user-ops-swarm.git
cd user-ops-swarm

# Install dependencies
pip install -e .

# Make sure Ollama is running locally with llama3.2
ollama run llama3.2

# Run the swarm with an example task
python -m src.flow.user_ops_flow \
  --input examples/summer-new-product.md \
  --context context/user_ops_context.md \
  --memory memory/memory_log.md
```

Outputs go to `runs/<run_id>/`. Open the generated `state.json` for a full run summary.

---

## Project Structure

```
user-ops-swarm/
├── src/
│   ├── flow/            # Main orchestration (user_ops_flow.py)
│   ├── agents/           # Agent YAML definitions
│   ├── tasks/            # Task YAML definitions
│   ├── schemas/          # Pydantic models for each artifact
│   ├── protocols/        # Inter-agent protocol docs
│   └── utils.py          # Shared helpers
├── context/              # Brand / business context template
├── memory/              # Long-term memory log (human-reviewed only)
├── examples/            # Example task inputs
├── runs/                # All run outputs (gitignored)
└── README.md
```

---

## License

MIT
