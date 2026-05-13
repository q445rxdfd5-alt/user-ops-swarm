# User Ops Swarm for QSR

> **Your restaurant's user operations department, distilled into an AI agent team.**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/Powered%20by-CrewAI-green.svg)](https://www.crewai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## tl;dr

**User Ops Swarm for QSR** is a local-first prototype that runs a CrewAI-powered agent team to handle restaurant user operations decisions—campaigns, channel strategies, risk reviews, and final go/no-go verdicts—just like a real ops team would.

It's built to answer one question before anything else: *Can a multi-agent organization make better operations decisions than a single prompt?*

Not a dashboard. Not a CRM. Not a campaign automator. An agent swarm that thinks through your problems like a team.

---

## Why This Exists

Real restaurant user operations is messy. A single campaign involves competing interests:

| Role | What They Want |
|------|----------------|
| Marketing | Brand awareness, market noise |
| Content | Viral reach, engagement |
| Delivery | Immediate order conversion |
| Group Buying | Low-cost new customer acquisition |
| Membership | Long-term asset accumulation |
| Stores | Manageable fulfillment load |
| Finance | Intact gross margins |
| Brand | Consistent positioning |

One person can't balance all of that. Neither can one AI agent working alone.

**User Ops Swarm** turns every stakeholder perspective into a dedicated agent, then orchestrates real debate, synthesis, and decision-making—exactly like a professional operations team would.

---

## What It Actually Does

Drop in a task—say, launching a summer new-product campaign—and the swarm walks through the full chain:

```
Signal Analysis → Opportunity Mapping → Bull vs. Bear Debate
→ Strategy Synthesis → Execution Planning → Risk Review
→ Director Decision → Memory Candidate
```

Each step produces structured output. No chat logs, no wall-of-text summaries. Just artifacts you can review, export, and build on.

### Output Artifacts

| File | What It Contains |
|------|-------------------|
| `01_context_summary.md` | Brand, business, channel, constraints overview |
| `02_opportunity_analysis.md` | User segments, scenarios, channel roles |
| `03_bull_bear_debate.md` | Growth arguments vs. risk objections |
| `04_strategy_summary.md` | Revised strategy with adopted/rejected points |
| `05_execution_plan.md` | Campaign, content, delivery, group-buying, membership plans |
| `06_risk_review.md` | Risk assessment across profit, brand, fulfillment, platforms |
| `07_final_decision.md` | Director verdict: approve / revise / reject / test-only |
| `08_memory_candidate.md` | Compressed learnings ready for human review |

---

## Architecture

The swarm runs on **CrewAI Flow**, which keeps the process sequential and auditable—no agent free-for-alls.

```
┌─────────────────────────────────────────────────────────────┐
│                     user_ops_context.md                      │
│              (brand · business · channel · rules)           │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     Context Loader                          │
│              Loads context + memory + input                  │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ User & Scene  │ │    Channel    │ │    Memory     │
│   Analyst     │ │   Analyst     │ │   Context     │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        └─────────────────┴─────────────────┘
                          ▼
              ┌───────────────────────┐
              │   Bull/Bear Debate    │
              │  (Growth vs. Risk)    │
              └───────────┬───────────┘
                          ▼
              ┌───────────────────────┐
              │   Strategy Manager    │
              │  (Synthesis Agent)    │
              └───────────┬───────────┘
                          ▼
              ┌───────────────────────┐
              │   Execution Crew      │
              │ (5 planning agents)   │
              └───────────┬───────────┘
                          ▼
              ┌───────────────────────┐
              │    Risk Reviewer      │
              │  (Block / Modify /    │
              │   Approve)            │
              └───────────┬───────────┘
                          ▼
              ┌───────────────────────┐
              │   User Ops Director   │
              │  (Final Decision)    │
              └───────────┬───────────┘
                          ▼
              ┌───────────────────────┐
              │   Reflection Agent    │
              │ (Memory Candidate)    │
              └───────────────────────┘
```

### The Rulebook

- **Flow controls sequence.** Agents don't improvise.
- **State is explicit.** Every stage writes to `state.json`—no context lost in chat history.
- **Memory requires approval.** Reflection output is a candidate, not an auto-write.
- **Structured output only.** JSON schemas under every agent's output.

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/q445rxdfd5-alt/user-ops-swarm.git
cd user-ops-swarm

# Install dependencies
pip install -r requirements.txt

# Run a sample campaign
python main.py --input examples/summer-new-product.md
```

### Requirements

- Python 3.11+
- CrewAI
- Pydantic
- PyYAML

---

## Example Use Cases

### Summer New-Product Launch

> *Launch a new summer product. Goals: new customer acquisition, delivery orders, member signups. Constraints: protect margins, keep store operations simple.*

The swarm will surface target segments, channel roles, growth arguments, risk objections, a revised campaign strategy, and a final director decision—complete with execution plan and risk review.

### Delivery Order Decline Diagnosis

> *Delivery orders dropped 15% over the past two weeks. Is it platform algorithm changes, pricing, product quality, fulfillment, or competitor activity?*

The swarm runs signal analysis across all channels, generates hypotheses, and produces a prioritized action plan.

### Dormant Member Reactivation

> *We want to bring back members who haven't ordered in 60+ days—without training them to wait for coupons.*

The swarm designs a tiered reactivation strategy, balances offer risk vs. lifetime value, and reviews brand impact.

---

## What This Is NOT

This project does **not** include:

- SaaS UI or web dashboard
- Real-time CRM or POS integration
- Automatic campaign deployment
- Coupon issuance or ad buying
- Multi-tenant team features
- BI analytics or reporting

It is a **local prototype**. Your job is to validate whether the agent organization mechanism works—not to run production operations through it.

---

## Tech Stack

| Layer | Current | Future |
|-------|---------|--------|
| Runtime | CrewAI | LangGraph (if needed) |
| State | JSON files | Postgres + pgvector |
| Workflow | CrewAI Flow | Temporal (production) |
| Interface | CLI + Markdown | FastAPI + Next.js console |
| Memory | Human-reviewed candidates | Persistent vector store |

---

## Roadmap

| Phase | What's Next |
|-------|-------------|
| **Phase 0** | Spec complete, first example run working |
| **Phase 1** | Full CrewAI local prototype with all agents, schemas, example inputs |
| **Phase 2** | Evaluation harness: single agent vs. swarm comparison, rubrics, failure case library |
| **Phase 3** | Runtime upgrade to LangGraph if CrewAI control is insufficient |
| **Phase 4** | Control plane: run browser, state viewer, human approval workflow, memory manager |

---

## Contributing

This is a prototype-first project. If you want to contribute:

1. Open an issue to discuss the agent design or workflow
2. Submit PRs for schema improvements, example inputs, or evaluation metrics
3. Star the repo if this approach to bounded AI teams resonates with you

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Credits

Built with [CrewAI](https://www.crewai.com/) as the agent orchestration layer.

Inspired by institutional decision-making systems, trading agent architectures, and the messy reality of restaurant user operations.
