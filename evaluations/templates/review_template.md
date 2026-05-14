# Human Review Template — QSR Swarm Evaluation

---

## Run Metadata

- **Review ID**: `rev_XXXXXXXX`
- **Date**: `YYYY-MM-DD`
- **Reviewer**: _______________________________
- **Swarm Version**: _______________________________
- **Input Brief**: _______________________________

---

## Artifact Review Checklist

### 1. Context Summary (`context_summary.yaml`)
- [ ] All user-provided facts correctly extracted
- [ ] No hallucinated context from prior runs
- [ ] Gaps in user input acknowledged
- [ ] Scene classification consistent with input

### 2. Strategy Synthesis (`strategy_summary.yaml`)
- [ ] Coherent recommendation aligned with brief
- [ ] Bull/Bear arguments balanced and evidence-based
- [ ] No internal contradictions
- [ ] Risk considerations integrated, not siloed
- [ ] Scope matches original request (no creep)

### 3. Risk Review (`risk_review.yaml`)
- [ ] All CRITICAL risks identified
- [ ] CRITICAL risks block or gate execution
- [ ] Mitigation recommendations actionable
- [ ] Compliance risks addressed

### 4. Campaign/Content Deliverables
- [ ] Output matches approved strategy
- [ ] Platform requirements accurate and cited
- [ ] Deliverable count within expected scope
- [ ] Quality meets production standard

### 5. Final Decision (`final_decision.yaml`)
- [ ] Traces to approved strategy (provenance)
- [ ] No contradiction with synthesis phase
- [ ] Rationale documented
- [ ] No unexplained reversals

### 6. Memory Candidates (`memory_candidates/`)
- [ ] Schema valid (no corruption)
- [ ] Facts verifiable
- [ ] No contradictory stored memories
- [ ] Approved candidates marked for persistence

---

## Decision Traceability

| Phase | Artifact | Approved? | Notes |
|-------|----------|-----------|-------|
| Context | | | |
| Synthesis | | | |
| Risk Review | | | |
| Final Decision | | | |

---

## Overall Assessment

**Status**: [ ] PASS  [ ] CONDITIONAL PASS  [ ] FAIL

**Primary Failure Category** (if applicable):
- [ ] conflict_collapse
- [ ] risk_miss
- [ ] execution_drift
- [ ] decision_contradiction
- [ ] memory_corruption

---

## Memory Approval

- [ ] Memory candidates reviewed
- [ ] Conflicting memories reconciled
- [ ] Approved for persistence: [ ] YES  [ ] NO
- [ ] Approved candidates: _______________________________

---

## Notes

1. ___________________________________________________________________
2. ___________________________________________________________________
3. ___________________________________________________________________

---

**Reviewed by**: _______________________  **Date**: ____________
