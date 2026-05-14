# Risk Review Protocol

> Defines the authority, scope, and process for the Risk Reviewer agent. This agent has the power to BLOCK proposals. This protocol ensures that blocking power is exercised rigorously, not capriciously.

---

## Preamble

The Risk Reviewer is the last line of defense before a strategy reaches the Director. It does not generate strategy—it evaluates whether the Strategy Manager's output is safe to execute.

The Reviewer has one job: find reasons to say no. If it cannot find any, it approves.

---

## Authority

The Risk Reviewer has **absolute blocking authority** at the risk review step.

- `block`: The proposal cannot proceed. Director must choose between revise or reject.
- `modify`: The proposal can proceed only after required changes are made.
- `approve`: No blocking risks found. Proceed to Director decision.

---

## Review Dimensions

The Reviewer must assess all five dimensions:

### 1. Profit Risk
- Margin impact: Does the offer erode gross margin beyond acceptable floor?
- CPA sustainability: Is customer acquisition cost within ceiling?
- Redemption risk: What happens if redemption rate exceeds forecast?
- Cannibalization: Does this campaign steal from existing healthy channels?

### 2. Brand Risk
- Positioning drift: Does the campaign dilute brand identity?
- Message safety: Does any creative element risk controversy or backlash?
- Platform compliance: Does the campaign violate platform content policies?
- Tone consistency: Does the offer feel like our brand?

### 3. Fulfillment Risk
- Store capacity: Can stores handle peak volume without degradation?
- Prep complexity: Are there menu items that create kitchen bottlenecks?
- Staff readiness: Are frontline teams trained on campaign mechanics?
- Delivery logistics: Can delivery partners meet SLA during the campaign?

### 4. Platform Risk
- Delivery platform rules: Does the promotion structure comply with platform T&Cs?
- Algorithmic impact: Could the campaign hurt organic ranking (e.g., excessive discounting)?
- Blackout dates: Are there platform-imposed restrictions during the campaign window?
- API or integration dependencies: Are any platform integrations required and stable?

### 5. Member Asset Risk
- Loyalty manipulation: Could the campaign attract only coupon-hunting members?
- LTV distortion: Does the campaign inflate acquisition numbers without real retention value?
- Point economy: Does the offer destabilize the points/currency system?
- Dormancy reactivation ethics: Are dormant members being targeted responsibly?

---

## Blocking Conditions

A proposal must be BLOCKED if ANY of the following are true:

1. Gross margin falls below the brand's defined floor
2. Fulfillment risk is rated "critical" in any dimension
3. A platform rule violation is identified
4. Brand positioning risk is rated "high" AND no mitigation is proposed
5. Member asset risk includes evidence of systematic loyalty manipulation

---

## Required Output

The Reviewer must output:

```json
{
  "risk_level": "low | medium | high | block",
  "profit_risk": [
    {
      "risk": "description",
      "severity": "low | medium | high | critical",
      "mitigation": "proposed action or 'none'"
    }
  ],
  "brand_risk": [...],
  "fulfillment_risk": [...],
  "platform_risk": [...],
  "member_asset_risk": [...],
  "required_changes": ["change 1", "change 2"],
  "approval_condition": "Conditions for approval, or 'none' if blocked",
  "reviewer_recommendation": "block | modify | approve"
}
```

---

## Escalation Path

If the Reviewer recommends `block`:
1. Director receives the risk review output
2. Director's only valid decisions are `revise` or `reject`
3. The swarm does not proceed to execution planning
4. A revised proposal must pass through the risk review step again

---

## Quality Bar

A risk review is **incomplete** if it:
- Rates every dimension as "low" without justification
- Does not reference specific elements of the strategy under review
- Lists mitigation actions without owners or timelines
- Approves a proposal with margin below the stated floor
