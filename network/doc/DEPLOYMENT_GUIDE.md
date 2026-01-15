# Symphony MVP - 部署与运行指南

## 📋 目录

- [环境依赖](#环境依赖)
- [安装步骤](#安装步骤)
- [配置说明](#配置说明)
- [启动项目](#启动项目)
- [验证运行](#验证运行)
- [故障排查](#故障排查)

---

## 🔧 环境依赖

### 系统要求

| 组件         | 要求                             | 推荐         |
| ------------ | -------------------------------- | ------------ |
| **操作系统** | macOS 10.15+, Linux, Windows 10+ | macOS 13+    |
| **Python**   | 3.11+                            | 3.11.0       |
| **内存**     | 最低 2GB                         | 4GB+         |
| **磁盘空间** | 最低 500MB                       | 1GB+         |
| **网络**     | 需要访问 Groq API                | 稳定网络连接 |

### Python 版本验证

```bash
# 检查 Python 版本
python3 --version
# 应该显示: Python 3.11.x 或更高

# 如果版本过低，需要升级
# macOS (使用 Homebrew)
brew install python@3.11

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3.11

# Windows
# 从 https://www.python.org/downloads/ 下载安装
```

### 必需的 Python 包

```
openagents>=0.8.5
aiohttp>=3.8.0
python-dotenv>=1.0.0
```

### 可选工具

```bash
# Git (用于克隆代码)
git --version

# 虚拟环境工具
python3 -m venv --help
```

---

## 📦 安装步骤

### 步骤 1: 克隆代码

```bash
# 克隆仓库（假设代码在 GitHub）
git clone https://github.com/your-username/symphony-openagents.git

# 进入项目目录
cd symphony-openagents/network
```

**如果没有 Git**：

- 下载 ZIP 文件并解压
- 进入 `network` 目录

### 步骤 2: 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 验证虚拟环境
which python3  # 应该显示 venv 路径
```

### 步骤 3: 安装依赖

```bash
# 安装 OpenAgents
pip install openagents

# 或者从 requirements.txt 安装（如果有）
pip install -r requirements.txt

# 验证安装
openagents --version
# 应该显示: OpenAgents version 0.8.5 或更高
```

### 步骤 4: 验证安装

```bash
# 检查 Python 包
python3 -c "import openagents; print(openagents.__version__)"

# 检查 OpenAgents CLI
openagents --help
```

---

## ⚙️ 配置说明

### 1. 获取 Groq API 密钥

**⚠️ 安全警告：请勿将真实 API 密钥提交到代码仓库！**

#### 步骤：

1. 访问 [Groq Console](https://console.groq.com/)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 点击 "Create API Key"
5. 复制生成的密钥（格式：`gsk_xxxxxxxxxxxxx`）

#### 免费额度：

- 每天 14,400 请求
- 每分钟 30 请求
- 足够开发和测试使用

### 2. 配置环境变量

#### 方法 1: 使用 .env 文件（推荐）

```bash
# 在 network 目录下创建 .env 文件
cd network
touch .env

# 编辑 .env 文件
nano .env
# 或使用其他编辑器: vim .env, code .env
```

**`.env` 文件内容**：

```bash
# OpenAgents 全局环境变量
# ⚠️ 请勿将此文件提交到 Git！

# Groq API 密钥（必需）
GROQ_API_KEY=gsk_your_actual_api_key_here

# 数据库路径（可选，默认值）
DATABASE_PATH=data/symphony_mvp.db

# 日志级别（可选）
LOG_LEVEL=INFO

# OpenAgents 配置（可选）
OPENAGENTS_HOST=localhost
OPENAGENTS_PORT=8700

# LLM 配置（可选）
DEFAULT_LLM_PROVIDER=groq
DEFAULT_LLM_MODEL_NAME=llama-3.3-70b-versatile
```

#### 方法 2: 系统环境变量

```bash
# macOS/Linux (临时，当前会话有效)
export GROQ_API_KEY="gsk_your_actual_api_key_here"

# macOS/Linux (永久，添加到 ~/.bashrc 或 ~/.zshrc)
echo 'export GROQ_API_KEY="gsk_your_actual_api_key_here"' >> ~/.zshrc
source ~/.zshrc

# Windows (临时)
set GROQ_API_KEY=gsk_your_actual_api_key_here

# Windows (永久，使用系统设置)
# 控制面板 → 系统 → 高级系统设置 → 环境变量
```

### 3. 配置 .gitignore（重要！）

确保 `.env` 文件不会被提交到 Git：

```bash
# 检查 .gitignore
cat .gitignore

# 如果没有，创建并添加
echo ".env" >> .gitignore
echo "*.log" >> .gitignore
echo "*.db" >> .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
```

### 4. 验证配置

```bash
# 验证环境变量
echo $GROQ_API_KEY
# 应该显示你的 API 密钥（前几个字符）

# 或使用 Python 验证
python3 -c "import os; print('API Key:', os.getenv('GROQ_API_KEY')[:10] + '...')"
```

---

## 🚀 启动项目

### 模式 1: 集成模式（推荐，简单）

**特点**：单一 Agent，所有功能集成在 prompt 中

```bash
# 确保在 network 目录
cd network

# 给启动脚本执行权限
chmod +x restart_integrated.sh

# 启动
./restart_integrated.sh
```

**预期输出**：

```
============================================================
🎯 Symphony MVP - 集成模式启动
============================================================

🛑 停止所有进程...
✅ GROQ_API_KEY 已加载

🌐 启动网络服务...
🚀 启动 Daily Assistant (集成模式)...

============================================================
✅ 启动完成！
============================================================
```

### 模式 2: 多 Agent 协作模式（高级）

**特点**：3 个独立 Agent 协作，职责分离

```bash
# 确保在 network 目录
cd network

# 给启动脚本执行权限
chmod +x restart_multi_agent.sh

# 启动
./restart_multi_agent.sh
```

**预期输出**：

```
============================================================
🎯 Symphony MVP - 多 Agent 协作模式
============================================================

🛑 停止所有进程...
✅ GROQ_API_KEY 已加载

🌐 启动网络服务...
🚀 启动 Coordinator Agent...
🚀 启动 Analyst Agent...
🚀 启动 Creator Agent...

============================================================
✅ 启动完成！
============================================================
```

### 手动启动（调试用）

```bash
# 终端 1: 启动网络
openagents network start .

# 终端 2: 启动 Agent（集成模式）
openagents agent start configs/daily_assistant_integrated.yaml

# 或者（多 Agent 模式）
# 终端 2: Coordinator
python3 agents/coordinator_collaborator.py

# 终端 3: Analyst
python3 agents/analyst_collaborator.py

# 终端 4: Creator
python3 agents/creator_collaborator.py
```

---

## ✅ 验证运行

### 1. 检查进程

```bash
# 查看运行的进程
ps aux | grep openagents | grep -v grep

# 应该看到：
# - openagents network start
# - openagents agent start (集成模式)
# 或
# - python3 coordinator_collaborator.py
# - python3 analyst_collaborator.py
# - python3 creator_collaborator.py
```

### 2. 检查端口

```bash
# 检查网络端口
lsof -i :8700  # HTTP 端口
lsof -i :8600  # gRPC 端口

# 应该看到 Python 进程在监听这些端口
```

### 3. 查看日志

```bash
# 查看网络日志
tail -f logs/network.log

# 查看 Agent 日志（集成模式）
tail -f logs/daily_assistant.log

# 查看 Agent 日志（多 Agent 模式）
tail -f logs/coordinator.log
tail -f logs/analyst.log
tail -f logs/creator.log
```

### 4. 访问 Web UI

```bash
# 打开浏览器访问
open http://localhost:8700

# 或手动访问
# http://localhost:8700
```

**预期看到**：

- OpenAgents 网络主页
- 显示 "Online" 状态
- 显示已连接的 Agents 数量

### 5. 测试消息

#### 通过 Web UI 测试

1. 访问 http://localhost:8700/studio
2. 选择 "general" 频道
3. 发送测试消息：
   - 简单测试：`你好`
   - 深度分析：`最近工作压力很大，感觉很焦虑`

#### 通过命令行测试（高级）

```bash
# 使用 curl 发送消息
curl -X POST http://localhost:8700/api/channels/general/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "你好", "sender_id": "test_user"}'
```

### 6. 验证数据库

```bash
# 查看数据库文件
ls -lh data/

# 应该看到：
# - symphony_mvp.db (Simple Storage)
# - memory_palace.db (Memory Palace)

# 查看数据库内容（可选）
python3 view_database.py
```

---

## 🔍 故障排查

### 问题 1: API 密钥未设置

**错误信息**：

```
❌ GROQ_API_KEY 未设置
```

**解决方案**：

```bash
# 检查环境变量
echo $GROQ_API_KEY

# 如果为空，设置环境变量
export GROQ_API_KEY="gsk_your_api_key"

# 或检查 .env 文件
cat .env
```

### 问题 2: 端口被占用

**错误信息**：

```
ERROR: Failed to bind to port 8700: address already in use
```

**解决方案**：

```bash
# 查找占用端口的进程
lsof -i :8700

# 杀死进程
kill -9 <PID>

# 或使用启动脚本（会自动清理）
./restart_integrated.sh
```

### 问题 3: Agent 无法连接

**错误信息**：

```
Failed to connect to server
Agent registration failed
```

**解决方案**：

```bash
# 1. 确保网络服务正在运行
ps aux | grep "openagents network"

# 2. 检查网络端口
lsof -i :8700
lsof -i :8600

# 3. 重启网络
pkill -9 -f openagents
./restart_integrated.sh
```

### 问题 4: API 速率限制

**错误信息**：

```
HTTP 429 Too Many Requests
```

**解决方案**：

```bash
# 1. 等待一段时间（Groq 有速率限制）
# 2. 检查 API 使用情况
# 3. 考虑升级 Groq 计划
# 4. 优化请求频率（已在代码中实现）
```

### 问题 5: Python 版本不兼容

**错误信息**：

```
SyntaxError: invalid syntax
```

**解决方案**：

```bash
# 检查 Python 版本
python3 --version

# 如果低于 3.11，升级 Python
# macOS
brew install python@3.11

# Linux
sudo apt install python3.11
```

### 问题 6: 依赖包缺失

**错误信息**：

```
ModuleNotFoundError: No module named 'openagents'
```

**解决方案**：

```bash
# 安装依赖
pip install openagents

# 或重新安装所有依赖
pip install -r requirements.txt

# 验证安装
python3 -c "import openagents; print(openagents.__version__)"
```

### 问题 7: 日志文件权限

**错误信息**：

```
Permission denied: logs/
```

**解决方案**：

```bash
# 创建日志目录
mkdir -p logs

# 设置权限
chmod 755 logs

# 清理旧日志（可选）
rm -f logs/*.log
```

---

## 📊 性能监控

### 查看系统资源

```bash
# CPU 和内存使用
top -p $(pgrep -f openagents)

# 或使用 htop（更友好）
htop -p $(pgrep -f openagents)
```

### 查看 API 使用情况

```bash
# 统计 API 调用次数
grep "HTTP Request" logs/*.log | wc -l

# 查看最近的 API 调用
grep "HTTP Request" logs/*.log | tail -20
```

### 查看数据库大小

```bash
# 查看数据库文件大小
du -h data/*.db

# 查看记录数量
python3 view_database.py
```

---

## 🛑 停止项目

### 优雅停止

```bash
# 使用 Ctrl+C 停止（如果在前台运行）

# 或查找并停止进程
pkill -f openagents
pkill -f "python.*agent"
pkill -f "python.*collaborator"
```

### 清理资源

```bash
# 清理日志
rm -f logs/*.log

# 清理数据库（谨慎！会删除所有数据）
rm -f data/*.db

# 清理临时文件
rm -rf __pycache__
rm -rf .pytest_cache
```

---

## 📚 快速参考

### 常用命令

```bash
# 启动（集成模式）
./restart_integrated.sh

# 启动（多 Agent 模式）
./restart_multi_agent.sh

# 查看日志
tail -f logs/daily_assistant.log

# 检查进程
ps aux | grep openagents | grep -v grep

# 停止所有
pkill -9 -f openagents

# 访问 Web UI
open http://localhost:8700
```

### 目录结构

```
network/
├── agents/                    # Agent 实现
│   ├── coordinator_collaborator.py
│   ├── analyst_collaborator.py
│   └── creator_collaborator.py
├── configs/                   # 配置文件
│   ├── daily_assistant_integrated.yaml
│   └── daily_assistant.yaml
├── storage/                   # 存储层
│   ├── simple_storage.py
│   ├── memory_palace.py
│   └── framework_library.py
├── logs/                      # 日志文件
├── data/                      # 数据库文件
├── .env                       # 环境变量（需创建）
├── network.yaml              # 网络配置
└── restart_*.sh              # 启动脚本
```

---

## 🔐 安全最佳实践

### 1. API 密钥管理

- ✅ 使用 `.env` 文件存储密钥
- ✅ 将 `.env` 添加到 `.gitignore`
- ✅ 定期轮换 API 密钥
- ❌ 不要在代码中硬编码密钥
- ❌ 不要将密钥提交到 Git
- ❌ 不要在日志中打印密钥

### 2. 网络安全

- ✅ 仅在本地运行（localhost）
- ✅ 使用防火墙限制端口访问
- ❌ 不要暴露到公网（除非配置了认证）

### 3. 数据安全

- ✅ 定期备份数据库
- ✅ 加密敏感数据
- ✅ 限制数据库文件权限

```bash
# 设置数据库文件权限
chmod 600 data/*.db
```

---

## 📞 获取帮助

### 文档

- [OpenAgents 官方文档](https://openagents.org/docs/)
- [Groq API 文档](https://console.groq.com/docs/)
- 项目 README.md
- 架构文档：ARCHITECTURE.md

### 社区

- OpenAgents GitHub Issues
- OpenAgents Discord 社区

### 日志调试

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG

# 查看详细日志
tail -f logs/*.log
```

---

## ✅ 检查清单

部署前确认：

- [ ] Python 3.11+ 已安装
- [ ] OpenAgents 已安装
- [ ] Groq API 密钥已获取
- [ ] .env 文件已创建并配置
- [ ] .gitignore 已配置
- [ ] 端口 8700 和 8600 可用
- [ ] 网络连接正常

启动后确认：

- [ ] 网络服务正在运行
- [ ] Agent 已成功连接
- [ ] Web UI 可以访问
- [ ] 测试消息有响应
- [ ] 日志无错误信息

---

**祝你部署顺利！🎉**
