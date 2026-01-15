# 专业 Agent 快速测试指南

## 测试前准备

### 1. 确认 Network 运行

```bash
ps aux | grep openagents
# 应该看到 network 进程在运行
```

### 2. 启动 Agent

#### 方式 1：使用脚本（推荐）

```bash
cd network
chmod +x restart_specialist_agents.sh
./restart_specialist_agents.sh
```

#### 方式 2：手动启动

```bash
# 终端 1：启动分析师
cd network/configs
openagents agent start analyst_agent.yaml

# 终端 2：启动创作者
cd network/configs
openagents agent start creator_agent.yaml
```

### 3. 确认 Agent 启动成功

```bash
# 查看进程
ps aux | grep "analyst_agent"
ps aux | grep "creator_agent"

# 查看日志（等待 5-10 秒后）
tail -20 network/logs/analyst_agent.log
tail -20 network/logs/creator_agent.log

# 成功标志：
# - 看到 "Successfully loaded"
# - 没有 "ERROR" 或 "Failed"
# - 看到 "Listening for messages"
```

## 测试场景

### 测试 1：Analyst Agent 基础响应

**发送消息：**

```
@analyst-agent 你好
```

**预期结果：**

```
我是专业分析师，需要深度框架分析时请 @我 或说'分析师帮我分析'。
```

**检查点：**

- ✅ Agent 有回复
- ✅ 回复简短
- ✅ 提示如何使用

---

### 测试 2：Analyst Agent MBTI 分析

**发送消息：**

```
分析师，用 MBTI 分析我。我是一个内向的人，喜欢独处思考，但在需要的时候也能很好地与人交流。我更关注未来可能性而不是当下细节，做决定时会综合考虑逻辑和他人感受。我喜欢有计划但也保持灵活性。
```

**预期结果：**

- 📊 完整的 MBTI 分析报告
- 包含：核心洞察、优势识别、挑战与盲点、发展建议
- 格式清晰，使用 emoji 标记
- 分析深入，有具体建议

**检查点：**

- ✅ 识别出可能的 MBTI 类型（如 INFJ、INFP 等）
- ✅ 分析了四个维度
- ✅ 提供了具体的发展建议
- ✅ 建议了短期、中期、长期目标

---

### 测试 3：Analyst Agent Big Five 分析

**发送消息：**

```
@analyst-agent 用 Big Five 分析我的性格
```

**预期结果：**

- 📊 Big Five 分析报告
- 评估五个维度：开放性、尽责性、外向性、宜人性、神经质
- 每个维度有具体分析
- 提供平衡建议

**检查点：**

- ✅ 分析了所有五个维度
- ✅ 识别了优势和挑战
- ✅ 提供了具体建议

---

### 测试 4：Creator Agent 基础响应

**发送消息：**

```
@creator-agent 你好
```

**预期结果：**

```
我是行动计划创作者，需要制定详细计划时请 @我 或说'创作者帮我做计划'。
```

**检查点：**

- ✅ Agent 有回复
- ✅ 回复简短
- ✅ 提示如何使用

---

### 测试 5：Creator Agent 行动计划

**发送消息：**

```
创作者，我想提升英语口语能力，帮我制定一个3个月的学习计划
```

**预期结果：**

- 🎯 完整的行动计划
- 包含：计划概述、分阶段步骤、预期效果、检查点
- 每个步骤有明确时间框架
- 包含可导出的任务清单格式
- 有成功指标和注意事项

**检查点：**

- ✅ 计划分为多个阶段
- ✅ 每个步骤具体可执行
- ✅ 有明确的时间框架
- ✅ 包含检查点和成功指标
- ✅ 有可复制的任务清单格式

---

### 测试 6：完整工作流

**步骤 1：日常对话**

```
最近工作压力很大，感觉有点迷茫
```

_（Daily Assistant 会回复）_

**步骤 2：请求深度分析**

```
分析师，帮我用 HUMAN 3.0 框架分析一下我的状态
```

_（Analyst Agent 会提供深度分析）_

**步骤 3：请求行动计划**

