#!/usr/bin/env python3
"""
Coordinator Collaborator - 协调者协作 Agent
负责接收用户消息，协调分析师和创作者，返回结果
"""

import asyncio
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from openagents.agents.collaborator_agent import CollaboratorAgent
from openagents.models.agent_config import AgentConfig
from storage.simple_storage import storage


class CoordinatorCollaborator(CollaboratorAgent):
    """协调者协作 Agent - 协调整个分析流程"""
    
    def __init__(self):
        config = AgentConfig(
            instruction="""你是 Symphony 系统的协调者。

你的职责：
1. 接收用户消息
2. 判断是否需要深度分析
3. 协调分析师和创作者
4. 将结果返回给用户

保持简洁、友好、支持性。始终用中文回复。""",
            model_name="llama-3.1-8b-instant",
            provider="groq",
            api_key=os.getenv("GROQ_API_KEY"),
            api_base="https://api.groq.com/openai/v1",
            temperature=0.7,
            max_tokens=150
        )
        super().__init__(agent_config=config, agent_id="coordinator-agent")
        
        # 跟踪等待的响应
        self.pending_analysis = {}  # user_id -> {channel, content}
        self.pending_plans = {}     # user_id -> {channel, insights}
        
        print(f"🎯 协调者协作 Agent '{self.agent_id}' 已创建")
    
    async def on_channel_post(self, msg):
        """处理频道消息"""
        sender = msg.sender_id
        content = msg.text
        channel = msg.channel
        
        # 跳过自己的消息
        if sender == self.agent_id:
            return
        
        print(f"\n📨 收到消息 from {sender}")
        print(f"   频道: {channel}")
        print(f"   内容: {content[:100]}...")
        
        # 保存消息
        storage.save_message(
            user_id=sender,
            content=content,
            message_type="channel_message",
            metadata={"channel": channel}
        )
        
        # 检查是否需要分析
        if self._needs_analysis(content):
            print(f"   🎯 检测到需要分析")
            await self.handle_analysis_request(sender, content, channel)
        else:
            # 普通对话
            print(f"   💬 普通对话")
            response = await self.run_agent(f"用户说：{content}\n\n请给出简短、友好的回复（1-2句话）")
            
            ws = self.workspace()
            await ws.channel(channel).post(response)
    
    async def on_direct(self, msg):
        """处理直接消息 - 来自分析师或创作者的响应"""
        sender = msg.sender_id
        
        print(f"\n📥 收到直接消息 from {sender}")
        
        try:
            if isinstance(msg.text, str):
                data = json.loads(msg.text)
            else:
                data = msg.text
            
            user_id = data.get("user_id")
            
            # 来自分析师的响应
            if sender == "analyst-agent":
                await self.handle_analysis_response(data)
            
            # 来自创作者的响应
            elif sender == "creator-agent":
                await self.handle_plan_response(data)
                
        except Exception as e:
            print(f"   ❌ 处理响应失败: {e}")
            import traceback
            traceback.print_exc()
    
    async def handle_analysis_request(self, user_id: str, content: str, channel: str):
        """处理分析请求"""
        ws = self.workspace()
        
        try:
            # 告知用户
            await ws.channel(channel).post("我理解你的感受。让我为你进行深入分析，找出解决方案... 🔍")
            
            # 检测框架
            framework = self._detect_framework(content)
            
            # 发送请求给分析师
            request = {
                "user_id": user_id,
                "content": content,
                "framework": framework,
                "channel": channel
            }
            
            # 记录等待的分析
            self.pending_analysis[user_id] = {
                "channel": channel,
                "content": content
            }
            
            print(f"   📤 发送分析请求给 analyst-agent")
            await ws.agent("analyst-agent").send(json.dumps(request, ensure_ascii=False))
            
        except Exception as e:
            print(f"   ❌ 发送分析请求失败: {e}")
            await ws.channel(channel).post("抱歉，分析过程中遇到了问题。请稍后再试。")
    
    async def handle_analysis_response(self, data: dict):
        """处理分析师的响应"""
        user_id = data.get("user_id")
        insights = data.get("insights", [])
        channel = data.get("channel", "general")
        
        print(f"   ✅ 收到分析结果: {len(insights)} 个洞察")
        
        # 发送给创作者
        ws = self.workspace()
        
        # 记录等待的计划
        self.pending_plans[user_id] = {
            "channel": channel,
            "insights": insights
        }
        
        print(f"   📤 发送给 creator-agent 生成行动计划")
        await ws.agent("creator-agent").send(json.dumps(data, ensure_ascii=False))
    
    async def handle_plan_response(self, data: dict):
        """处理创作者的响应"""
        user_id = data.get("user_id")
        channel = data.get("channel", "general")
        action_plan = data.get("action_plan", {})
        insights = data.get("insights", [])
        
        print(f"   ✅ 收到行动计划: {action_plan.get('title')}")
        
        # 格式化完整响应
        response = self._format_complete_response(insights, action_plan)
        
        # 发送给用户
        ws = self.workspace()
        await ws.channel(channel).post(response)
        
        print(f"   📤 完整结果已发送到频道: {channel}")
        
        # 清理等待记录
        self.pending_analysis.pop(user_id, None)
        self.pending_plans.pop(user_id, None)
    
    def _needs_analysis(self, content: str) -> bool:
        """判断是否需要分析"""
        analysis_keywords = [
            "分析", "analyze", "压力", "stress", "焦虑", "anxiety",
            "困惑", "confused", "问题", "problem", "困难", "difficulty",
            "建议", "advice", "帮助", "help", "怎么", "如何", "为什么",
            "原因", "reason", "解决", "solution", "改进", "improve",
            "career", "职业", "工作", "work", "关系", "relationship",
            "成长", "growth", "发展", "development", "mbti", "性格"
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in analysis_keywords)
    
    def _detect_framework(self, content: str) -> str:
        """检测应该使用的分析框架"""
        content_lower = content.lower()
        
        if "mbti" in content_lower or "personality" in content_lower or "性格" in content_lower:
            return "MBTI"
        elif "big five" in content_lower or "五大人格" in content_lower:
            return "Big Five"
        elif "human" in content_lower or "potential" in content_lower or "潜能" in content_lower:
            return "HUMAN 3.0"
        else:
            return "general"
    
    def _format_complete_response(self, insights: list, action_plan: dict) -> str:
        """格式化完整的响应"""
        response = "📊 **分析完成**\n\n"
        
        # 添加洞察
        response += "💡 **关键洞察：**\n"
        for i, insight in enumerate(insights[:3], 1):
            response += f"{i}. {insight}\n"
        
        response += "\n"
        
        # 添加行动计划
        response += f"🎯 **{action_plan['title']}**\n\n"
        
        if action_plan.get('overview'):
            response += f"📝 {action_plan['overview']}\n\n"
        
        response += "📋 **行动步骤：**\n"
        for i, step in enumerate(action_plan.get('steps', [])[:5], 1):
            action = step.get('action', '')
            timeline = step.get('timeline', '')
            
            response += f"\n{i}. {action}"
            if timeline:
                response += f" ({timeline})"
        
        response += "\n\n🌟 开始行动吧！如果需要调整或有任何问题，随时告诉我。"
        
        return response


async def main():
    """主函数"""
    print("🚀 启动协调者协作 Agent...")
    
    agent = CoordinatorCollaborator()
    
    try:
        await agent.async_start(
            network_host="localhost",
            network_port=8700,
            secret="",  # 空 secret 用于无认证网络
        )
        
        print(f"\n✅ 协调者协作 Agent '{agent.agent_id}' 正在运行")
        print("📡 监听频道消息，协调分析流程")
        print("⏹️  按 Ctrl+C 停止\n")
        
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 停止中...")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.async_stop()


if __name__ == "__main__":
    asyncio.run(main())
