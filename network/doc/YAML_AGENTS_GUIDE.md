# Symphony MVP - YAML 多 Agent 模式指南

## 🎯 架构概述

三个独立的 YAML Agent，使用不同的 AI 模型，自动 fallback 机制：

```
┌─────────────────────────────────────────────────────────┐
│                    用户 (频道消息)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│  协调者 Agent (coordinator-agent)                        │
│  - 模型: Qwen → Groq (fallback)                         │
│  - 职责: 接收消息，判断类型，简单对话直接回复            │
└─────────────────────────────────────────────────────────┘
                     │
                     ↓ (需要深度分析时)
┌─────────────────────────────────────────────────────────┐
│  分析师 Agent (analyst-agent)                            │
│  - 模型: DeepSeek → Qwen → Groq (fallback)              │
│  - 职责: 使用专业框架进行深度分析，生成洞察              │
└─────────────────────────────────────────────────────────┘
                     │
                     ↓ (分析完成后)
┌─────────────────────────────────────────────────────────┐
│  创作者 Agent (creator-agent)                            │
│  - 模型: Gemini → Qwen → Groq (fallback)                │
│  - 职责: 基于洞察生成可执行的行动计划                    │
└─────────────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│              返回结果给用户                              │
└─────────────────────────────────────────────────────────┘
```

## 📦 Agent 配置

### 1. 协调者 Agent (`coordinator_agent.yaml`)

**职责**：

- 接收用户消息
- 判断是简单对话还是需要深度分析
- 简单对话直接回复
- 复杂问题告知"正在分析..."

**模型配置**：

```yaml
主模型: Qwen (qwen-plus)
备用: Groq (llama-3.3-70b-versatile)
```

**触发器**：

- 监听 `general` 频道的消息

### 2. 分析师 Agent (`analyst_agent.yaml`)

**职责**：

- 接收深度分析请求
- 使用专业框架（MBTI、Big Five、HUMAN 3.0 等）
- 生成 3-5 个关键洞察

**模型配置**：

```yaml
主模型: DeepSeek (deepseek-chat)
备用1: Qwen (qwen-plus)
备用2: Groq (llama-3.3-70b-versatile)
```

**分析框架**：

- MBTI（性格分析）
- Big Five（五大人格）
- HUMAN 3.0（全面成长）
- 职业发展框架
- 通用分析框架

### 3. 创作者 Agent (`creator_agent.yaml`)

**职责**：

- 接收分析洞察
- 生成具体、可操作的行动计划
- 每个步骤包含行动、时间、效果

**模型配置**：

```yaml
主模型: Gemini (gemini-2.0-flash-exp)
备用1: Qwen (qwen-plus)
备用2: Groq (llama-3.3-70b-versatile)
```

**输出格式**：

- 计划标题和概述
- 5-7 个具体步骤
- 每步包含时间框架和预期效果
- 鼓励性结语

## 🔧 配置 API Keys

### 1. 编辑 `.env` 文件

```bash
cd network
nano .env  # 或使用其他编辑器
```

### 2. 添加 API Keys

```bash
# Groq API (必需，作为所有 Agent 的 fallback)
GROQ_API_KEY=gsk_your_groq_api_key

# Qwen API (可选，阿里云通义千问)
QWEN_API_KEY=sk-your_qwen_api_key

# DeepSeek API (可选，分析师主模型)
DEEPSEEK_API_KEY=sk-your_deepseek_api_key

# Gemini API (可选，创作者主模型)
GEMINI_API_KEY=your_gemini_api_key
```

### 3. 获取 API Keys

#### Groq (必需)

- 网址: https://console.groq.com/
- 免费额度: 每天 14,400 请求
- 模型: llama-3.3-70b-versatile

#### Qwen / 通义千问 (可选)

- 网址: https://dashscope.console.aliyun.com/apiKey
- 需要阿里云账号
- 模型: qwen-plus, qwen-turbo

#### DeepSeek (可选)

- 网址: https://platform.deepseek.com/api_keys
- 性价比高，适合深度分析
- 模型: deepseek-chat

#### Gemini (可选)

- 网址: https://aistudio.google.com/app/apikey
- Google AI Studio
- 模型: gemini-2.0-flash-exp

## 🚀 启动系统

### 方法 1: 使用启动脚本（推荐）

```bash
cd network
./restart_yaml_agents.sh
```

### 方法 2: 手动启动

```bash
# 1. 启动网络
openagents network start .

# 2. 启动协调者
openagents agent start configs/coordinator_agent.yaml

# 3. 启动分析师
openagents agent start configs/analyst_agent.yaml

# 4. 启动创作者
openagents agent start configs/creator_agent.yaml
```

## ✅ 验证运行

### 1. 检查进程

```bash
ps aux | grep openagents | grep -v grep
```

应该看到 4 个进程：

- 1 个网络进程
- 3 个 agent 进程

### 2. 查看日志

```bash
# 协调者日志
tail -f logs/coordinator.log

# 分析师日志
tail -f logs/analyst.log

# 创作者日志
tail -f logs/creator.log
```

### 3. 访问 Web UI

```bash
open http://localhost:8700
```

### 4. 测试消息

在 `general` 频道发送：

**简单对话测试**：

```
你好
```

预期：协调者直接回复

**深度分析测试**：

```
最近工作压力很大，感觉很焦虑，不知道该怎么办
```

预期：

1. 协调者告知"正在分析..."
2. 分析师生成洞察
3. 创作者生成行动计划
4. 返回完整结果

## 🔄 Fallback 机制

### 工作原理

