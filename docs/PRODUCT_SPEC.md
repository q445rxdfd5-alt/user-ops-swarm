# user-ops-swarm 产品规格

## 一、输入格式规范

### 场景文件（Scenario File）

用户填写的任务描述文件，Markdown 格式。

**必填字段：** 核心情况（1段文字）
**推荐填写：** 关键数据表格 + 优先级 + 约束条件
**可选填写：** 历史参考 + 已有方案

示例文件：`examples/TEMPLATE_scenario.md`

---

## 二、输出文档规范（8 份）

### 01 — 上下文摘要（context_summary）

| 字段 | 说明 |
|---|---|
| 场景类型 | 问题分类 |
| 核心挑战 | 一句话描述 |
| 关键指标快照 | 数据表格 |
| 约束条件 | 预算/时间/红线 |
| 历史教训 | memory 中的相关经验 |
| 分析置信度 | 高/中/低 |

### 02 — 机会分析（opportunity_analysis）

| 字段 | 说明 |
|---|---|
| 用户分群 | 核心用户类型 |
| 需求驱动因素 | 需求背后的动机 |
| 渠道表现矩阵 | 各渠道的当前表现 |
| 最大缺口 | 机会最大的点 |

### 03 — 多空辩论（bull_bear_debate）

格式：**Bull 立场 → Bear 反驳**

- Bull：针对哪些具体论点，提出了什么激进方案
- Bear：引用 Bull 的具体说法，逐条反驳，给出风险证据

### 04 — 策略整合（strategy_summary）

| 字段 | 说明 |
|---|---|
| 采纳的 Bull 论点 | 引用原文，说明为什么采纳 |
| 采纳的 Bear 论点 | 引用原文，说明为什么采纳 |
| 拒绝的论点 | 说明拒绝原因 |
| 整合后策略 | 优先级排序的策略列表 |
| 置信度 | 0-10 分 |

### 05 — 执行计划（execution_plan）

| 板块 | 内容 |
|---|---|
| 活动规划 | 阶段 + 时间线 + 预算分配 |
| 内容计划 | 各渠道文案主题 |
| 配送设计 | 履约架构 + 承诺时限 |
| 团购机制 | 折扣结构 + 裂变路径 |
| 会员运营 | 等级设计 + 留存钩子 |

### 06 — 风险审查（risk_review）

| 字段 | 说明 |
|---|---|
| 已识别风险 | 含概率 × 影响评级 |
| BLOCK 状态 | 是否触发 BLOCK |
| 缓释措施 | 具体行动 |
| kill switch | 触发条件 |

### 07 — 最终决策（final_decision）

| 字段 | 说明 |
|---|---|
| 决策结果 | approve / revise / reject / test_only |
| 决策溯源 | 引用了哪些 Bull/Bear/Risk 论点 |
| 行动要求 | 下一步具体动作 |
| 决策置信度 | very_confident / confident / neutral / uncertain |

### 08 — 经验候选（memory_candidate）

| 字段 | 说明 |
|---|---|
| 洞察类型 | 问题类型 / 决策模式 / 执行经验 |
| 核心内容 | 可复用的结论 |
| 适用场景 | 何时可以再次使用 |
| 证据基础 | 来自哪一次运行 |
| 优先级 | high / medium / low |

---

## 三、导出格式

### 格式一：执行摘要（Markdown，单页）

面向运营人员，提炼关键决策和行动清单，不含分析过程。

- 包含：决策结果、理由、执行阶段（含日期和目标）、预算分配、风险级别
- 阶段名称取自 `staged_milestones` 中的日期字段（如 "May 17"）
- 预算显示总预算 + 分项明细

生成方式：`python tools/export_report.py --run-id <id> --format md`
输出路径：`reports/<run-id>-report.md`

### 格式二：结构化数据（JSON）

面向技术集成，完整保留所有结构化字段。

生成方式：`python tools/export_report.py --run-id <id> --format json`
输出路径：`reports/<run-id>-decision.json`

### 格式三：完整导出

同时生成 md + json。

生成方式：`python tools/export_report.py --run-id <id> --format all`（默认）
输出路径：`reports/<run-id>-report.md` + `reports/<run-id>-decision.json`

---

## 四、品牌背景模板

品牌背景文件定义了分析的品牌上下文，所有 Agent 在第一步读取。

模板路径：`context/user_ops_context.md`

**填写说明：**

```
## Brand Identity
- Brand Name：（品牌名称）
- Brand Positioning：（一句话定位）
- Brand Voice：（语气风格）
- Core Values：（核心价值）

## Business Overview
- Store Count：（门店数量）
- Primary Markets：（主要市场）
- Average Ticket Size：（客单价）
- Peak Hours：（高峰时段）

## Channel Configuration
- Delivery Platforms：（外卖平台及份额）
- Commission structure：（各平台佣金率）
- Group Buying：（团购机制）
- Membership Program：（会员体系）

## Financial Constraints
- Margin floor：（毛利率红线）
- Budget range：（预算区间）
- Discount tolerance：（折扣容忍度）
```

---

## 五、CLI 命令规范

```bash
# 基本运行
python main.py --input <场景文件.md> --run-id <唯一ID>

# 指定品牌背景
python main.py --input <场景.md> --context <品牌背景.md> --run-id <ID>

# 指定经验库
python main.py --input <场景.md> --memory <经验库.md> --run-id <ID>

# 干跑（验证格式，不调用 LLM）
python main.py --input <场景.md> --dry-run

# 导出报告
python tools/export_report.py --run-id <ID> --format md|json|all
python tools/export_report.py --run-id <ID>  # 默认导出 all

# 经验审核
python tools/memory_review.py --run-id <ID>   # 交互式审核
python tools/memory_review.py --run-id <ID> --approve  # 全部批准
python tools/memory_review.py --run-id <ID> --dry-run   # 预览不写入
```
