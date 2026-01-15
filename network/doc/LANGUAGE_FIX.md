# 🌐 语言问题修复指南

## 问题描述

Daily Assistant 回复时使用了错误的语言（泰文而不是中文）：

```
用户: "hello？"
Daily Assistant: "สวัสดี ฉันกำลังดีครับ"  ❌ 泰文
```

**期望行为**:

```
用户: "hello？"
Daily Assistant: "你好！我是你的日常助理，有什么可以帮助你的吗？"  ✅ 中文
```

---

## 🔧 已应用的修复

### 1. 增强 system_message

在 `configs/daily_assistant.yaml` 中添加了明确的系统消息：

```yaml
llm_config:
  system_message: "You are a Chinese-speaking assistant. You MUST respond ONLY in Chinese (中文). Never use English, Thai, or any other language. Always use simplified Chinese characters."
```

### 2. 强化 instruction

在指令中添加了：

- 【必须】标记强调语言要求
- 明确禁止使用其他语言
- 添加了示例对话

---

## 🚀 应用修复步骤

### 方法 1: 完全重启（推荐）

```bash
cd network

# 1. 停止所有 agents
pkill -9 -f "openagents agent"
pkill -9 -f "python.*agent"

# 2. 等待 API 恢复（避免 429 错误）
sleep 60

# 3. 使用修复脚本重启
./restart_fixed.sh
```

### 方法 2: 仅重启 Daily Assistant

如果其他 agents 工作正常，只重启 Daily Assistant：

```bash
# 1. 停止 Daily Assistant
pkill -f "daily_assistant.yaml"

# 2. 等待 5 秒
sleep 5

# 3. 重启
cd network
openagents agent start configs/daily_assistant.yaml > logs/日常助理.log 2>&1 &

# 4. 检查日志
tail -f logs/日常助理.log
```

---

## ✅ 验证修复

### 1. 测试简单问候

在 Studio 中发送：

```
hello？
```

**期望回复**（中文）:

```
你好！我是你的日常助理，有什么可以帮助你的吗？
```

### 2. 测试分析触发

发送：

```
最近工作压力很大，经常加班到很晚，感觉很焦虑
```

**期望回复**（中文）:

```
我理解你的感受。让我为你进行深入分析，找出解决方案。
```

### 3. 检查日志

```bash
# 查看最近的回复
tail -20 logs/日常助理.log

# 应该看到中文回复，不应该看到泰文或英文
```

---

## 🐛 如果问题仍然存在

### 可能原因 1: 配置未重新加载

**症状**: 重启后还是回复泰文

**解决**:

```bash
# 确保完全停止
pkill -9 -f "daily_assistant"
sleep 10

# 验证进程已停止
ps aux | grep daily_assistant

# 重新启动
cd network
openagents agent start configs/daily_assistant.yaml > logs/日常助理.log 2>&1 &
```

### 可能原因 2: LLM 模型问题

**症状**: 即使配置正确，模型还是不遵守指令

**解决**: 尝试更换模型

编辑 `configs/daily_assistant.yaml`:

```yaml
config:
  model_name: "llama-3.3-70b-versatile" # 更大的模型

llm_config:
  model: "llama-3.3-70b-versatile"
  temperature: 0.5 # 降低温度，更确定性
```

### 可能原因 3: API 缓存

**症状**: 前几条消息还是错误语言，后面才正常

**解决**: 清除对话历史

```bash
# 在 Studio 中开始新对话
# 或者清空数据库
sqlite3 data/symphony_mvp.db "DELETE FROM user_messages;"
```

---

## 📊 监控语言一致性

### 创建测试脚本

```bash
# 创建 test_language.sh
cat > network/test_language.sh << 'EOF'
#!/bin/bash

echo "🧪 测试 Daily Assistant 语言一致性"
echo ""

# 测试用例
test_cases=(
    "hello"
    "你好"
    "how are you"
    "最近怎么样"
    "I need help"
    "我需要帮助"
)

for msg in "${test_cases[@]}"; do
    echo "📤 发送: $msg"
    # 这里需要通过 API 发送消息并检查回复
    # 实际实现需要调用 OpenAgents API
    echo ""
done
EOF

chmod +x network/test_language.sh
```

---

## 🎯 成功标准

✅ 所有回复都使用简体中文
✅ 不出现英文、泰文或其他语言
✅ 回复内容相关且有意义
✅ 分析流程正常触发
✅ 用户体验流畅

---

## 📝 配置文件位置

- **主配置**: `network/configs/daily_assistant.yaml`
- **日志文件**: `network/logs/日常助理.log`
- **重启脚本**: `network/restart_fixed.sh`

---

## 💡 预防措施

### 1. 在配置中始终指定语言

```yaml
llm_config:
  system_message: "You MUST respond in Chinese (中文)."
```

### 2. 在 instruction 中重复强调

```yaml
config:
  instruction: |
    【必须】始终用中文回复
    ...
```

### 3. 添加示例对话

```yaml
config:
  instruction: |
    示例对话：
    用户："hello"
    你："你好！"
```

### 4. 降低 temperature

```yaml
llm_config:
  temperature: 0.5 # 更确定性，更遵守指令
```

---

## 🚀 立即行动

```bash
# 1. 进入目录
cd network

# 2. 完全重启
pkill -9 -f "openagents agent"
pkill -9 -f "python.*agent"
sleep 60
./restart_fixed.sh

# 3. 测试
# 打开 http://localhost:8700/studio/
# 发送: "hello？"
# 期望: 中文回复

# 4. 验证
tail -f logs/日常助理.log
```

现在 Daily Assistant 应该始终用中文回复了！🎉
