# 🔍 API 使用分析报告

## 问题：API 消耗过快

### 当前情况

**一条用户消息触发的 API 调用**：

1. **Daily Assistant (YAML)** - 1 次 LLM 调用

   - 用户发送消息 → Daily Assistant 回复

2. **Analyst Agent (Python)** - 1 次 LLM 调用（如果触发分析）

   - 执行深度分析 → 生成洞察

3. **Creator Agent (Python)** - 1 次 LLM 调用（如果触发分析）
   - 生成行动计划 → 格式化输出

**总计：每条需要分析的消息 = 3 次 API 调用**

---

## 🚨 发现的问题

### 问题 1: Daily Assistant 响应所有消息

```yaml
config:
  react_to_all_messages: true # ← 这会让它响应所有消息！
```

**影响**：

- ❌ Daily Assistant 会响应**自己的消息**
- ❌ Daily Assistant 会响应**其他 agent 的消息**
- ❌ 造成消息循环和不必要的 API 调用

**证据**：

```
📨 收到消息 from daily-assistant
   用户: daily-assistant
   内容: nice to meet you too!...
```

Listener 在监听 Daily Assistant 自己的消息！

### 问题 2: Listener 也在监听所有消息

```python
async def react(self, ctx: EventContext):
    """监听所有消息"""
    event = ctx.incoming_event
    source_id = event.source_id

    # 跳过自己的消息和其他 agent 的消息
    if source_id == self.agent_id or source_id.endswith("-agent") or source_id.endswith("-listener"):
        return
```

虽然有过滤，但还是会处理每条消息。

### 问题 3: 分析流程每次都调用 LLM

即使是简单的消息，如果触发了分析关键词，也会：

1. Analyst 调用 LLM 生成分析
2. Creator 调用 LLM 生成行动计划

---

## 💡 优化方案

### 优化 1: 限制 Daily Assistant 响应范围 ⭐⭐⭐

**修改 `configs/daily_assistant.yaml`**:

```yaml
config:
  react_to_all_messages: false # 改为 false

  # 只响应直接消息和提及
  react_to_direct_messages: true
  react_to_mentions: true
```

**效果**：

- ✅ 只响应用户的直接消息
- ✅ 只响应被 @ 提及时
- ✅ 不响应其他 agent 的消息
- ✅ 减少 50% 的 API 调用

### 优化 2: 添加消息去重 ⭐⭐

**在 Listener 中添加消息缓存**:

```python
class DailyAssistantListener(WorkerAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.processed_messages = set()  # 缓存已处理的消息
        self.cache_size = 100

    async def react(self, ctx: EventContext):
        event = ctx.incoming_event

        # 生成消息唯一标识
        msg_id = event.payload.get("original_event_id")
        if msg_id in self.processed_messages:
            return  # 跳过已处理的消息

        # 处理消息...

        # 添加到缓存
        self.processed_messages.add(msg_id)
        if len(self.processed_messages) > self.cache_size:
            # 清理旧缓存
            self.processed_messages = set(list(self.processed_messages)[-self.cache_size:])
```

**效果**：

- ✅ 避免重复处理同一条消息
- ✅ 减少不必要的 API 调用

### 优化 3: 使用更便宜的模型 ⭐⭐⭐

**当前配置**：

```yaml
model: "llama-3.1-8b-instant" # 每次调用消耗配额
```

**优化选项**：

1. **Daily Assistant 使用更小的模型**（简单对话）:

   ```yaml
   model: "llama-3.1-8b-instant" # 保持不变，已经是最小的
   ```

2. **减少 max_tokens**（减少消耗）:

   ```yaml
   max_tokens: 100 # 从 150 减少到 100
   ```

3. **考虑使用本地模型**（如果可能）:
   - Ollama
   - LM Studio
   - 完全免费，无限制

### 优化 4: 添加分析频率限制 ⭐⭐

**限制每个用户的分析频率**:

```python
from datetime import datetime, timedelta

class DailyAssistantListener(WorkerAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_analysis = {}  # user_id -> timestamp
        self.analysis_cooldown = 300  # 5分钟冷却

    async def react(self, ctx: EventContext):
        # ... 提取 user_id ...

        # 检查冷却时间
        if user_id in self.last_analysis:
            last_time = self.last_analysis[user_id]
            if (datetime.now() - last_time).seconds < self.analysis_cooldown:
                print(f"   ⏰ 分析冷却中，跳过 (剩余 {self.analysis_cooldown - (datetime.now() - last_time).seconds}秒)")
                return

        # 检查是否需要分析
        if self._needs_analysis(content):
            self.last_analysis[user_id] = datetime.now()
            # 发送分析请求...
```

**效果**：

- ✅ 避免短时间内重复分析
- ✅ 减少 API 消耗
- ✅ 提升用户体验（不会被分析轰炸）

### 优化 5: 缓存分析结果 ⭐

**对相似问题使用缓存**:

