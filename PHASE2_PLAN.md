# Phase 2 — Red vs Blue Evaluation System

## Why This Exists

Current evaluator is keyword-based. 15 cases all score 4.77 because keyword density is similar. No real quality discrimination.

Red vs Blue adds adversarial evaluation:
- Red team: agents that challenge and break the system's output
- Blue team: multi-role reviewers from different perspectives
- Multi-dimension: evaluator can't be fooled by keyword stuffing

## Architecture

### Red Team (Attack Layer)
```
竞争者_红队 (Competitor Red)
  → 模拟竞品攻击：价格战 / 差评攻击 / 平台封杀
  → 生成"你会输"的场景，推到 bull/bear 输入
  → 检验系统在没有明显优势时如何决策

危机_红队 (Crisis Red)
  → 模拟突发情况：食安事件 / 舆情爆发 / 平台算法突变
  → 生成"必须快速决策"的场景
  → 检验决策链路在时间压力下的质量

边界_红队 (Boundary Red)
  → 模拟边际场景：预算=0 / 时间=0 / 团队不足
  → 生成"资源耗尽"的场景
  → 检验系统在约束下是否能找到非对称解
```

### Blue Team (Review Layer)
```
质量_蓝队 (Quality Blue)
  → 从 output 质量角度审核：结构完整性 / 逻辑一致性 / 执行可行性
  → 输出评分 + 具体问题列表

风险_蓝队 (Risk Blue)
  → 从风险角度审核：已知风险识别 / 未知风险盲区 / 缓释措施充分性
  → 输出 risk_score + kill_switch 有效性

战略_蓝队 (Strategy Blue)
  → 从战略角度审核：与 brand context 一致性 / 长期价值 vs 短期冲动 / 竞争护城河
  → 输出 strategic_alignment_score
```

## Red vs Blue Flow

```
[原始 Case Input]
       │
       ▼
   [红队攻击]
  竞争者/危机/边界红队
  生成对抗性增强输入
       │
       ▼
  [Swarm 执行]
  标准 9-step flow
  (Bull/Bear/Risk/Director/Reflection)
       │
       ▼
  [蓝队审核]
  quality + risk + strategy 三维评分
       │
       ▼
  [评分输出]
  {
    "red_scenario": "...",
    "red_attack_type": "price_war|food_safety|platform_ban|resource_exhaustion",
    "blue_quality_score": 1-5,
    "blue_risk_score": 1-5,
    "blue_strategy_score": 1-5,
    "pass": true/false,
    "key_findings": [...],
    "swarm_failures": [...],
    "improvement_areas": [...]
  }
```

## Implementation

### New Files

| File | Purpose |
|------|---------|
| `src/agents/competitor_red.yaml` | Simulates competitor attacks |
| `src/agents/crisis_red.yaml` | Simulates crisis scenarios |
| `src/agents/boundary_red.yaml` | Simulates resource exhaustion |
| `src/agents/quality_blue.yaml` | Quality reviewer |
| `src/agents/risk_blue.yaml` | Risk reviewer (similar to risk_reviewer but post-output) |
| `src/agents/strategy_blue.yaml` | Strategic alignment reviewer |
| `src/tasks/red_attack.yaml` | Task for red team generation |
| `src/tasks/blue_review.yaml` | Task for blue team multi-dimension review |
| `src/flow/red_blue_flow.py` | Orchestrates red → swarm → blue flow |

### CLI

```bash
python main.py --input <case> --mode red-blue
# Output: runs/<id>/red_blue_report.json
```

## Success Criteria

- Red team generates scenario variants that stress test the system
- Blue team produces multi-dimension scores that actually differ across cases
- System fails on some red attacks → this is the point, not a bug
- Evaluation score variance: stddev > 0.3 across 15 cases (vs current 0.00)