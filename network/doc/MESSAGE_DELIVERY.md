# 📨 消息发送机制详解

## 当前实现分析

### Creator Agent 当前的发送方式

**代码位置**: `agents/creator_agent.py` Line 155-158

```python
# 当前实现
message = self._format_action_plan_message(action_plan)

await self.send_direct_message(
    target_agent_id=user_id,  # 例如: "admin"
    text=message
)
```

### 问题分析

❌ **问题**: `send_direct_message(target_agent_id=user_id)`

- `user_id` 是用户 ID（如 "admin"）
- 但 `send_direct_message` 期望的是 agent_id
- 用户不是 agent，所以这个消息可能无法送达

---

## 🎯 正确的发送方式

### 方案 1: 发送到频道 ✅ **推荐**

**优点**:

- 用户在频道中可以看到
- 其他人也能看到（如果需要）
- 符合 OpenAgents 的设计模式

**实现**:

```python
# 获取 messaging adapter
messaging = self.client.mod_adapters.get("openagents.mods.workspace.messaging")

if messaging:
    # 发送到频道
    await messaging.send_channel_message(
        channel="general",  # 或者从上下文获取原始频道
        text=message
    )
```

### 方案 2: 通过 Daily Assistant 转发

**优点**:

- Daily Assistant 可以作为中介
- 保持对话的连贯性
- 用户感觉是在和同一个助手对话

**实现**:

```python
# 发送给 Daily Assistant，让它转发给用户
await messaging.send_direct_message(
    target_agent_id="daily-assistant",
    text=f"FORWARD_TO_USER|{user_id}|{message}"
)
```

### 方案 3: 直接消息（如果用户是 agent）

**适用场景**: 用户通过 agent 身份登录

**实现**:

```python
# 仅当用户有 agent 身份时
await messaging.send_direct_message(
    target_agent_id=user_id,
    text=message
)
```

---

## 🔧 推荐的改进方案

### 改进后的 Creator Agent

```python
async def handle_analysis_completed(self, ctx: EventContext):
    """处理分析完成事件，生成行动计划"""
    event = ctx.incoming_event
    payload = event.payload or {}

    user_id = payload.get("user_id", "unknown")
    framework = payload.get("framework", "general")
    insights = payload.get("insights", [])
    original_content = payload.get("original_content", "")

    # 获取原始频道（如果有）
    original_channel = payload.get("channel", "general")

    print(f"\n📋 收到分析结果")
    print(f"   用户: {user_id}")
    print(f"   框架: {framework}")
    print(f"   洞察数量: {len(insights)}")

    try:
        # 生成行动计划
        action_plan = await self.create_action_plan(
            user_id=user_id,
            framework=framework,
            insights=insights,
            context=original_content
        )

        # 保存行动计划
        storage.save_action_plan(
            user_id=user_id,
            title=action_plan["title"],
            steps=action_plan["steps"],
            overview=action_plan.get("overview", "")
        )

        # 格式化消息
        message = self._format_action_plan_message(action_plan)

        # 🆕 改进：发送到频道
        messaging = self.client.mod_adapters.get("openagents.mods.workspace.messaging")
        if messaging:
            # 方式1: 发送到原始频道
            await messaging.send_channel_message(
                channel=original_channel,
                text=message
            )
            print(f"   ✅ 行动计划已发送到频道: {original_channel}")

            # 方式2 (可选): 同时发送直接消息提醒
            # await messaging.send_direct_message(
            #     target_agent_id="daily-assistant",
            #     text=f"@{user_id} 你的分析报告已准备好！"
            # )
        else:
            print(f"   ⚠️  messaging mod 不可用")

        print(f"   📤 标题: {action_plan['title']}")

    except Exception as e:
        print(f"   ❌ 创建行动计划失败: {e}")
        import traceback
        traceback.print_exc()
```

---

## 📊 消息流向图

### 当前实现（有问题）

```
Creator Agent
     ↓
send_direct_message(target_agent_id="admin")
     ↓
❌ 失败：admin 不是 agent
```

### 改进方案 1: 频道消息 ✅

```
Creator Agent
     ↓
send_channel_message(channel="general")
     ↓
✅ 消息发送到 general 频道
     ↓
用户在 Studio 中看到消息
```

### 改进方案 2: 通过 Daily Assistant

```
Creator Agent
     ↓
send_direct_message(target_agent_id="daily-assistant")
     ↓
Daily Assistant 接收
     ↓
Daily Assistant 转发到频道
     ↓
用户在 Studio 中看到消息
```

---

## 🎨 消息格式示例

### 当前格式（文本）

```
🎯 压力管理与工作效率提升计划

📝 通过时间管理、情绪调节和沟通技巧，系统性地降低工作压力，提升生活质量

📋 行动计划:

1. 实施番茄工作法，每25分钟专注工作后休息5分钟 (本周开始)
   💡 提高工作效率，减少加班时间

2. 每天进行10分钟深呼吸或冥想练习 (每日早晚)
   💡 缓解焦虑，提升情绪稳定性

3. 使用艾森豪威尔矩阵整理任务优先级 (每周一)
   💡 明确重点，避免被琐事淹没

4. 与上级预约一对一会议，讨论工作量 (本周内)
   💡 获得支持，调整工作负荷

5. 设定工作边界，晚上8点后不处理工作邮件 (本月开始)
   💡 改善工作生活平衡，保护个人时间

🌟 开始行动吧！如果需要调整或有任何问题，随时告诉我。
```