```python
import hashlib

class AnalystAgent(WorkerAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analysis_cache = {}  # content_hash -> insights
        self.cache_ttl = 3600  # 1小时

    async def perform_analysis(self, content: str, framework: str, user_id: str):
        # 生成内容哈希
        content_hash = hashlib.md5(f"{content[:100]}_{framework}".encode()).hexdigest()

        # 检查缓存
        if content_hash in self.analysis_cache:
            cached = self.analysis_cache[content_hash]
            if (datetime.now() - cached['timestamp']).seconds < self.cache_ttl:
                print(f"   💾 使用缓存的分析结果")
                return cached['insights']

        # 执行新分析
        insights = await self._do_analysis(content, framework, user_id)

        # 保存到缓存
        self.analysis_cache[content_hash] = {
            'insights': insights,
            'timestamp': datetime.now()
        }

        return insights
```

---

## 📊 优化效果预估

### 当前消耗（每条需要分析的消息）

| Agent           | API 调用 | Tokens (估算)    |
| --------------- | -------- | ---------------- |
| Daily Assistant | 1 次     | ~150 tokens      |
| Analyst         | 1 次     | ~800 tokens      |
| Creator         | 1 次     | ~600 tokens      |
| **总计**        | **3 次** | **~1550 tokens** |

### 优化后消耗

| 优化            | 减少比例 | 说明                  |
| --------------- | -------- | --------------------- |
| 限制响应范围    | -50%     | 不响应其他 agent 消息 |
| 消息去重        | -20%     | 避免重复处理          |
| 分析频率限制    | -30%     | 5 分钟冷却            |
| 减少 max_tokens | -10%     | 150 → 100             |
| 缓存分析结果    | -40%     | 相似问题复用          |

**综合效果：减少 60-70% 的 API 调用**

---

## 🚀 立即应用的优化

### 快速优化（5 分钟）

1. **修改 Daily Assistant 配置**:

   ```yaml
   config:
     react_to_all_messages: false
     react_to_direct_messages: true
     react_to_mentions: true
   ```

2. **减少 max_tokens**:
   ```yaml
   llm_config:
     max_tokens: 100 # 从 150 减少
   ```

### 中期优化（30 分钟）

3. **添加消息去重**（Listener）
4. **添加分析频率限制**（Listener）

### 长期优化（1-2 小时）

5. **实现分析结果缓存**（Analyst）
6. **考虑使用本地模型**（完全免费）

---

## 💰 成本对比

### Groq API 限制（免费层）

- **每分钟请求数**: 30 requests/min
- **每天请求数**: 14,400 requests/day
- **Tokens**: 根据模型不同

### 当前使用情况

假设每天 100 条需要分析的消息：

- API 调用: 100 × 3 = **300 次/天**
- Tokens: 100 × 1550 = **155,000 tokens/天**

### 优化后

假设减少 60%：

- API 调用: 100 × 3 × 0.4 = **120 次/天**
- Tokens: 100 × 1550 × 0.4 = **62,000 tokens/天**

**节省：180 次 API 调用，93,000 tokens**

---

## 🎯 推荐方案

### 立即执行（最高优先级）

1. ✅ 修改 `react_to_all_messages: false`
2. ✅ 减少 `max_tokens: 100`
3. ✅ 添加消息去重

### 本周执行

4. ✅ 添加分析频率限制（5 分钟冷却）
5. ✅ 优化关键词检测（更精确）

### 考虑长期

6. 🤔 实现分析结果缓存
7. 🤔 使用本地模型（Ollama）
8. 🤔 实现更智能的分析触发逻辑

---

## 📝 监控建议

创建 API 使用监控脚本：

```python
# monitor_api_usage.py
import sqlite3
from datetime import datetime, timedelta

def get_api_usage_stats():
    conn = sqlite3.connect('data/symphony_mvp.db')
    cursor = conn.cursor()

    # 统计今天的消息数
    today = datetime.now().date()
    cursor.execute("""
        SELECT COUNT(*) FROM user_messages
        WHERE date(timestamp) = ?
    """, (today,))

    messages_today = cursor.fetchone()[0]

    # 统计分析次数
    cursor.execute("""
        SELECT COUNT(*) FROM analysis_results
        WHERE date(timestamp) = ?
    """, (today,))

    analyses_today = cursor.fetchone()[0]

    # 估算 API 调用
    api_calls = messages_today + (analyses_today * 2)

    print(f"📊 今日 API 使用统计")
    print(f"   消息数: {messages_today}")
    print(f"   分析数: {analyses_today}")
    print(f"   估算 API 调用: {api_calls}")
    print(f"   估算 Tokens: {api_calls * 500}")

    conn.close()

if __name__ == "__main__":
    get_api_usage_stats()
```

---

## 🚀 立即行动

```bash
cd network

# 1. 备份当前配置
cp configs/daily_assistant.yaml configs/daily_assistant.yaml.backup

# 2. 应用优化（我会帮你修改）

# 3. 重启 agents
pkill -9 -f "openagents agent"
pkill -9 -f "python.*agent"
sleep 5
./fix_all_issues.sh
```

让我知道是否要我立即应用这些优化！
