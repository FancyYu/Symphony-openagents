# 🎻 Symphony - 个人成长 AI 助手系统

Symphony 是一个基于 OpenAgents 平台构建的个人成长 AI 助手系统。系统采用单一集成 agent 架构，提供日常对话、情感支持、深度分析和行动计划等全方位服务。

## 🌟 系统特点

- **一体化助手**：日常对话、分析、计划全部集成
- **深度框架分析**：支持 MBTI、Big Five、HUMAN 3.0 等多种心理学框架
- **个性化计划**：生成具体可执行的行动方案
- **中文优化**：完全中文交互，符合中国用户习惯
- **简单稳定**：单一 agent 架构，避免复杂的 agent 间通信

## 🏗️ 系统架构

```
用户 (User)
    ↓
日常助理 (Daily Assistant) - 集成式 YAML Agent
    ├─ 日常对话能力
    ├─ 深度分析能力 (MBTI, Big Five, HUMAN 3.0)
    └─ 行动计划生成能力
    ↓
用户 (User) - 收到分析和计划
```

### 架构演进

**V1 (已废弃)**: 多 agent 架构 (Python WorkerAgent)

- 问题：WorkerAgent 无法访问 messaging mod

**V2 (已废弃)**: 多 agent 架构 (Python CollaboratorAgent)

- 问题：gRPC 认证失败

**V3 (已废弃)**: 多 agent 架构 (YAML + 指令过滤)

- 问题：LLM 指令过滤不可靠，agent 循环对话

**V4 (当前)**: 单一集成 agent 架构

- ✅ 稳定可靠
- ✅ 功能完整
- ✅ 易于维护

## 📦 核心组件

### Daily Assistant (日常助理)

- **类型**: YAML 配置的 CollaboratorAgent
- **文件**: `agents/daily_assistant_integrated.yaml`
- **模型**: Qwen Plus (通义千问)
- **核心能力**:
  - 日常对话和情感支持
  - 深度心理分析（MBTI、Big Five、HUMAN 3.0）
  - 行动计划生成
  - 持续陪伴和指导

### 分析框架库

系统内置多种专业分析框架：

#### 1. MBTI（性格类型分析）

- **维度**: E/I、S/N、T/F、J/P
- **适用**: 性格特点、职业匹配、人际关系
- **输出**: 16 种性格类型 + 详细分析

#### 2. Big Five（五大人格特质）

- **维度**: 开放性、尽责性、外向性、宜人性、神经质
- **适用**: 全面性格评估、行为预测
- **输出**: 各维度评分 + 特质组合分析

#### 3. HUMAN 3.0（全面成长模型）

- **维度**: 健康、理解、意义、行动、关系
- **适用**: 整体生活评估、平衡发展
- **输出**: 五维度评估 + 提升路径

#### 4. 职业发展框架

- **维度**: 技能、兴趣、价值观、路径、障碍
- **适用**: 职业规划、转型决策
- **输出**: 现状评估 + 机会识别

#### 5. 通用深度分析

- **步骤**: 现状识别 → 根因分析 → 影响评估 → 机会发现
- **适用**: 任何需要深入思考的问题
- **输出**: 多角度洞察 + 系统性建议

## � 快速开始

### 前置要求

1. **安装 OpenAgents**

```bash
pip install openagents --upgrade
```

2. **配置 API Key**

**方式 1: 使用环境变量（推荐）**

```bash
export QWEN_API_KEY="your-qwen-api-key-here"
```

**方式 2: 使用 .env 文件**

```bash
# 复制示例文件
cp network/.env.example network/.env

# 编辑 .env 文件，填入你的 API Key
# QWEN_API_KEY=your-qwen-api-key-here
```

**获取 Qwen API Key:**

- 访问: https://dashscope.console.aliyun.com/apiKey
- 注册/登录阿里云账号
- 创建 API Key

### 启动系统

**步骤 1: 启动 Network**

```bash
cd network
openagents network start .
```

**步骤 2: 启动 Daily Assistant**

在新终端运行：

```bash
# 确保已设置环境变量
export QWEN_API_KEY="your-qwen-api-key-here"
#如果环境变量无法设置也可以直接将 daily_assistant_integrated.yaml中的api key替换成你的api key。

# 启动 agent
cd network/agents
openagents agent start daily_assistant_integrated.yaml
```

### 开始使用

1. 打开浏览器访问: http://localhost:8700/studio/
2. 登录: admin / admin
3. 在 general 频道发送消息

### 使用示例

#### 日常对话

```
你: 你好
助理: 你好！我是你的日常助理，有什么可以帮助你的吗？😊

你: 最近工作压力很大
助理: [提供情感支持和基础建议]
```

#### 深度分析

```
你: 用 MBTI 分析我的性格
助理: 📊 MBTI 分析报告
     [详细的性格类型分析、优势、盲点、发展建议]

你: 帮我做 Big Five 分析
助理: 📊 Big Five 分析报告
     [五大人格维度评估和建议]

你: 用 HUMAN 3.0 框架评估我的状态
助理: 📊 HUMAN 3.0 分析报告
     [健康、理解、意义、行动、关系五维度评估]
```

#### 行动计划

```
你: 帮我制定英语学习计划
助理: 🎯 英语学习行动计划
     [具体步骤、时间框架、预期效果、可导出清单]

你: 给我一个职业发展方案
助理: 🎯 职业发展行动计划
     [分阶段规划、检查点、成功指标]
```

## 📊 工作流程

### 简单对话流程

