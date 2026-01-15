# Agent 通信机制详解

## OpenAgents CollaboratorAgent 架构

### 基本原理

所有 CollaboratorAgent 都：

1. 连接到同一个 Network
2. 监听同一个频道（如 "general"）
3. 收到所有消息
4. 通过配置和指令决定是否响应

```
┌─────────────────────────────────────────┐
│           OpenAgents Network            │
│              (Port 8700)                │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
┌──────────────┐ ┌──────────┐ ┌──────────┐
│   daily-     │ │ analyst- │ │ creator- │
│  assistant   │ │  agent   │ │  agent   │
└──────────────┘ └──────────┘ └──────────┘
  react: true    react: true  react: true
```

### 消息流

```
用户发送消息
    ↓
Network 广播
    ↓
┌───────────────────────────────────────┐
│ 所有 agent 同时收到相同消息            │
└───────────────────────────────────────┘
    ↓           ↓           ↓
每个 agent 独立判断是否回复
    ↓           ↓           ↓
  LLM 分析    LLM 分析    LLM 分析
    ↓           ↓           ↓
  决定回复    决定沉默    决定沉默
```

## Agent 间通信方式

### 方式 1：间接通信（推荐）✅

**原理：** 通过用户作为中介

```
用户 → daily-assistant
daily-assistant → 引导用户说特定关键词
用户 → "分析师帮我分析"
analyst-agent → 检测到关键词，响应
```

**优点：**

- 用户保持控制权
- 流程清晰透明
- 避免 agent 循环对话
- 符合设计理念

**实现：**

```yaml
# daily-assistant 的引导语
"如果需要深度分析，可以说'分析师帮我分析'"
```

### 方式 2：直接 @ 提及（技术可行但不推荐）⚠️

**原理：** daily-assistant 在回复中包含 @analyst-agent

```python
# daily-assistant 发送消息
send_channel_message(
    channel="general",
    text="@analyst-agent 请分析用户的MBTI类型"
)
```

**问题：**

1. **循环风险**：analyst 回复后，daily 可能再次响应
2. **用户困惑**：看起来像 agent 在自己聊天
3. **控制权丧失**：用户失去对流程的控制
4. **指令不可靠**：LLM 可能不稳定地执行 @

**为什么不推荐：**

- 之前已经证明：LLM 指令过滤不可靠
- 两个 agent 都有 `react_to_all_messages: true`
- 很容易形成对话循环

### 方式 3：设置 react_to_all_messages: false（最可靠）✅

**原理：** analyst 和 creator 只响应明确的 @

```yaml
# analyst_agent.yaml
config:
  react_to_all_messages: false # 只响应 @
```

**优点：**

- 完全避免循环
- 明确的触发机制
- 技术上最可靠

**缺点：**

- 用户必须明确 @ 才能触发
- daily-assistant 无法代替用户触发

## 当前实现（方案 1）

### 配置

```yaml
# daily-assistant
react_to_all_messages: true
instruction: "引导用户说'分析师帮我分析'"

# analyst-agent
react_to_all_messages: true
instruction: "只响应包含'分析师'或'MBTI'等关键词的消息"

# creator-agent
react_to_all_messages: true
instruction: "只响应包含'创作者'或'制定计划'等关键词的消息"
```

### 工作流程

**步骤 1：用户日常对话**

```
用户: "最近压力很大"
→ daily-assistant: ✅ "我理解你的感受。[提供基础建议]"
→ analyst-agent: ❌ (没有分析关键词，保持沉默)
→ creator-agent: ❌ (没有计划关键词，保持沉默)
```

**步骤 2：daily-assistant 引导**

```
daily-assistant: "如果需要深度压力分析，可以说'分析师用HUMAN 3.0分析我'"
```

**步骤 3：用户触发专业分析**

```
用户: "分析师用HUMAN 3.0分析我"
→ daily-assistant: ❌ (检测到"分析师"，让专业agent处理)
→ analyst-agent: ✅ "📊 HUMAN 3.0 分析报告..."
→ creator-agent: ❌ (没有计划关键词)
```

**步骤 4：用户请求计划**

```
用户: "创作者，根据分析帮我制定计划"
→ daily-assistant: ❌ (检测到"创作者")
→ analyst-agent: ❌ (没有分析关键词)
→ creator-agent: ✅ "🎯 压力管理行动计划..."
```