### 可选：富文本格式（Markdown）

```markdown
# 🎯 压力管理与工作效率提升计划

> 通过时间管理、情绪调节和沟通技巧，系统性地降低工作压力，提升生活质量

## 📋 行动计划

### 1. 实施番茄工作法

**时间线**: 本周开始  
**预期收益**: 提高工作效率，减少加班时间

### 2. 每日放松练习

**时间线**: 每日早晚  
**预期收益**: 缓解焦虑，提升情绪稳定性

### 3. 任务优先级管理

**时间线**: 每周一  
**预期收益**: 明确重点，避免被琐事淹没

### 4. 与上级沟通

**时间线**: 本周内  
**预期收益**: 获得支持，调整工作负荷

### 5. 设定工作边界

**时间线**: 本月开始  
**预期收益**: 改善工作生活平衡，保护个人时间

---

🌟 **开始行动吧！** 如果需要调整或有任何问题，随时告诉我。
```

---

## 🔍 用户如何接收消息

### 在 OpenAgents Studio 中

1. **打开浏览器**: http://localhost:8700/studio/
2. **登录**: admin / admin
3. **进入频道**: 点击 "general" 频道
4. **查看消息**:
   - 看到 Daily Assistant 的即时回复
   - 几秒后看到 Creator Agent 发送的完整报告

### 消息显示效果

```
┌─────────────────────────────────────────────┐
│ General 频道                                 │
├─────────────────────────────────────────────┤
│                                             │
│ 👤 admin (你)                               │
│ 最近工作压力很大，经常加班到很晚，感觉很焦虑  │
│ 17:30                                       │
│                                             │
│ 🤖 daily-assistant                          │
│ 我理解你的感受。工作压力和焦虑确实很困扰人。  │
│ 让我帮你深入分析一下压力来源和应对方法。      │
│ 17:30                                       │
│                                             │
│ 🎨 creator-agent                            │
│ 🎯 压力管理与工作效率提升计划                │
│                                             │
│ 📝 通过时间管理、情绪调节和沟通技巧，        │
│ 系统性地降低工作压力，提升生活质量            │
│                                             │
│ 📋 行动计划:                                │
│                                             │
│ 1. 实施番茄工作法... (本周开始)             │
│    💡 提高工作效率，减少加班时间             │
│                                             │
│ 2. 每天进行10分钟深呼吸... (每日早晚)       │
│    💡 缓解焦虑，提升情绪稳定性               │
│                                             │
│ ... (更多步骤)                              │
│                                             │
│ 🌟 开始行动吧！                             │
│ 17:30                                       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🎯 推荐的完整流程

### 1. Listener 保存频道信息

```python
# agents/daily_assistant_listener.py

async def react(self, ctx: EventContext):
    event = ctx.incoming_event
    payload = event.payload or {}

    # 提取频道信息
    channel = payload.get("channel", "general")

    # 发送分析请求时包含频道信息
    analysis_msg = f"ANALYSIS_REQUEST|{user_id}|{framework}|{channel}|{content}"
    await messaging.send_direct_message(
        target_agent_id="analyst-agent",
        text=analysis_msg
    )
```

### 2. Analyst 传递频道信息

```python
# agents/analyst_agent.py

async def handle_analysis_request_from_message(self, ctx: EventContext, message: str):
    parts = message.split("|", 4)  # 改为4个部分
    if len(parts) >= 5:
        user_id = parts[1]
        framework = parts[2]
        channel = parts[3]  # 🆕 获取频道
        content = parts[4]

        # 发送给 Creator 时包含频道
        analysis_data = {
            "user_id": user_id,
            "framework": framework,
            "channel": channel,  # 🆕 传递频道
            "insights": insights,
            "confidence": 0.8,
            "original_content": content
        }
```

### 3. Creator 发送到原始频道

```python
# agents/creator_agent.py

async def handle_analysis_completed(self, ctx: EventContext):
    payload = event.payload or {}
    channel = payload.get("channel", "general")  # 🆕 获取频道

    # 发送到原始频道
    messaging = self.client.mod_adapters.get("openagents.mods.workspace.messaging")
    if messaging:
        await messaging.send_channel_message(
            channel=channel,  # 🆕 使用原始频道
            text=message
        )
```

---

## 📝 总结

### 当前问题

❌ 使用 `send_direct_message(target_agent_id=user_id)` 无法送达用户

### 推荐方案

✅ 使用 `send_channel_message(channel="general")` 发送到频道

### 实现步骤

1. Listener 记录原始频道
2. Analyst 传递频道信息
3. Creator 发送到原始频道

### 用户体验

- 用户在频道中发送消息
- 立即看到 Daily Assistant 的回复
- 几秒后在同一频道看到完整的分析报告
- 流畅、自然的对话体验

---

## 🚀 下一步

需要我帮你修改代码，实现正确的消息发送机制吗？
