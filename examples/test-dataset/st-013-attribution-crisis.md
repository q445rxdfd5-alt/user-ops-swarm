# ST-013: Cross-Platform Attribution — Are WeChat Campaigns Actually Working?

> **Priority**: HIGH — CFO wants answer before Q3 budget allocation, meeting May 28
> **Submitted by**: CFO + Analytics Lead
> **Date**: 2026-05-12

---

## Situation

Over the past 3 months (Feb-April 2026), we've spent **¥62,000 on WeChat Moments and WeChat Banner advertising** targeting our existing member base and lookalike audiences in the Shanghai delivery radius.

Reported WeChat campaign metrics:
- **Total spend**: ¥62,000
- **Impressions**: 2.1M
- **Click-through rate**: 8.3% (175,000 clicks)
- **WeChat merchant page visits**: 142,000
- **WeChat checkout initiated**: 28,000

Reported in-store / delivery results from WeChat campaigns:
- **Attributed delivery orders**: 3,800 (from campaign UTM-tagged links)
- **Attributed GMV**: ¥159,600 (3,800 orders × ¥42 AOV)
- **Attributed gross margin**: ¥97,356 (61%)

However, our store operations team reports that their daily order volume didn't meaningfully increase during the campaign period. The regional store manager (Chen) says: "WeChat campaigns bring the wrong people — deal seekers who order once and never come back."

The CFO's question: **Did the WeChat campaigns generate a positive ROI, and should we increase or decrease Q3 budget?**

Attribution analysis challenges:
- WeChat and Meituan operate on separate user identity systems — WeChat user can't be matched to Meituan order without a unified member ID
- Our in-store pickup customers (40% of volume) are easier to track but represent a different behavior pattern
- UTM-tagged WeChat checkout has only 16% completion rate (most users click but don't buy)
- The 175,000 clicks that didn't convert via UTM may still have influenced brand awareness and Meituan orders (halo effect)

---

## Goals (Ranked)

1. Determine whether WeChat campaigns generated ≥ 1.5x ROI (¥1.5 return per ¥1 spent)
2. Understand why attributed WeChat GMV (¥159,600) doesn't match observable in-store volume increase
3. Recommend Q3 budget allocation (currently ¥60,000/quarter, propose increase/decrease/maintain)
4. Identify attribution improvements needed to make future measurement reliable
5. Resolve the internal disagreement about whether WeChat drives real incremental volume or just deal-seekers

---

## Constraints

- **Data gap**: We cannot deterministically link WeChat users to Meituan/Ele.me orders without a unified loyalty ID
- **Time constraint**: CFO needs a recommendation by May 25 for the May 28 budget meeting
- **Historical comparison**: WeChat campaign spend in Q3 2025 (¥45,000) correlated with a 12% increase in monthly delivery orders. CFO used that as justification for increasing to ¥62,000 in Q1 2026. But Q1 2026 delivery orders only grew 4%.
- **Team trust issue**: Store operations doesn't believe in WeChat campaigns. Marketing believes in them. Both have partial data.

---

## Team Positions

**Marketing Lead (Lin):**
> "The attribution gap is a measurement problem, not a campaign problem. Of course WeChat-to-Meituan attribution fails — they're different ecosystems. What we can measure: brand search volume on Meituan increased 31% during the campaign period. Our store rating improved from 4.4 to 4.6 (campaign awareness effect). And the 28,000 checkout initiations represent 16% conversion = 4,480 potential orders we know about, plus the halo of people who saw the ad and searched for us directly on Meituan. If we assume 1 additional Meituan order per 100 impressions (lift-based attribution): 2.1M impressions × 1% × ¥42 AOV = ¥882,000 in halo-effect GMV. We can't prove it but the correlation is strong. My recommendation: increase to ¥80,000 in Q3 and fix the attribution problem by requiring WeChat users to log in with their Meituan/Ele.me member ID."

**Analytics Lead (Dr. Zhang):**
> "Marketing is doing magic math. Brand lift is real but unmeasurable at this data quality level. What I can say definitively: the 3,800 UTM-attributed orders at ¥42 AOV = ¥159,600 GMV, 61% margin = ¥97,356 gross margin. Against ¥62,000 spend = 1.57x ROI. That's positive but below our 2x threshold for marketing channels. And the 4.5% click-to-order conversion rate (28K → 3.8K) is below industry benchmark of 7%. The problem is WeChat checkout UX — users click but abandon because the WeChat merchant page doesn't integrate with their delivery address book. Fix the UX first, then scale spend. I recommend maintaining ¥60,000 but restructuring: ¥40,000 on creative/testing (fix CTR problem) and ¥20,000 on attribution infrastructure."

**CFO (Li):**
> "I need a clear number for May 28. My board presentation says 'WeChat campaign ROI is X.' If X < 1.5, I'm recommending a budget cut to ¥30,000. If X ≥ 1.5, I'm recommending ¥80,000. If we can't measure it, I default to zero — no spend. The store operations complaint is also my complaint. We increased spend 38% (from ¥45K to ¥62K) and saw delivery orders grow 4% (from baseline). That's not a meaningful return. At minimum I need a credible estimate with confidence bounds."

---

## Options Under Review

**Option A — "Maintain Spend, Fix Attribution"**
- Keep Q3 WeChat budget at ¥60,000.
- Allocate ¥20,000 to fixing WeChat checkout UX (UTM completion rate goal: 16% → 25%).
- Restructure remaining ¥40,000 toward A/B testing creative.
- Delay ROI conclusion until attribution is fixed (Q4 decision).
- Communicate to CFO: "Inconclusive — invest in measurement before scaling."

**Option B — "Halo Attribution Model"**
- Accept that direct attribution is impossible; use a multi-touch model.
- Estimate: 1% of non-converting impressions still drive Meituan brand search lift = ¥882,000 halo GMV potential.
- Adjusted total GMV attribution: ¥159,600 direct + ¥200,000 estimated halo = ¥359,600.
- ROI = ¥359,600 / ¥62,000 = 5.8x. Recommend increasing to ¥80,000.
- Risk: CFO may reject halo math without empirical validation.

**Option C — "Cut to Minimum, Test-and-Learn"**
- Cut Q3 budget to ¥25,000 (experimentation only).
- Use savings (¥35,000) to fund a controlled A/B test: run WeChat campaigns in Pudong district only, measure Meituan order lift in Pudong vs. non-campaign Shanghai areas.
- 8-week test, results by July 31.
- Risk: Marketing loses face; test may be inconclusive.

---

*What is the recommended attribution approach and Q3 budget recommendation?*