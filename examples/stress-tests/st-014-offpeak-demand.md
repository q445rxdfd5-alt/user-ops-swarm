# ST-014: Off-Peak Demand Generation — 14:00-17:00 Trough Recovery

> **Priority**: MEDIUM — Kitchen at 40% idle capacity, ¥0 incremental budget available
> **Submitted by**: Regional Ops + Growth
> **Date**: 2026-05-11

---

## Situation

Our Shanghai store operates at **96-100% kitchen capacity during 11:00-14:00** (lunch peak) and **18:00-21:00** (dinner peak). But from **14:00-17:00, we are at 38-42% kitchen utilization** — a daily idle window of approximately 3 hours where our kitchen team and delivery infrastructure are significantly underused.

Current metrics for the 14:00-17:00 window:
- **Average orders**: 28 orders/hour (vs. 72 orders/hour at lunch peak)
- **AOV**: ¥34 (vs. ¥46 at lunch — off-peak customers order less)
- **Delivery coverage**: Meituan algorithm deprioritizes us during off-peak (low expected conversion = low placement)
- **Hourly GMV**: 28 × ¥34 × 61% margin = **¥582/hour**

At full lunch-peak capacity utilization for those 3 hours:
- **Target orders**: 60 orders/hour (still below 72 to maintain quality buffer)
- **Hourly GMV target**: 60 × ¥34 × 61% = **¥1,244/hour**
- **Incremental GMV opportunity**: ¥1,244 - ¥582 = ¥662/hour × 3 hours = **¥1,986/day** = **¥59,580/month**

The problem: our delivery platform (Meituan) has a dynamic ranking algorithm that deprioritizes stores during low-conversion windows. Even if we run a promotion, we won't get surfaced to users unless we improve our off-peak conversion metrics. And we have **¥0 incremental budget** — any off-peak campaign must be cost-neutral (no discounts, no paid placement).

---

## Goals (Ranked)

1. Increase 14:00-17:00 order volume from 28 to ≥ 55 orders/hour
2. Maintain or improve AOV (currently ¥34, off-peak customers buy less)
3. Improve Meituan off-peak ranking signal without paid placement
4. Drive ≥ 200 incremental orders/day in the trough without adding kitchen staff or delivery costs
5. Develop a repeatable off-peak playbook that can be applied to new stores

---

## Constraints

- **Budget**: ¥0 for paid campaigns, paid placement, or discounts
- **Platform algorithm**: Meituan ranking is conversion-weighted — we need to show improved conversion rate in the 14:00-17:00 window to earn organic placement
- **Delivery time**: Office workers in nearby buildings go back to work after 13:30. We need to understand who the 14:00-17:00 customer actually is.
- **AOV**: Cannot use discounts. Any volume increase must come from customer behavior change, not price incentive.
- **Fulfillment cap**: 180 orders/day total. We're at 180 during peak. Off-peak volume can't cannibalize peak capacity.
- **Kitchen buffer**: We need to keep 20% kitchen capacity in reserve for the 17:00 dinner surge.

---

## Team Positions

**Growth Manager (Chen):**
> "The off-peak customer is an office worker who skipped lunch, a delivery-to-office order for a late meeting, or a walk-in from the IFC mall tourists. These are not our core office-worker customers. We need to capture them differently. My idea: partner with nearby office building WeChat groups — there are 22 buildings in our delivery radius, and many have internal 'lunch group buy' WeChat groups. If we offer a '3-person minimum' afternoon office delivery option (a lighter meal set at ¥28, not competing with dinner), we could drive group orders during off-peak. No discount needed if the product is positioned as a convenient 'afternoon refuel' option rather than a discounted meal deal. The group dynamic increases AOV to ¥28 × 3 = ¥84 per group, vs. ¥34 solo order."

**Regional Ops Manager (Chen):**
> "Group orders are complicated to fulfill and require coordination. Our kitchen is already stressed during peak — I don't want group orders coming in at 14:00 when I'm still clearing lunch. Here's what actually works: a 'flash menu' of 3-4 items available ONLY from 14:00-17:00. Something unique that creates urgency and gives people a reason to order. Think: a limited afternoon snack/sides combo that's not on the regular menu. This creates FOMO, doesn't cannibalize dinner orders (it's a different item), and gives Meituan something to surface as a 'limited time' deal. No discount needed if the item is positioned correctly. I can add one new prep station (¥2,400 one-time equipment) to handle the off-peak items without touching core kitchen flow."

**Brand & Marketing (Lin):**
> "Both of you are thinking transactions. The real issue is that Meituan's algorithm doesn't know we want to be surfaced at 14:00-17:00. The fix is simple: manually boost our conversion rate signal through a 'loyalty program' mechanism. Offer our WeChat members (18,000 Shanghai) a 'Surprise Menu' notification at 13:45 every day — 30 minutes before off-peak starts — with a link to the limited off-peak menu. The click-through on WeChat member notifications is 23% (4,140 potential clicks/day). Even 5% conversion = 207 orders/day, and these come with a pre-committed delivery address (member profile). Meituan sees high conversion from these orders and upgrades our off-peak ranking organically. No budget, no discount, just better use of owned channels."

---

## Options Under Review

**Option A — "Afternoon Office Group Order"**
- Launch a "3-Person Afternoon Refuel" set at ¥28/person × 3 minimum.
- Partner with 10 office building WeChat groups (no cost, just coordination).
- Estimated: 15 group orders/day × ¥84 AOV = ¥1,260/day GMV, ¥769/day gross margin.
- Kitchen concern: groups arrive at unpredictable times. May need order batching.

**Option B — "Flash Menu + Prep Station"**
- Add 3-4 limited off-peak items (soup + sides + snack combo) to kitchen.
- ¥2,400 one-time prep station investment.
- No discount — flash items priced at normal margin.
- Estimated: +27 orders/hour × 3 hours = +81 orders/day = ¥2,754/day GMV, ¥1,680/day margin.
- Risk: new items require kitchen training and may slow down dinner prep transition.

**Option C — "WeChat Member Off-Peak Notification"**
- Daily 13:45 WeChat push to Shanghai members (4,140 potential reach at 23% CTR = 952 clicks → 5% conversion = 47 orders/day at ¥34 AOV).
- No new items, no discount, no prep station.
- Meituan ranking improves as off-peak conversion signal strengthens.
- Estimated: +47 orders/day = ¥1,598/day GMV, ¥975/day gross margin.
- Timeline: measurable ranking improvement in 2-3 weeks as algorithm reweights off-peak signal.

---

*What is the recommended off-peak demand generation strategy?*