每个 Agent 的 YAML 配置中，`llm` 字段是一个数组，OpenAgents 会按顺序尝试：

```yaml
llm:
  - provider: openai
    model_name: deepseek-chat
    api_key: ${DEEPSEEK_API_KEY}
    # 如果失败，尝试下一个

  - provider: openai
    model_name: qwen-plus
    api_key: ${QWEN_API_KEY}
    # 如果失败，尝试下一个

  - provider: groq
    model_name: llama-3.3-70b-versatile
    api_key: ${GROQ_API_KEY}
    # 最后的 fallback
```

### 失败场景

1. **API Key 未配置**：跳到下一个模型
2. **API Key 无效**：跳到下一个模型
3. **速率限制**：跳到下一个模型
4. **网络错误**：跳到下一个模型

### 最小配置

只需要 Groq API Key，所有 Agent 都会使用 Groq：

```bash
# .env 文件
GROQ_API_KEY=gsk_your_groq_api_key

# 其他 API keys 留空或使用占位符
QWEN_API_KEY=your_qwen_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## 📊 模型对比

| Agent  | 主模型   | 优势                 | Fallback    |
| ------ | -------- | -------------------- | ----------- |
| 协调者 | Qwen     | 中文理解好，响应快   | Groq        |
| 分析师 | DeepSeek | 深度推理强，性价比高 | Qwen → Groq |
| 创作者 | Gemini   | 创意强，格式化好     | Qwen → Groq |

## 🎯 使用场景

### 场景 1: 简单问候

```
用户: 你好
协调者: 你好！我是你的日常助理，有什么可以帮助你的吗？
```

### 场景 2: 深度分析

```
用户: 最近工作压力很大，经常加班，感觉快撑不住了

协调者: 正在为你进行深度分析... 🔍

[分析师使用 DeepSeek 分析]
📊 **分析洞察**
1. 工作负荷超出承受能力，需要重新评估任务优先级
2. 缺乏有效的时间管理和边界设置
3. 长期压力可能导致倦怠，需要及时调整
4. 可能存在完美主义倾向，增加了心理负担
5. 需要建立更好的工作生活平衡机制

[创作者使用 Gemini 生成计划]
🎯 **工作压力管理行动计划**

📝 通过改善时间管理和建立健康边界，逐步减轻工作压力

📋 **行动步骤：**

1. 每天早晨列出3个最重要任务 (本周开始)
   💡 预期效果：聚焦重点，避免被琐事淹没

2. 设置工作时间边界，晚上8点后不查看工作邮件 (立即执行)
   💡 预期效果：保护个人时间，改善工作生活平衡

3. 每天安排15分钟冥想或散步 (每日)
   💡 预期效果：有效释放压力，提升专注力

4. 与上级沟通工作量，寻求支持或调整 (本周内)
   💡 预期效果：获得理解和资源支持

5. 每周安排一次完全放松的活动 (每周)
   💡 预期效果：定期充电，保持长期动力

🌟 开始行动吧！记住，照顾好自己才能更好地工作。
```

## 🔧 故障排查

### 问题 1: Agent 无法启动

**检查**：

```bash
# 查看日志
tail -50 logs/coordinator.log
tail -50 logs/analyst.log
tail -50 logs/creator.log
```

**常见原因**：

- GROQ_API_KEY 未设置
- 网络服务未启动
- 端口被占用

### 问题 2: 所有请求都使用 Groq

**原因**：其他 API keys 未配置或无效

**解决**：

1. 检查 `.env` 文件中的 API keys
2. 确保 API keys 有效且有额度
3. 查看日志确认是否有错误信息

### 问题 3: 响应很慢

**可能原因**：

- 主模型 API 响应慢
- 正在尝试多个 fallback

**优化**：

- 使用响应更快的模型
- 减少 fallback 层级
- 检查网络连接

## 📈 性能优化

### 1. 模型选择

- **快速响应**：使用 Groq（最快）
- **深度分析**：使用 DeepSeek（推理强）
- **创意输出**：使用 Gemini（格式好）
- **中文优化**：使用 Qwen（中文理解好）

### 2. Token 优化

当前配置：

- 协调者: 200 tokens（简短回复）
- 分析师: 800 tokens（详细分析）
- 创作者: 600 tokens（结构化计划）

### 3. 温度设置

- 协调者: 0.7（平衡）
- 分析师: 0.8（更有创造性）
- 创作者: 0.7（结构化）

## 🔮 未来扩展

### 可以添加的功能

1. **记忆系统**：集成 Memory Palace
2. **用户画像**：持续学习用户特征
3. **主动提醒**：定期检查和跟进
4. **多模态**：支持语音、图片输入
5. **协作学习**：Agent 间共享知识

### 可以添加的 Agent

1. **情绪支持 Agent**：专注情绪疏导
2. **目标跟踪 Agent**：跟踪行动计划执行
3. **报告生成 Agent**：生成周报、月报
4. **知识管理 Agent**：整理和检索知识

## 💡 最佳实践

1. **API Key 管理**：

   - 定期轮换
   - 监控使用量
   - 设置预算提醒

2. **日志管理**：

   - 定期清理旧日志
   - 监控错误信息
   - 分析使用模式

3. **用户体验**：

   - 快速响应简单问题
   - 深度分析复杂问题
   - 提供进度反馈

4. **成本控制**：
   - 优先使用免费/便宜的模型
   - 合理设置 token 限制
   - 避免重复调用

---

**祝你使用愉快！🎉**

如有问题，查看日志或参考 OpenAgents 官方文档。
