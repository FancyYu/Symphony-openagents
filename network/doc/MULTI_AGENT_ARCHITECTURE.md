# Symphony MVP - 多 Agent 协作架构

## 🎯 架构概述

使用 **Python CollaboratorAgent** 实现真正的多 Agent 协作系统。

## 📊 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         用户                                 │
└────────────────────┬────────────────────────────────────────┘
                     │ 频道消息
                     ↓
┌─────────────────────────────────────────────────────────────┐
│          Coordinator Agent (Python CollaboratorAgent)        │
│  - 接收用户消息                                              │
│  - 判断是否需要分析                                          │
│  - 协调分析流程                                              │
└──────────┬──────────────────────┬───────────────────────────┘
           │                      │
           │ workspace().agent()  │ workspace().agent()
           │ .send()              │ .send()
           ↓                      ↓
    ┌─────────────┐        ┌─────────────┐
    │  Analyst    │        │  Creator    │
    │  Agent      │        │  Agent      │
    │             │        │             │
    │ - 分析内容   │        │ - 生成计划   │
    │ - 返回洞察   │───────→│ - 返回步骤   │
    └─────────────┘        └─────────────┘
           │                      │
           │ workspace().agent()  │
           │ .send()              │
           ↓                      ↓
    ┌─────────────────────────────────┐
    │     Coordinator Agent            │
    │  - 整合结果                      │
    │  - 发送给用户                    │
    └─────────────────────────────────┘
```

## 🔧 Agent 实现

### 1. Coordinator Agent (协调者)

**文件**: `agents/coordinator_collaborator.py`

**职责**:

- 监听频道消息
- 判断是否需要深度分析
- 发送请求给 Analyst
- 接收 Analyst 响应，转发给 Creator
- 接收 Creator 响应，整合后发送给用户

**关键代码**:

```python
class CoordinatorCollaborator(CollaboratorAgent):
    async def on_channel_post(self, msg):
        # 接收用户消息
        if self._needs_analysis(msg.text):
            # 发送给分析师
            ws = self.workspace()
            await ws.agent("analyst-agent").send(request)

    async def on_direct(self, msg):
        # 接收来自其他 Agent 的响应
        if msg.sender_id == "analyst-agent":
            # 转发给创作者
            await ws.agent("creator-agent").send(data)
        elif msg.sender_id == "creator-agent":
            # 发送给用户
            await ws.channel(channel).post(response)
```

### 2. Analyst Agent (分析师)

**文件**: `agents/analyst_collaborator.py`

**职责**:

- 接收分析请求（通过直接消息）
- 使用框架库进行分析
- 生成洞察
- 返回结果给 Coordinator

**关键代码**:

```python
class AnalystCollaborator(CollaboratorAgent):
    async def on_direct(self, msg):
        # 接收分析请求
        request = json.loads(msg.text)

        # 执行分析
        insights = await self.perform_analysis(...)

        # 返回结果
        ws = self.workspace()
        await ws.agent(msg.sender_id).send(result)
```

### 3. Creator Agent (创作者)

**文件**: `agents/creator_collaborator.py`

**职责**:

- 接收分析结果（通过直接消息）
- 生成行动计划
- 返回结果给 Coordinator

**关键代码**:

```python
class CreatorCollaborator(CollaboratorAgent):
    async def on_direct(self, msg):
        # 接收分析结果
        analysis = json.loads(msg.text)

        # 生成行动计划
        plan = await self.create_action_plan(...)

        # 返回结果
        ws = self.workspace()
        await ws.agent(msg.sender_id).send(result)
```

## 📡 通信机制

### 使用 workspace() 接口

```python
# 获取 workspace
ws = self.workspace()

# 发送消息给其他 Agent
await ws.agent("target-agent-id").send(message)

# 发送消息到频道
await ws.channel("general").post(message)

# 发送消息给用户
await ws.agent(user_id).send(message)
```

### 消息格式

所有 Agent 间通信使用 JSON 格式：

```python
# 分析请求
{
    "user_id": "admin",
    "content": "最近工作压力很大",
    "framework": "general",
    "channel": "general"
}

# 分析响应
{
    "user_id": "admin",
    "framework": "general",
    "channel": "general",
    "insights": ["洞察1", "洞察2", "洞察3"],
    "confidence": 0.8,
    "original_content": "..."
}

