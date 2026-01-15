# Symphony MVP - 架构 V2（编排器模式）

## 概述

简化的架构，使用**直接调用**而不是事件系统。所有交互由 Daily Assistant Orchestrator 协调。

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         用户                                 │
└────────────────────┬────────────────────────────────────────┘
                     │ 消息
                     ↓
┌─────────────────────────────────────────────────────────────┐
│          Daily Assistant Orchestrator (Python)               │
│  - 接收用户消息                                              │
│  - 判断是否需要分析                                          │
│  - 协调分析流程                                              │
│  - 返回结果给用户                                            │
└──────────┬──────────────────────┬───────────────────────────┘
           │                      │
           │ 直接调用             │ 直接调用
           ↓                      ↓
    ┌─────────────┐        ┌─────────────┐
    │  Analyst    │        │  Creator    │
    │  (核心逻辑)  │        │  (核心逻辑)  │
    │             │        │             │
    │ - 分析内容   │        │ - 生成计划   │
    │ - 返回洞察   │        │ - 返回步骤   │
    └─────────────┘        └─────────────┘
```

## 组件说明

### 1. Daily Assistant Orchestrator

- **类型**: CollaboratorAgent (Python)
- **职责**:
  - 监听频道消息
  - 判断是否需要深度分析
  - 直接调用 Analyst 和 Creator
  - 整合结果并发送给用户
- **文件**: `agents/daily_assistant_orchestrator.py`

### 2. Analyst Agent (核心逻辑)

- **类型**: WorkerAgent (Python)
- **职责**:
  - 提供 `perform_analysis()` 方法
  - 使用框架库进行分析
  - 返回洞察列表
- **文件**: `agents/analyst_agent.py`
- **不再作为独立进程运行**

### 3. Creator Agent (核心逻辑)

- **类型**: WorkerAgent (Python)
- **职责**:
  - 提供 `create_action_plan()` 方法
  - 生成结构化行动计划
  - 返回计划字典
- **文件**: `agents/creator_agent.py`
- **不再作为独立进程运行**

## 消息流程

### 普通对话

```
用户: "你好"
  ↓
Orchestrator: 检测不需要分析
  ↓
Orchestrator: 直接友好回复
  ↓
用户收到: "你好！我是你的日常助理..."
```

### 深度分析流程

```
用户: "最近工作压力很大"
  ↓
Orchestrator: 检测需要分析
  ↓
Orchestrator → 用户: "我理解你的感受。让我为你进行深入分析..."
  ↓
Orchestrator.analyst.perform_analysis()
  ↓
Orchestrator.creator.create_action_plan()
  ↓
Orchestrator: 整合结果
  ↓
用户收到: "📊 分析完成\n💡 关键洞察：...\n🎯 行动计划：..."
```

## 优势

### ✅ 相比事件系统的优势

1. **简单直接**: 不依赖复杂的事件系统
2. **易于调试**: 调用栈清晰，错误容易追踪
3. **无需 messaging mod**: 避免了 WorkerAgent 无法访问 messaging mod 的问题
4. **性能更好**: 减少了事件传递的开销
5. **代码更少**: 不需要事件监听和分发逻辑

### ✅ 保留的功能

1. **所有分析框架**: HUMAN 3.0, MBTI, Big Five 等
2. **Memory Palace**: 长期记忆和用户画像
3. **Simple Storage**: 消息、分析、计划存储
4. **API 优化**: 消息去重、冷却时间等

## 数据流

```
用户消息
  ↓
Simple Storage (保存消息)
  ↓
Analyst 分析
  ↓
Memory Palace (保存洞察)
  ↓
Simple Storage (保存分析)
  ↓
Creator 生成计划
  ↓
Simple Storage (保存计划)
  ↓
返回给用户
```

## 启动方式

```bash
cd network
./restart_orchestrator.sh
```

## 配置文件

- `network.yaml` - 网络配置（无认证）
- `configs/daily_assistant.yaml` - Daily Assistant 配置（未使用，因为用 Python 版本）
- `.env` - 环境变量（GROQ_API_KEY）

## 日志

- `logs/network.log` - 网络服务日志
- `logs/日常助理编排器.log` - Orchestrator 日志

## 测试

发送测试消息到频道：

```
最近工作压力很大
```

预期响应：

1. "我理解你的感受。让我为你进行深入分析..."
2. 完整的分析结果和行动计划

## 扩展

如需添加新功能：

1. 在 Orchestrator 中添加新的判断逻辑
2. 创建新的 Agent 类提供核心功能
3. 在 Orchestrator 中调用新 Agent 的方法

## 注意事项

- Analyst 和 Creator 不再作为独立进程运行
- 所有逻辑都在 Orchestrator 进程中执行
- 如果需要并发处理，可以使用 asyncio.gather()
