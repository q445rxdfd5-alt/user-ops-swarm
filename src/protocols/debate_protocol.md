# Debate Protocol

> Defines the rules of engagement for the Bull vs. Bear debate. These rules govern how the two agents interact, what constitutes a valid argument, and how the Strategy Manager absorbs the output.

---

## Preamble

The Bull/Bear debate is not a friendly discussion. It is a structured adversarial process designed to surface the real tensions in any growth proposal. The Bull agent represents the relentless pursuit of growth; the Bear agent represents the relentless resistance to unchecked risk.

Neither agent should win. The goal is a sharpened strategy that has survived genuine scrutiny.

---

## Role Definitions

### Growth Bull Agent

**Mandate**: Make the strongest possible case for aggressive growth.

- Argue for new customer acquisition, GMV expansion, order volume, member signups, and brand awareness
- Ground optimism in data, benchmarks, or specific hypotheses
- Explicitly address and rebut the Bear's likely objections
- Do not concede weakness without a counter-argument

**Constraints**:
- Must specify expected upside with quantified targets
- Must identify required resources (budget, time, organizational support)
- Must explain why the conservative position underestimates opportunity

### Growth Bear Agent

**Mandate**: Identify every way this proposal could hurt the business.

- Challenge margin assumptions, fulfillment capacity, brand positioning, and member asset quality
- Propose specific blockers or required modifications
- Do not argue against growth in principle — argue against sloppy execution
- Acknowledge valid Bull points; redirect them toward safer structures

**Constraints**:
- Must provide at least one specific risk scenario per major objection
- Must identify items that must change before approval
- Must distinguish between "block entirely" and "block until modified"

---

## Debate Rules

### Rule 1: Arguments Must Be Specific

Generic statements like "this is risky" or "this will drive growth" are not valid arguments. Each statement must include:
- The specific claim
- The evidence or reasoning behind it
- The consequence if the claim is wrong

### Rule 2: Bull Must Respond to Bear

The Bull's output is incomplete if it does not directly address the Bear's likely objections. The Strategy Manager will penalize Bull outputs that ignore known risks.

### Rule 3: Bear Must Provide Alternatives

A valid Bear objection includes either:
- A modification that preserves the growth goal while reducing risk, OR
- A clear blocker with explicit conditions for unblocking

Merely saying "no" without a path forward is a weak Bear output.

### Rule 4: Both Sides Must Quote the Strategy

Every argument must reference specific elements of the proposed strategy, not abstract principles.

### Rule 5: The Debate Heat Score

The Bull's output must include a self-assessed "debate heat" score (1-10) indicating how contentious this proposal is expected to be. A heat score below 4 means the proposal hasn't been seriously challenged.

---

## Strategy Manager Absorption Rules

The Strategy Manager's job is not to find a middle ground. It is to:

1. **Adopt** points from either side that strengthen the final strategy
2. **Reject** points that are based on flawed reasoning or wrong premises
3. **Merge** conflicting recommendations into a synthesis that is better than either
4. **Defer** legitimate but timing-inappropriate suggestions to a future phase

The Manager must list explicitly:
- Which Bull points were adopted (and why)
- Which Bear points were adopted (and why)
- Which points were rejected (and why)
- Which points were deferred (and why)

Silence on a point is not adoption.

---

## Output Format

Both Bull and Bear must output structured JSON:

**Bull**:
```json
{
  "growth_thesis": "...",
  "recommended_actions": [...],
  "expected_upside": [...],
  "required_resources": [...],
  "arguments_against_conservatism": [...],
  "debate_heat": 7
}
```

**Bear**:
```json
{
  "bear_thesis": "...",
  "key_objections": [...],
  "risk_scenarios": [...],
  "must_change_items": [...],
  "blockers": [...]
}
```

---

## Evaluation Criteria

A debate is considered **high quality** when:
- Bull identifies 3+ specific growth levers
- Bear identifies 3+ genuine risks that Bull did not address
- At least 2 Bull arguments are modified after Bear's challenges
- The Strategy Manager rejects at least 1 point from each side
- The final strategy is measurably different from what Bull originally proposed