## 关键词过滤机制

### Analyst Agent 触发词

```
必须包含以下之一：
- "分析师" / "@analyst-agent" / "analyst"
- "MBTI" / "Big Five" / "HUMAN 3.0"
- "框架分析" / "深度分析" / "心理分析"
- "职业发展分析" / "性格分析"
```

### Creator Agent 触发词

```
必须包含以下之一：
- "创作者" / "@creator-agent" / "creator"
- "制定计划" / "行动计划" / "执行计划"
- "帮我规划" / "给我方案" / "详细步骤"
```

### Daily Assistant 避让规则

```
如果消息包含：
- "分析师" / "analyst-agent" → 不回复或简短确认
- "创作者" / "creator-agent" → 不回复或简短确认
```

## 可靠性分析

### 方案 1（当前）：指令过滤

- **可靠性**：⭐⭐⭐ (70-80%)
- **优点**：灵活、用户友好
- **缺点**：LLM 可能误判
- **风险**：偶尔可能多个 agent 同时回复

### 方案 2：react_to_all_messages: false

- **可靠性**：⭐⭐⭐⭐⭐ (95%+)
- **优点**：技术上最可靠
- **缺点**：必须明确 @，不够灵活
- **风险**：几乎无风险

### 方案 3：单一 agent

- **可靠性**：⭐⭐⭐⭐⭐ (100%)
- **优点**：完全避免冲突
- **缺点**：失去专业化分工
- **风险**：无风险但功能受限

## 改进建议

### 短期（当前可行）

1. **优化关键词列表**：增加更多明确的触发词
2. **强化指令**：在 prompt 中多次强调过滤规则
3. **添加日志**：记录每次判断过程，便于调试

### 中期（需要开发）

1. **添加消息元数据**：标记消息来源（用户 vs agent）
2. **实现优先级机制**：专业 agent 优先级高于 daily
3. **添加确认机制**：agent 回复前先确认是否应该回复

### 长期（架构改进）

1. **实现真正的 agent 调用**：类似函数调用机制
2. **添加协调层**：专门的 coordinator 分配任务
3. **实现状态机**：明确的对话状态管理

## 测试场景

### 场景 1：正常分工 ✅

```
用户: "你好"
→ daily: "你好！有什么可以帮助你的？"

用户: "分析师，用MBTI分析我"
→ analyst: "📊 MBTI分析报告..."

用户: "创作者，制定计划"
→ creator: "🎯 行动计划..."
```

### 场景 2：边界情况 ⚠️

```
用户: "帮我分析一下这个问题"
→ 可能触发：daily（"分析"太模糊）
→ 不应触发：analyst（没有明确框架）

用户: "我需要一个计划"
→ 可能触发：daily（"计划"太模糊）
→ 不应触发：creator（没有明确请求）
```

### 场景 3：冲突情况 ❌

```
用户: "分析师和创作者都来帮我"
→ 可能触发：analyst + creator（同时响应）
→ 解决：在指令中说明"如果同时提到多个agent，只有第一个提到的响应"
```

## 最佳实践

### 用户使用指南

1. **日常对话**：直接说话，daily-assistant 会回复
2. **需要深度分析**：明确说"分析师"或框架名称
3. **需要详细计划**：明确说"创作者"或"制定计划"
4. **一次一个请求**：避免同时请求多个 agent

### Agent 配置指南

1. **触发词要明确**：避免模糊词汇
2. **指令要重复**：在 prompt 多处强调规则
3. **测试要充分**：覆盖各种边界情况
4. **日志要详细**：便于调试和优化

## 总结

**当前方案 1 的实现：**

- ✅ 所有 agent 都 `react_to_all_messages: true`
- ✅ 通过 LLM 指令过滤决定是否回复
- ✅ daily-assistant 引导用户说关键词
- ✅ 用户说关键词触发专业 agent
- ❌ daily-assistant 不直接 @ 其他 agent

**为什么不让 daily @ 其他 agent：**

1. 容易形成循环对话
2. 用户失去控制权
3. LLM 指令不够可靠
4. 违背设计理念（用户为中心）

**推荐的使用方式：**

- daily-assistant 作为**引导者**，告诉用户如何触发专业 agent
- 用户作为**控制者**，决定何时使用哪个 agent
- 专业 agent 作为**执行者**，响应明确的请求
