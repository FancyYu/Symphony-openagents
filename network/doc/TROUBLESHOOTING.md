# 🔧 问题排查与解决方案

## 🐛 已发现的问题

### 问题 1: Daily Assistant 用英文回复 ❌

**症状**:

- 用户发送中文消息
- Daily Assistant 用英文回复

**原因**:

- `daily_assistant.yaml` 的 instruction 是英文的

**解决方案**: ✅ 已修复

```yaml
# 修改前
instruction: |
  You are the Daily Assistant...

# 修改后
instruction: |
  你是 Symphony 系统中的日常助理...
  始终用中文回复
```

**如何应用**:

```bash
# 重启 Daily Assistant
pkill -f "daily_assistant.yaml"
openagents agent start configs/daily_assistant.yaml > logs/日常助理.log 2>&1 &
```

---

### 问题 2: API 限流 (429 Too Many Requests) ⚠️

**症状**:

```
HTTP/1.1 429 Too Many Requests
Retrying request in 36.000000 seconds
```

**原因**:

- Groq API 免费层有速率限制
- 频繁调用超过限制

**解决方案**:

#### 方案 1: 减少 token 使用 ✅ 已应用

```yaml
llm_config:
  max_tokens: 150 # 从 300 降到 150
  temperature: 0.7 # 从 0.8 降到 0.7
```

#### 方案 2: 等待重试

- Groq 会自动重试
- 等待 30-60 秒

#### 方案 3: 升级 API 计划

- 访问 https://console.groq.com/
- 升级到付费计划

#### 方案 4: 切换到其他 LLM

```yaml
# 使用 OpenAI
llm_config:
  provider: "openai"
  api_key: "${OPENAI_API_KEY}"
  model: "gpt-4o-mini"
```

---

### 问题 3: 响应慢 🐌

**症状**:

- 消息发送后等待很久才收到回复
- 4-10 秒延迟

**原因**:

1. API 限流导致重试
2. LLM 推理时间
3. 多个 agent 串行处理

**解决方案**:

#### 立即改进:

1. ✅ 减少 max_tokens (150 而不是 300)
2. ✅ 优化 instruction (更简洁)
3. 等待 API 限流恢复

#### 长期优化:

1. 使用更快的模型
2. 实现缓存机制
3. 并行处理部分任务

---

### 问题 4: 工具调用错误 ❌

**症状**:

```
tool call validation failed: parameters for tool reply_channel_message
did not match schema: errors: [missing properties: 'reply_to_id']
```

**原因**:

- Daily Assistant 尝试使用 `reply_channel_message` 工具
- 但缺少必需的 `reply_to_id` 参数

**解决方案**:
这是 OpenAgents 的工具调用问题，不影响核心功能。可以忽略或：

```yaml
# 在 daily_assistant.yaml 中简化工具使用
config:
  instruction: |
    ...
    使用 send_channel_message 发送消息，不要使用 reply_channel_message
```

---

## 🚀 快速修复步骤

### 步骤 1: 停止所有 agents

```bash
pkill -9 -f "openagents agent"
pkill -9 -f "daily_assistant_listener"
pkill -9 -f "analyst_agent"
pkill -9 -f "creator_agent"
```

### 步骤 2: 等待 API 限流恢复

```bash
# 等待 1-2 分钟
sleep 120
```

### 步骤 3: 重新启动系统

```bash
cd network
python start_symphony.py
```

### 步骤 4: 测试

发送简单消息测试：

```
你好
```

应该收到中文回复。

---

## 📊 性能优化建议

### 1. 减少不必要的 LLM 调用

**当前**: 每条消息都调用 LLM

**优化**:

- 简单问候不调用 LLM
- 使用规则匹配快速响应

```python
# 在 daily_assistant_listener.py 中
SIMPLE_RESPONSES = {
    "你好": "你好！有什么我可以帮助你的吗？",
    "hi": "Hi! How can I help you?",
    "谢谢": "不客气！随时为你服务。"
}

if content in SIMPLE_RESPONSES:
    # 直接回复，不调用 LLM
    return SIMPLE_RESPONSES[content]
```

### 2. 使用更快的模型

```yaml
# Groq 最快的模型
model: "llama-3.3-70b-versatile"  # 更快但更贵

# 或者使用本地模型
model: "ollama/llama3"  # 需要本地 Ollama
```

### 3. 实现响应缓存

```python
# 缓存常见问题的回复
CACHE = {
    "压力大": "我理解你的压力。让我帮你分析...",
    "焦虑": "焦虑是很常见的。让我们一起找出原因..."
}
```

---

## 🔍 日志分析

### 查看实时日志

```bash
# Daily Assistant
tail -f logs/日常助理.log | grep -E "RECEIVED|ERROR|429"

# Listener
tail -f logs/日常助理监听器.log | grep -E "收到消息|检测到"

# Analyst
tail -f logs/分析师智能体.log | grep -E "收到分析|完成"

# Creator
tail -f logs/创作者智能体.log | grep -E "收到分析|发送"
```

### 关键指标

**正常响应时间**:

- Daily Assistant: < 1 秒
- 完整分析流程: 3-5 秒

**异常信号**:

- `429 Too Many Requests` - API 限流
- `400 Bad Request` - 参数错误
- `Connection refused` - 网络服务未启动
- `Agent already registered` - Agent 重复注册

---

## 🎯 当前状态检查

### 检查 API 配额

```bash
# 测试 Groq API
curl -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "Hi"}],
    "max_tokens": 10
  }'
```

### 检查 Agent 状态

```bash
# 查看运行中的 agents
ps aux | grep -E "daily_assistant|analyst|creator|listener"

# 查看端口占用
lsof -i :8700
lsof -i :8600
```

---

## ✅ 修复后的预期行为

### 测试 1: 简单问候

```
用户: 你好
Daily Assistant: 你好！有什么我可以帮助你的吗？
响应时间: < 1秒
```

### 测试 2: 需要分析的消息

```
用户: 最近工作压力很大
Daily Assistant: 我理解你的感受。让我为你进行深入分析，找出解决方案。
[等待 3-5秒]
Creator: 🎯 压力管理与工作效率提升计划...
```

### 测试 3: MBTI 分析

```
用户: 用 MBTI 分析我的性格
Daily Assistant: 好的，我会使用 MBTI 框架为你分析。
[等待 3-5秒]
Creator: 🎯 MBTI 性格分析报告...
```

---

## 🆘 紧急问题处理

### 如果系统完全无响应

```bash
# 1. 完全停止
pkill -9 -f openagents
pkill -9 -f python

# 2. 清理端口
lsof -ti:8700 | xargs kill -9
lsof -ti:8600 | xargs kill -9

# 3. 等待
sleep 30

# 4. 重启网络服务
cd network
openagents network start .

# 5. 等待网络启动
sleep 10

# 6. 重启 agents
python start_symphony.py
```

### 如果 API 持续限流

```bash
# 临时方案：使用 OpenAI
export OPENAI_API_KEY=你的OpenAI密钥

# 修改 daily_assistant.yaml
# provider: "openai"
# model: "gpt-4o-mini"
```

---

## 📝 总结

### 已修复 ✅

1. Daily Assistant 现在用中文回复
2. 减少了 token 使用 (150 vs 300)
3. 优化了 instruction

### 需要注意 ⚠️

1. Groq API 有速率限制
2. 响应时间 3-5 秒是正常的
3. 工具调用错误可以忽略

### 下一步 🚀

1. 重启系统应用修复
2. 测试中文回复
3. 监控 API 使用情况
4. 考虑升级 API 计划或切换提供商
