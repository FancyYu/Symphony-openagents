# 🚀 Symphony 快速测试指南

## ✅ 修改确认

已完成的修改：

- ✅ Listener: 捕获并传递频道信息
- ✅ Analyst: 解析并传递频道信息
- ✅ Creator: 发送到原始频道（而不是用户 ID）

---

## 🎯 测试步骤

### 第 1 步: 启动网络服务

```bash
cd network
openagents network start .
```

**预期输出**:

```
✅ Network started successfully
🌐 Studio: http://localhost:8700/studio/
📡 HTTP: http://localhost:8700
🔌 gRPC: localhost:8600
```

**等待**: 看到 "Network started" 后继续

---

### 第 2 步: 设置环境变量

```bash
export GROQ_API_KEY=你的GROQ密钥
```

**验证**:

```bash
echo $GROQ_API_KEY
```

---

### 第 3 步: 启动 Symphony 系统

**新开一个终端窗口**:

```bash
cd network
python start_symphony.py
```

**预期输出**:

```
🎻 SYMPHONY MVP - 多智能体个人成长系统
============================================================

📁 设置项目结构...
   ✅ agents/
   ✅ shared/
   ✅ configs/
   ✅ logs/
   ✅ data/
   ✅ storage/

🔧 检查依赖...
   ✅ OpenAgents: 已安装

🌐 检查网络服务...
   ✅ 网络服务正在运行

🔑 检查环境变量...
   ✅ GROQ_API_KEY: 已设置

============================================================
启动智能体组件
============================================================

🚀 启动日常助理...
   ✅ 已启动 (PID: xxxx)

⏳ 等待日常助理启动 (5秒)...

🚀 启动日常助理监听器...
   ✅ 已启动 (PID: xxxx)

🚀 启动分析师智能体...
   ✅ 已启动 (PID: xxxx)

🚀 启动创作者智能体...
   ✅ 已启动 (PID: xxxx)

============================================================
✅ Symphony 系统启动完成！
============================================================
```

**如果看到错误**: 检查日志文件

```bash
tail -f logs/日常助理.log
tail -f logs/分析师智能体.log
```

---

### 第 4 步: 打开 Studio

1. 打开浏览器
2. 访问: **http://localhost:8700/studio/**
3. 登录:
   - Username: **admin**
   - Password: **admin**

---

### 第 5 步: 发送测试消息

在 **general** 频道发送以下任一消息：

#### 测试 1: 压力管理（通用框架）

```
最近工作压力很大，经常加班到很晚，感觉很焦虑
```

#### 测试 2: MBTI 分析

```
我想了解自己的性格类型，用 MBTI 帮我分析一下
```

#### 测试 3: 职业发展

```
我对职业发展感到困惑，不知道该往哪个方向走
```

#### 测试 4: 成长分析

```
如何提升自己的学习能力和成长思维？
```

---

## 🔍 预期结果

### 时间线

| 时间         | 你会看到                   |
| ------------ | -------------------------- |
| **T+0 秒**   | 你的消息出现在频道         |
| **T+0.5 秒** | Daily Assistant 立即回复   |
| **T+4 秒**   | Creator Agent 发送完整报告 |

### 示例输出

```
┌─────────────────────────────────────────────┐
│ General 频道                                 │
├─────────────────────────────────────────────┤
│                                             │
│ 👤 admin (你)                               │
│ 最近工作压力很大，经常加班到很晚，感觉很焦虑  │
│ 刚刚                                         │
│                                             │
│ ─────────────────────────────────────────── │
│                                             │
│ 🤖 daily-assistant                          │
│ 我理解你的感受。工作压力和焦虑确实很困扰人。  │
│ 让我帮你深入分析一下压力来源和应对方法。      │
│ 我会连接我们的分析师为你提供专业的洞察。      │
│ 刚刚                                         │
│                                             │
│ ─────────────────────────────────────────── │
│                                             │
│ 🎨 creator-agent                            │
│ 🎯 压力管理与工作效率提升计划                │
│                                             │
│ 📝 通过时间管理、情绪调节和沟通技巧，        │
│ 系统性地降低工作压力，提升生活质量            │
│                                             │
│ 📋 行动计划:                                │
│                                             │
│ 1. 实施番茄工作法，每25分钟专注工作后休息... │
│    💡 提高工作效率，减少加班时间             │
│                                             │
│ 2. 每天进行10分钟深呼吸或冥想练习...        │
│    💡 缓解焦虑，提升情绪稳定性               │
│                                             │
│ 3. 使用艾森豪威尔矩阵整理任务优先级...      │
│    💡 明确重点，避免被琐事淹没               │
│                                             │
│ 4. 与上级预约一对一会议，讨论工作量...      │
│    💡 获得支持，调整工作负荷                 │
│                                             │
│ 5. 设定工作边界，晚上8点后不处理工作邮件... │
│    💡 改善工作生活平衡，保护个人时间         │
│                                             │
│ 🌟 开始行动吧！如果需要调整或有任何问题，    │
│ 随时告诉我。                                 │
│ 刚刚                                         │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📊 监控日志（可选）

### 实时查看日志

**终端 1**: Listener 日志

```bash
tail -f logs/日常助理监听器.log
```

**终端 2**: Analyst 日志

```bash
tail -f logs/分析师智能体.log
```

**终端 3**: Creator 日志

```bash
tail -f logs/创作者智能体.log
```

### 预期日志输出

**Listener**:

```
📨 收到消息 from admin
   用户: admin
   内容: 最近工作压力很大...
   🎯 检测到需要分析的内容
   📤 已发送分析请求给分析师智能体 (频道: general)
