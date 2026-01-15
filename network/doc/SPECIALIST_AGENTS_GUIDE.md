# Symphony 专业 Agent 使用指南

## 概述

Symphony 系统现在包含三个专业 agent：

- **Daily Assistant**（日常助理）：处理日常对话和基础分析
- **Analyst Agent**（分析师）：提供深度框架分析
- **Creator Agent**（创作者）：生成详细行动计划

## Agent 配置

### 1. Daily Assistant（日常助理）

- **文件**：`agents/daily_assistant_integrated.yaml`
- **功能**：日常对话、基础分析、情感支持
- **触发**：自动响应所有用户消息
- **模型**：qwen-plus
- **特点**：集成了基础分析和计划功能

### 2. Analyst Agent（分析师）

- **文件**：`configs/analyst_agent.yaml`
- **功能**：深度框架分析（MBTI、Big Five、HUMAN 3.0、职业发展等）
- **触发**：需要明确调用
- **模型**：qwen-plus
- **特点**：专业、深度、结构化分析

### 3. Creator Agent（创作者）

- **文件**：`configs/creator_agent.yaml`
- **功能**：详细行动计划、可导出格式
- **触发**：需要明确调用
- **模型**：qwen-plus
- **特点**：具体、可执行、可追踪

## 使用方法

### 日常对话

直接发送消息，Daily Assistant 会自动回复：

```
你好
最近工作压力很大
我想提升自己
```

### 请求深度分析

使用以下方式调用 Analyst Agent：

```
@analyst-agent 帮我分析一下
分析师，用 MBTI 分析我
用 Big Five 框架分析我的性格
分析我的职业发展方向
```

### 请求行动计划

使用以下方式调用 Creator Agent：

```
@creator-agent 帮我制定计划
创作者，给我一个行动方案
我需要详细的执行步骤
帮我规划一下学习计划
```

## 启动 Agent

### 启动所有 Agent

```bash
# 启动日常助理
cd network/agents
openagents agent start daily_assistant_integrated.yaml

# 启动专业 agent
cd network
./restart_specialist_agents.sh
```

### 单独启动

```bash
# 只启动分析师
cd network/configs
openagents agent start analyst_agent.yaml

# 只启动创作者
cd network/configs
openagents agent start creator_agent.yaml
```

## 工作流示例

### 场景 1：职业困惑

```
用户：最近对工作很迷茫，不知道该不该换工作
Daily Assistant：[提供基础支持和初步分析]

用户：分析师，帮我深度分析一下职业发展
Analyst Agent：[使用职业发展框架进行深度分析]

用户：创作者，根据分析结果给我制定计划
Creator Agent：[生成详细的职业发展行动计划]
```

### 场景 2：个人成长

```
用户：我想更了解自己
Daily Assistant：[询问具体方向]

用户：用 MBTI 分析我
Analyst Agent：[进行 MBTI 框架分析]

用户：基于这个分析，帮我做个成长计划
Creator Agent：[生成个性化成长计划]
```

### 场景 3：压力管理

```
用户：最近压力很大，快崩溃了
Daily Assistant：[提供情感支持和基础建议]

用户：分析师，帮我分析压力来源
Analyst Agent：[使用 HUMAN 3.0 框架分析]

用户：创作者，给我一个减压计划
Creator Agent：[生成具体的压力管理行动计划]
```

## 分析框架说明

### MBTI（性格类型分析）

- 适用于：了解性格特点、职业匹配、人际关系
- 维度：E/I、S/N、T/F、J/P
- 输出：性格类型、优势、盲点、发展建议

### Big Five（五大人格特质）

- 适用于：全面性格评估、行为预测
- 维度：开放性、尽责性、外向性、宜人性、神经质
- 输出：各维度评分、特质组合分析、平衡建议

### HUMAN 3.0（全面成长模型）

- 适用于：整体生活评估、平衡发展
- 维度：健康、理解、意义、行动、关系
- 输出：五维度评估、短板识别、提升路径

### 职业发展框架

- 适用于：职业规划、转型决策
- 维度：技能、兴趣、价值观、路径、障碍
- 输出：现状评估、机会识别、具体建议

### 通用深度分析

- 适用于：任何需要深入思考的问题
- 步骤：现状识别、根因分析、影响评估、机会发现、风险评估
- 输出：多角度洞察、系统性建议

## 行动计划特点

### 结构化输出

- 分阶段规划
- 明确时间框架
- 预期效果说明
- 检查点设置

### 可导出格式

每个计划都包含可复制的任务清单：

```
[ ] 步骤1：具体行动 - 截止日期：2026-01-20
[ ] 步骤2：具体行动 - 截止日期：2026-01-25
[ ] 步骤3：具体行动 - 截止日期：2026-02-01
```

可直接复制到：

- Notion
- Todoist
- Microsoft To Do
- Apple Reminders
- 任何支持 Markdown 的工具

## 注意事项

### Agent 互动规则

1. **Daily Assistant**：响应所有用户消息，不响应其他 agent
2. **Analyst Agent**：只响应明确的分析请求
3. **Creator Agent**：只响应明确的计划请求
4. **避免循环**：agent 之间不会相互回复

### 最佳实践

1. **日常对话**：直接和 Daily Assistant 聊
2. **需要深度分析**：明确调用 Analyst Agent
3. **需要详细计划**：明确调用 Creator Agent
4. **循序渐进**：先分析，再计划，再执行

### 故障排查

```bash
# 查看 agent 日志
tail -f network/logs/analyst_agent.log
tail -f network/logs/creator_agent.log

# 查看 agent 状态
ps aux | grep "analyst_agent"
ps aux | grep "creator_agent"

# 重启 agent
cd network
./restart_specialist_agents.sh
```

## API 配置

所有 agent 使用 Qwen API：

- **API Key**：在 `.env` 文件中配置
- **模型**：qwen-plus
- **API Base**：https://dashscope.aliyuncs.com/compatible-mode/v1

## 技术细节

### Agent 类型

- 所有 agent 使用 `CollaboratorAgent`
- 支持 messaging mod
- 通过 gRPC 连接到 network（端口 8700）

### 消息机制

- 使用 `send_channel_message` 工具回复
- 自动识别消息来源
- 避免 agent 间循环对话

### 配置参数

- `react_to_all_messages: true`：响应所有消息
- `temperature: 0.7-0.8`：平衡创造性和准确性
- `max_tokens: 1000-1500`：足够详细的输出

## 未来扩展

### 计划中的功能

1. **自动导出**：直接导出到外部工具（Notion、Todoist）
2. **进度追踪**：自动记录和提醒
3. **数据分析**：基于历史对话的趋势分析
4. **多模态支持**：图表、思维导图生成

### 可添加的框架

- 九型人格（Enneagram）
- 优势识别器（StrengthsFinder）
- 价值观评估
- 生活轮盘（Life Wheel）
- OKR 目标管理

## 支持

如有问题，请查看：

- `doc/TROUBLESHOOTING.md`
- `doc/ARCHITECTURE.md`
- Agent 日志文件
