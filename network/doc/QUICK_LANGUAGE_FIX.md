# 🚀 快速修复语言问题

## 问题

Daily Assistant 回复泰文而不是中文：

```
用户: "hello？"
回复: "สวัสดี ฉันกำลังดีครับ" ❌
```

## 已修复

✅ 添加了强制中文的 system_message
✅ 在 instruction 中添加了示例对话
✅ 明确禁止使用其他语言

## 立即应用修复

### 方法 1: 使用快速修复脚本（推荐）

```bash
cd network
./fix_language_now.sh
```

### 方法 2: 手动重启

```bash
cd network

# 停止所有
pkill -9 -f "openagents agent"
pkill -9 -f "python.*agent"

# 等待 30 秒
sleep 30

# 重启
openagents agent start configs/daily_assistant.yaml > logs/日常助理.log 2>&1 &
sleep 5
python3 agents/daily_assistant_listener.py > logs/日常助理监听器.log 2>&1 &
sleep 3
python3 agents/analyst_agent.py > logs/分析师智能体.log 2>&1 &
sleep 3
python3 agents/creator_agent.py > logs/创作者智能体.log 2>&1 &
```

## 测试

1. 打开 http://localhost:8700/studio/
2. 发送: `hello？`
3. 期望回复: `你好！我是你的日常助理，有什么可以帮助你的吗？`

## 验证

```bash
# 查看最新回复
tail -20 logs/日常助理.log

# 应该看到中文，不应该看到泰文或英文
```

## 如果还有问题

查看详细文档：

```bash
cat LANGUAGE_FIX.md
```