```

**Analyst**:

```
📊 收到分析请求
   用户: admin
   框架: general
   频道: general
   内容: 最近工作压力很大...
   ✅ 分析完成: 5 个洞察
   📤 已发送分析结果给创作者智能体
```

**Creator**:

```
📋 收到分析结果
   用户: admin
   框架: general
   洞察数量: 5
   目标频道: general
   ✅ 行动计划已发送到频道: general
   📤 标题: 压力管理与工作效率提升计划
```

---

## ❌ 常见问题排查

### 问题 1: 网络服务无法启动

**症状**: `Connection refused` 或 `502 Bad Gateway`

**解决**:

```bash
# 检查端口占用
lsof -i :8700
lsof -i :8600

# 如果有占用，杀掉进程
kill -9 <PID>

# 重新启动
openagents network start .
```

---

### 问题 2: Agent 无法启动

**症状**: 日志显示 "Agent already registered"

**解决**:

```bash
# 停止所有 agent
pkill -9 -f "openagents agent"
pkill -9 -f "daily_assistant_listener"
pkill -9 -f "analyst_agent"
pkill -9 -f "creator_agent"

# 等待30秒让网络服务清理
sleep 30

# 重新启动
python start_symphony.py
```

---

### 问题 3: Daily Assistant 回复但没有分析报告

**可能原因**:

1. Listener 没有检测到关键词
2. Analyst 或 Creator 没有启动

**检查**:

```bash
# 检查进程
ps aux | grep python | grep agent

# 检查日志
tail -20 logs/日常助理监听器.log
tail -20 logs/分析师智能体.log
tail -20 logs/创作者智能体.log
```

---

### 问题 4: GROQ API 错误

**症状**: 日志显示 API 错误

**解决**:

```bash
# 验证 API key
echo $GROQ_API_KEY

# 重新设置
export GROQ_API_KEY=你的密钥

# 重启 agents
```

---

## 🎉 测试成功标志

✅ 你应该看到：

1. Daily Assistant 立即回复
2. 4 秒后收到完整的分析报告
3. 报告包含：标题、概述、3-5 个行动步骤
4. 所有消息都在同一个频道

✅ 日志中应该看到：

1. Listener 检测到关键词
2. Analyst 完成分析
3. Creator 发送到频道

---

## 🔄 停止系统

```bash
# 在 start_symphony.py 运行的终端按 Ctrl+C

# 或者手动停止
pkill -9 -f "openagents agent"
pkill -9 -f "daily_assistant_listener"
pkill -9 -f "analyst_agent"
pkill -9 -f "creator_agent"

# 停止网络服务
# 在网络服务终端按 Ctrl+C
```

---

## 📝 测试检查清单

- [ ] 网络服务启动成功
- [ ] GROQ_API_KEY 已设置
- [ ] 4 个 agent 都启动成功
- [ ] Studio 可以访问
- [ ] 可以登录 (admin/admin)
- [ ] 发送测试消息
- [ ] Daily Assistant 立即回复
- [ ] 收到完整的分析报告
- [ ] 报告格式正确
- [ ] 所有消息在同一频道

---

## 🎯 准备好了！

现在你可以开始测试了！

**快速启动命令**:

```bash
# 终端1
cd network && openagents network start .

# 终端2（等待网络启动后）
cd network && export GROQ_API_KEY=你的密钥 && python start_symphony.py

# 浏览器
http://localhost:8700/studio/
```

祝测试顺利！🎻
