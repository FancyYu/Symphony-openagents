#!/usr/bin/env python3
"""
Analyst Collaborator - 分析师协作 Agent
使用 CollaboratorAgent 实现，可以正常使用 messaging mod
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

from openagents.agents.collaborator_agent import CollaboratorAgent
from openagents.models.agent_config import AgentConfig
from storage.memory_palace import memory_palace
from storage.framework_library import framework_library
from storage.simple_storage import storage


class AnalystCollaborator(CollaboratorAgent):
    """分析师协作 Agent - 接收分析请求，返回洞察"""
    
    def __init__(self):
        config = AgentConfig(
            instruction="""You are an Analyst Agent in the Symphony personal growth system.

Your role:
- Receive analysis requests from other agents
- Analyze user messages for patterns, concerns, and growth opportunities
- Generate insights using various frameworks (HUMAN 3.0, MBTI, Big Five, etc.)
- Return structured analysis results

When you receive a message with analysis request:
1. Extract the content and framework
2. Apply the framework to analyze
3. Generate 3-5 key insights
4. Return results in JSON format

Be thorough, empathetic, and evidence-based.""",
            model_name="llama-3.1-8b-instant",
            provider="groq",
            api_key=os.getenv("GROQ_API_KEY"),
            api_base="https://api.groq.com/openai/v1",
            temperature=0.7,
            max_tokens=800
        )
        super().__init__(agent_config=config, agent_id="analyst-agent")
        
        print(f"🔬 分析师协作 Agent '{self.agent_id}' 已创建")
    
    async def on_direct(self, msg):
        """处理直接消息 - 分析请求"""
        print(f"\n📊 收到分析请求 from {msg.sender_id}")
        
        # 解析请求
        try:
            if isinstance(msg.text, str):
                request = json.loads(msg.text)
            else:
                request = msg.text
            
            user_id = request.get("user_id", "unknown")
            content = request.get("content", "")
            framework_name = request.get("framework", "general")
            channel = request.get("channel", "general")
            
            print(f"   用户: {user_id}")
            print(f"   框架: {framework_name}")
            print(f"   内容: {content[:100]}...")
            
            # 执行分析
            insights = await self.perform_analysis(content, framework_name, user_id)
            
            # 保存分析结果
            storage.save_analysis(
                user_id=user_id,
                framework=framework_name,
                insights=insights,
                confidence=0.8
            )
            
            # 保存到记忆殿堂
            keywords = self._extract_keywords(content, framework_name)
            memory_palace.add_long_term_memory(
                user_id=user_id,
                memory_type="analysis",
                content=f"Framework: {framework_name}\nInsights: {json.dumps(insights, ensure_ascii=False)}",
                keywords=keywords,
                importance=0.8,
                metadata={"framework": framework_name}
            )
            
            print(f"   ✅ 分析完成: {len(insights)} 个洞察")
            
            # 返回结果给发送者
            result = {
                "user_id": user_id,
                "framework": framework_name,
                "channel": channel,
                "insights": insights,
                "confidence": 0.8,
                "original_content": content
            }
            
            ws = self.workspace()
            await ws.agent(msg.sender_id).send(json.dumps(result, ensure_ascii=False))
            print(f"   📤 已返回分析结果给 {msg.sender_id}")
            
        except Exception as e:
            print(f"   ❌ 分析失败: {e}")
            import traceback
            traceback.print_exc()
    
    async def perform_analysis(self, content: str, framework_name: str, user_id: str) -> List[str]:
        """执行分析"""
        # 从记忆殿堂获取上下文
        context_data = memory_palace.build_context(user_id, current_topic=content)
        
        # 获取框架信息
        framework = framework_library.get_framework(framework_name)
        if not framework:
            framework = framework_library.get_framework("general")
        
        # 构建分析提示
        prompt = f"""Analyze the following user message using the {framework.name} framework.

Framework Description: {framework.description}

Framework Dimensions:
{chr(10).join(f"- {dim}" for dim in framework.dimensions)}

Analysis Guidelines:
{framework_library.get_analysis_prompt(framework_name)}

User message: {content}

User Context:
- Total interactions: {len(context_data['recent_memories'])}
- Previous frameworks used: {json.loads(context_data['profile'].get('frameworks_used', '[]'))}

Recent relevant memories:
{self._format_memories(context_data['recent_memories'][:3])}

Generate 3-5 key insights. Each insight should be:
- Specific and actionable
- Based on the framework principles
- Focused on personal growth opportunities
- Written in a supportive, empathetic tone

Format as a numbered list in Chinese."""

        # 使用 LLM 生成分析
        response = await self.run_agent(prompt)
        
        # 解析响应为洞察列表
        insights = self._parse_insights(response)
        
        return insights
    
    def _format_memories(self, memories: List[dict]) -> str:
        """格式化记忆"""
        if not memories:
            return "无历史记录"
        
        formatted = []
        for mem in memories:
            content = mem.get('content', '')[:100]
            formatted.append(f"- {content}")
        
        return "\n".join(formatted)
    
    def _extract_keywords(self, content: str, framework: str) -> List[str]:
        """提取关键词"""
        keywords = [framework.lower()]
        
        import re
        words = re.findall(r'\w+', content.lower())
        
        stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        
        for word in words:
            if word not in stopwords and len(word) > 1:
                keywords.append(word)
                if len(keywords) >= 8:
                    break
        
        return keywords
    
    def _parse_insights(self, response: str) -> List[str]:
        """解析 LLM 响应为洞察列表"""
        insights = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                import re
                line = re.sub(r'^\d+[\.\)]\s*', '', line)
                line = re.sub(r'^[-•]\s*', '', line)
                if line and len(line) > 10:
                    insights.append(line)
        
        if not insights:
            insights = [line.strip() for line in lines[:5] if line.strip() and len(line.strip()) > 10]
        
        return insights[:5]


async def main():
    """主函数"""
    print("🚀 启动分析师协作 Agent...")
    
    agent = AnalystCollaborator()
    
    try:
        await agent.async_start(
            network_host="localhost",
            network_port=8700,
            secret="",  # 空 secret 用于无认证网络
        )
        
        print(f"\n✅ 分析师协作 Agent '{agent.agent_id}' 正在运行")
        print("📡 等待分析请求（通过直接消息）")
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