```
创作者，根据分析结果帮我制定一个压力管理和职业发展计划
```

_（Creator Agent 会生成详细计划）_

**检查点：**

- ✅ 三个 agent 各司其职
- ✅ 没有 agent 之间的循环对话
- ✅ 分析和计划相互呼应
- ✅ 整体流程顺畅

---

## 常见问题排查

### 问题 1：Agent 不回复

**检查步骤：**

```bash
# 1. 确认 agent 进程运行
ps aux | grep "analyst_agent"

# 2. 查看日志
tail -50 network/logs/analyst_agent.log

# 3. 查看是否有 API 调用
grep "200 OK" network/logs/analyst_agent.log

# 4. 查看是否有错误
grep "ERROR" network/logs/analyst_agent.log
```

**可能原因：**

- Agent 未启动
- API key 无效
- Network 连接问题
- 消息未触发（检查触发词）

---

### 问题 2：Agent 回复但内容不对

**检查步骤：**

```bash
# 查看完整日志
tail -100 network/logs/analyst_agent.log

# 查看 API 响应
grep "response" network/logs/analyst_agent.log
```

**可能原因：**

- 模型理解错误
- 指令不够清晰
- 温度参数设置问题

---

### 问题 3：Agent 相互聊天

**检查步骤：**

```bash
# 查看消息来源
grep "from_agent" network/logs/analyst_agent.log
```

**解决方案：**

- 确认指令中有"不要回复其他 agent"
- 检查 `react_to_all_messages` 设置
- 考虑只使用 Daily Assistant 进行日常对话

---

### 问题 4：API 调用失败

**检查步骤：**

```bash
# 查看 API 错误
grep "401\|403\|500" network/logs/analyst_agent.log

# 测试 API key
curl -X POST "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions" \
  -H "Authorization: Bearer sk-d5c9b87505ac449fa8be658240744e2e" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-plus","messages":[{"role":"user","content":"你好"}]}'
```

**可能原因：**

- API key 过期或无效
- API 配额用完
- 网络连接问题

---

## 性能测试

### 响应时间测试

```bash
# 记录发送消息时间
date +%s

# 发送测试消息
# （在聊天界面发送）

# 记录收到回复时间
date +%s

# 计算差值（应该在 3-10 秒内）
```

### 并发测试

```bash
# 同时发送多条消息
# 观察 agent 是否能正确处理
```

---

## 测试清单

### Analyst Agent

- [ ] 基础响应测试
- [ ] MBTI 分析测试
- [ ] Big Five 分析测试
- [ ] HUMAN 3.0 分析测试
- [ ] 职业发展分析测试
- [ ] 通用深度分析测试
- [ ] 不相关消息过滤测试

### Creator Agent

- [ ] 基础响应测试
- [ ] 学习计划生成测试
- [ ] 职业发展计划测试
- [ ] 健康管理计划测试
- [ ] 导出格式测试
- [ ] 不相关消息过滤测试

### 集成测试

- [ ] 完整工作流测试
- [ ] Agent 不互相回复测试
- [ ] 多用户并发测试
- [ ] 长时间运行稳定性测试

---

## 测试报告模板

```markdown
# 测试报告

**测试日期：** 2026-01-15
**测试人员：** [你的名字]

## 测试环境

- Network 版本：
- Agent 版本：
- 模型：qwen-plus

## 测试结果

### Analyst Agent

- 基础响应：✅ / ❌
- MBTI 分析：✅ / ❌
- Big Five 分析：✅ / ❌
- 问题：[描述问题]

### Creator Agent

- 基础响应：✅ / ❌
- 计划生成：✅ / ❌
- 导出格式：✅ / ❌
- 问题：[描述问题]

### 集成测试

- 完整工作流：✅ / ❌
- Agent 隔离：✅ / ❌
- 问题：[描述问题]

## 改进建议

1. [建议 1]
2. [建议 2]
3. [建议 3]
```

---

## 下一步

测试通过后：

1. 记录测试结果
2. 优化 agent 配置
3. 添加更多分析框架
4. 实现外部导出功能
5. 添加进度追踪功能