```
用户消息 → Daily Assistant → 回复
```

### 深度分析流程

```
用户请求分析
    ↓
Daily Assistant 检测关键词
    ↓
执行框架分析（MBTI/Big Five/HUMAN 3.0）
    ↓
生成结构化分析报告
    ↓
返回给用户
```

### 行动计划流程

```
用户请求计划
    ↓
Daily Assistant 理解目标
    ↓
生成分阶段行动计划
    ↓
包含时间框架、预期效果、检查点
    ↓
提供可导出格式
    ↓
返回给用户
```

## 🔧 配置说明

### API 配置

**推荐方式：使用环境变量**

```bash
# 在启动 agent 前设置
export QWEN_API_KEY="your-qwen-api-key-here"
```

**配置文件中的引用：**

在 `agents/daily_assistant_integrated.yaml` 中：

```yaml
config:
  model_name: "qwen-plus"
  provider: "openai"
  api_key: "${QWEN_API_KEY}" # 从环境变量读取
  api_base: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  temperature: 0.7
  max_tokens: 1000
```

### Network 配置

在 `network.yaml` 中：

```yaml
network:
  name: "Symphony Network"
  port: 8700
  grpc_port: 8600
```

### 日志配置

日志自动保存在：

- `agents/openagents.log` - Agent 运行日志
- `openagents.log` - Network 日志

## 🛠️ 故障排除

### 问题 1: Network 无法启动

**症状**: `openagents network start .` 失败

**解决**:

```bash
# 检查端口占用
lsof -i :8700
lsof -i :8600

# 杀死占用进程
kill -9 <PID>

# 重新启动
openagents network start .
```

### 问题 2: Agent 无法连接

**症状**: Agent 启动后显示连接失败

**解决**:

```bash
# 确认 Network 正在运行
ps aux | grep openagents

# 检查 network.yaml 配置
cat network.yaml

# 确认端口配置正确（8700 HTTP, 8600 gRPC）
```

### 问题 3: Agent 不回复

**症状**: 发送消息后没有回复

**解决**:

```bash
# 查看 Agent 日志
tail -f agents/openagents.log

# 检查是否有 API 调用（应该看到 200 OK）
grep "200 OK" agents/openagents.log

# 检查是否有错误
grep "ERROR" agents/openagents.log

# 确认配置中有 react_to_all_messages: true
grep "react_to_all_messages" agents/daily_assistant_integrated.yaml
```

### 问题 4: API Key 错误

**症状**: 日志显示 401 Unauthorized

**解决**:

```bash
# 检查 API Key 配置
grep "api_key" agents/daily_assistant_integrated.yaml

# 测试 API Key
curl -X POST "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-plus","messages":[{"role":"user","content":"你好"}]}'
```

### 问题 5: 中文乱码

**症状**: 回复中出现乱码

**解决**:

- 确认终端支持 UTF-8
- 检查 instruction 中是否明确要求中文回复
- 查看 system_message 配置

## 📚 文档

### 核心文档

- `README.md` - 本文档（系统概述和快速开始）
- `HOW_TO_USE.md` - 详细使用指南

### 架构文档

- `doc/ARCHITECTURE.md` - 系统架构说明
- `doc/MULTI_AGENT_ARCHITECTURE.md` - 多 agent 架构（已废弃）
- `doc/AGENT_COMMUNICATION_EXPLAINED.md` - Agent 通信机制详解
- `doc/SOLUTION_COMPARISON.md` - 方案对比

### 使用指南

- `doc/SPECIALIST_AGENTS_GUIDE.md` - 专业 Agent 使用指南
- `doc/QUICK_TEST_SPECIALIST.md` - 快速测试指南
- `doc/YAML_AGENTS_GUIDE.md` - YAML Agent 配置指南

### 部署文档

- `doc/DEPLOYMENT_GUIDE.md` - 部署指南
- `doc/TROUBLESHOOTING.md` - 故障排除

### 创新说明

- `doc/INNOVATION_POINTS.md` - 创新点详解
- `doc/INNOVATION_SUMMARY.md` - 创新总结

## 🎯 功能特性

### ✅ 已实现

- [x] 日常对话和情感支持
- [x] MBTI 性格分析
- [x] Big Five 人格分析
- [x] HUMAN 3.0 全面成长评估
- [x] 职业发展分析
- [x] 通用深度分析
- [x] 行动计划生成
- [x] 中文优化
- [x] 结构化输出
- [x] 可导出计划格式

### 🚧 计划中

- [ ] 多用户支持
- [ ] 对话历史管理
- [ ] 分析结果持久化
- [ ] 进度追踪功能
- [ ] 数据可视化
- [ ] 外部工具集成（Notion、Todoist）
- [ ] 语音交互
- [ ] 移动端支持

## 🔄 版本历史

### V4 (当前) - 单一集成 Agent

- ✅ 稳定的单 agent 架构
- ✅ 完整的分析和计划功能
- ✅ 中文优化
- ✅ 简化维护

### V3 (已废弃) - YAML 多 Agent + 指令过滤

- ❌ LLM 指令过滤不可靠
- ❌ Agent 循环对话问题

### V2 (已废弃) - Python CollaboratorAgent

- ❌ gRPC 认证失败

### V1 (已废弃) - Python WorkerAgent

- ❌ WorkerAgent 无法访问 messaging mod

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- 基于 [OpenAgents](https://openagents.org/) 平台构建
- 使用 [Qwen](https://tongyi.aliyun.com/) API
- 心理学框架参考多个开源项目
