# Memory Review Protocol

> Defines how the Reflection Agent generates memory candidates, and the human review process for approving entries into the persistent memory log.

---

## Preamble

The User Ops Swarm generates experience. That experience must be captured, but not automatically trusted.

Early-stage agent memory is a liability: confident errors accumulate and distort future outputs. This protocol ensures that every memory entry is reviewed by a human before it influences future runs.

---

## Reflection Agent Output

After each run, the Reflection Agent outputs a `memory_candidate` with this structure:

```json
{
  "scenario": "Brief description of the campaign or decision type",
  "segment": "Primary user segment targeted",
  "channel": "Primary distribution channel",
  "offer": "Key offer mechanic used",
  "lesson": "The single most important learning",
  "risk": "The risk that materialized or nearly materialized",
  "reuse_condition": "When this lesson should be applied again",
  "confidence": 0.0
}
```

The `confidence` score (0.0-1.0) is the Reflection Agent's self-assessed certainty that this lesson is generalizable.

---

## Memory Candidate Criteria

A candidate is **worth retaining** if it meets ALL of:
1. It describes a consequence, not just an observation
2. It includes a specific condition for reuse
3. Confidence score is ≥ 0.5
4. It does not contradict a higher-confidence existing memory

A candidate should be **rejected** if it:
1. Is generic advice applicable to any campaign
2. Describes an expected outcome that did occur (not a surprise)
3. Has confidence < 0.3
4. Conflicts with a higher-confidence existing entry

---

## Human Review Process

1. After each run, the `07_memory_candidate.md` artifact is written to the run directory
2. The operator reviews the candidate against the criteria above
3. If approved: the entry is added to `memory/memory_log.md` with reviewer initials and date
4. If rejected: the entry is moved to the "Rejected Candidates" section with rejection reason
5. If uncertain: the entry is deferred to the next review cycle

---

## Memory Log Structure

```markdown
## Active Memories

| ID | Date | Scenario | Lesson | Confidence | Owner |
|----|------|----------|--------|------------|-------|
| M001 | 2026-05-14 | Summer new-product launch | High-discount group deals attract coupon-chasers with <30-day repurchase | 0.8 | [Initials] |

## Rejected Candidates

| ID | Date | Scenario | Rejection Reason |
|----|------|----------|-----------------|
| R001 | 2026-05-14 | Delivery decline | Generic advice, applies to any campaign |
```

---

## Memory Integrity Rules

- **No auto-write**: The Reflection Agent never writes directly to `memory_log.md`
- **No confidence inflation**: The Reviewer should not increase confidence scores without evidence
- **Conflict resolution**: When a new entry conflicts with an existing one, the higher-confidence entry wins
- **Decay consideration**: Memory entries older than 12 months without reinforcement should be flagged for re-review
