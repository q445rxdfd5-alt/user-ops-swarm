# ST-001: Delivery Volume Decline — Meituan Ranking Crisis

> **Priority**: HIGH — Fulfillment rate dropped below threshold, ranking is sliding
> **Submitted by**: Regional Ops Manager (Shanghai)
> **Date**: 2026-05-10

---

## Situation

Our Shanghai cluster (22 stores) has seen delivery volume drop 14% WoW over the past two weeks. Root cause: fulfillment rate fell to 87% after a new store opening in Pudong created kitchen overload — delayed orders compounded, triggering Meituan's algorithm to deprioritize our ranking.

Current state as of May 10:
- **Fulfillment rate**: 87% (Meituan penalty threshold: 90%)
- **Meituan ranking**: Down from #3 to #11 in "Asian Wok" category, Shanghai
- **Daily delivery orders (Shanghai)**: 3,820 (was 4,440 two weeks ago)
- **Estimated revenue impact**: ~¥68,000/week at risk
- **Meituan rating**: 4.32 (1 star below safe zone)

The algorithm penalty is self-reinforcing: lower ranking → fewer impressions → worse conversion → more cancellations if we over-promise on ETAs.

---

## Goals (Ranked)

1. Restore Meituan ranking to top-5 in category within 3 weeks
2. Recover fulfillment rate to 93%+ by end of May
3. Stop revenue bleed from Shanghai cluster
4. Avoid aMeituan commission spike from emergency promotional spend

---

## Constraints

- **No deep-discount tactics**: Cannot go below 35% total discount (brand + platform)
- **No false urgency**: Cannot advertise "running out" or fake stockouts to manage demand
- **Store capacity is real**: Cannot promise faster ETAs than kitchen can deliver
- **Budget**: ¥15,000 emergency budget for this recovery — covers ad spend and any operational fixes only
- **Timeline**: Must see ranking recovery signal within 10 days or escalate to exec team

---

## What We Know Works

- Stores that maintain >93% fulfillment for 7 consecutive days recover ranking within 14 days (based on platform account manager feedback)
- Our Chengdu cluster ran a "quiet excellence" campaign in Q4 2025 — no discounting, just 98%+ fulfillment for 3 weeks — ranking recovered without any promotional spend
- Shortening delivery menu to top-20 items can reduce kitchen load by 25% without killing conversion

---

## What We Disagree On

**VP Marketing**: "Run a targeted 20%-off coupon flash sale on Meituan. Use margin to buy back ranking position. We did this in 2023 and it worked."

**Head of Supply Chain**: "Cut the delivery menu from 45 to 20 items immediately. Simplify kitchen, reduce errors, restore fulfillment. Discounts don't fix the root cause."

**Regional Ops Manager**: "Both of you are missing the human factor. Our Pudong store is understaffed — 3 open shifts per week. Hire 2 more people, give them 2 weeks to train, then watch fulfillment fix itself."

---

## Critical Question

What is the optimal combination of fulfillment recovery tactics, menu rationalization, and any limited promotional support — given the 10-day hard deadline, ¥15K budget, and the risk of algorithmic entrenchment if we do nothing?

---

## Success Metrics

| Metric | Current | Target (10-day) | Target (21-day) |
|--------|---------|-----------------|------------------|
| Fulfillment rate | 87% | 91% | 93% |
| Meituan ranking | #11 | #7 | Top 5 |
| Daily delivery orders | 3,820 | 4,100 | 4,440 |
| Meituan rating | 4.32 | 4.38 | 4.41+ |

---

## Anti-Goals (Things We Should NOT Do)

- Do not launch a national campaign while Shanghai is in crisis
- Do not blame the algorithm publicly
- Do not hire temporary gig workers for kitchen — quality inconsistency will worsen ratings
- Do not pause Meituan entirely — losing that revenue stream makes recovery harder

---

*Escalation deadline: May 20, 2026 if ranking not at #7 or better*