# 行动计划响应
{
    "user_id": "admin",
    "channel": "general",
    "action_plan": {
        "title": "...",
        "overview": "...",
        "steps": [...]
    },
    "insights": [...]
}
```

## 🔄 完整流程

### 1. 用户发送消息

```
用户在频道发送: "最近工作压力很大"
```

### 2. Coordinator 接收并判断

```python
# coordinator_collaborator.py
async def on_channel_post(self, msg):
    if self._needs_analysis(msg.text):
        # 需要分析
        await self.handle_analysis_request(...)
```

### 3. Coordinator → Analyst

```python
request = {
    "user_id": "admin",
    "content": "最近工作压力很大",
    "framework": "general",
    "channel": "general"
}
await ws.agent("analyst-agent").send(json.dumps(request))
```

### 4. Analyst 分析并返回

```python
# analyst_collaborator.py
async def on_direct(self, msg):
    insights = await self.perform_analysis(...)
    result = {"insights": insights, ...}
    await ws.agent(msg.sender_id).send(json.dumps(result))
```

### 5. Coordinator → Creator

```python
# coordinator_collaborator.py
async def handle_analysis_response(self, data):
    await ws.agent("creator-agent").send(json.dumps(data))
```

### 6. Creator 生成计划并返回

```python
# creator_collaborator.py
async def on_direct(self, msg):
    plan = await self.create_action_plan(...)
    result = {"action_plan": plan, ...}
    await ws.agent(msg.sender_id).send(json.dumps(result))
```

### 7. Coordinator → 用户

```python
# coordinator_collaborator.py
async def handle_plan_response(self, data):
    response = self._format_complete_response(...)
    await ws.channel(channel).post(response)
```

## 🚀 启动方式

```bash
cd network
chmod +x restart_multi_agent.sh
./restart_multi_agent.sh
```

或手动启动：

```bash
# 终端 1: 网络
openagents network start .

# 终端 2: 协调者
python3 agents/coordinator_collaborator.py

# 终端 3: 分析师
python3 agents/analyst_collaborator.py

# 终端 4: 创作者
python3 agents/creator_collaborator.py
```

## ✅ 优势

### 相比集成模式

1. **真正的多 Agent 协作** - 每个 Agent 独立运行
2. **职责分离** - 每个 Agent 专注自己的任务
3. **可扩展性** - 易于添加新的 Agent
4. **并发处理** - 多个请求可以并行处理
5. **独立升级** - 可以单独更新某个 Agent

### 相比 WorkerAgent 方案

1. **可以使用 messaging mod** - 正常通信
2. **简单的 API** - workspace() 接口直观
3. **可靠的消息传递** - 不依赖自定义事件
4. **更好的调试** - 清晰的消息流

## 📊 性能考虑

### 延迟

- 单 Agent (集成模式): ~2-3 秒
- 多 Agent (协作模式): ~4-6 秒
  - Coordinator → Analyst: ~1 秒
  - Analyst 分析: ~2 秒
  - Analyst → Creator: ~1 秒
  - Creator 生成: ~1 秒
  - Creator → Coordinator → 用户: ~1 秒

### 并发

- 集成模式: 一次处理一个请求
- 协作模式: 可以并行处理多个请求

## 🔧 配置

### Agent ID

- `coordinator-agent` - 协调者
- `analyst-agent` - 分析师
- `creator-agent` - 创作者

### 端口

- 网络: 8700 (HTTP), 8600 (gRPC)
- 所有 Agents 连接到: localhost:8700

### 日志

- `logs/coordinator.log` - 协调者日志
- `logs/analyst.log` - 分析师日志
- `logs/creator.log` - 创作者日志

## 🎯 最佳实践

1. **错误处理**: 每个 Agent 都应该有完善的错误处理
2. **超时机制**: 设置合理的超时时间
3. **消息验证**: 验证接收到的消息格式
4. **日志记录**: 详细记录每个步骤
5. **状态管理**: 使用字典跟踪等待的响应

## 🔮 未来扩展

### 可以添加的 Agents

1. **Memory Agent** - 专门管理记忆和上下文
2. **Emotion Agent** - 情绪分析和支持
3. **Goal Agent** - 目标跟踪和提醒
4. **Report Agent** - 生成周报、月报

### 可以实现的功能

1. **多用户并发** - 同时处理多个用户
2. **优先级队列** - 紧急请求优先处理
3. **缓存机制** - 缓存常见分析结果
4. **A/B 测试** - 测试不同的分析策略

这就是完整的多 Agent 协作架构！
