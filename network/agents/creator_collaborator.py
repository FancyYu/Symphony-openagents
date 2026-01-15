#!/usr/bin/env python3
"""
Creator Collaborator - 创作者协作 Agent
使用 CollaboratorAgent 实现，可以正常使用 messaging mod
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from openagents.agents.collaborator_agent import CollaboratorAgent
from openagents.models.agent_config import AgentConfig
from storage.simple_storage import storage


class CreatorCollaborator(CollaboratorAgent):
    """创作者协作 Agent - 接收分析结果，生成行动计划"""
    
    def __init__(self):
        config = AgentConfig(
            instruction="""You are a Creator Agent in the Symphony personal growth system.

Your role:
- Receive analysis results from analyst agent
- Transform insights into actionable plans
- Create structured action plans with clear steps
- Return formatted plans

When you receive analysis results:
1. Extract insights and context
2. Create a motivating title
3. Generate 3-7 actionable steps with timelines
4. Format as structured JSON

Be practical, encouraging, and specific.""",
            model_name="llama-3.1-8b-instant",
            provider="groq",
            api_key=os.getenv("GROQ_API_KEY"),
            api_base="https://api.groq.com/openai/v1",
            temperature=0.7,
            max_tokens=600
        )
        super().__init__(agent_config=config, agent_id="creator-agent")
        
        print(f"🎨 创作者协作 Agent '{self.agent_id}' 已创建")
    
    async def on_direct(self, msg):
        """处理直接消息 - 分析结果"""
        print(f"\n📋 收到分析结果 from {msg.sender_id}")
        
        try:
            # 解析分析结果
            if isinstance(msg.text, str):
                analysis = json.loads(msg.text)
            else:
                analysis = msg.text
            
            user_id = analysis.get("user_id", "unknown")
            framework = analysis.get("framework", "general")
            insights = analysis.get("insights", [])
            original_content = analysis.get("original_content", "")
            channel = analysis.get("channel", "general")
            
            print(f"   用户: {user_id}")
            print(f"   框架: {framework}")
            print(f"   洞察数量: {len(insights)}")
            
            # 生成行动计划
            action_plan = await self.create_action_plan(
                user_id=user_id,
                framework=framework,
                insights=insights,
                context=original_content
            )
            
            # 保存行动计划
            storage.save_action_plan(
                user_id=user_id,
                title=action_plan["title"],
                steps=action_plan["steps"],
                overview=action_plan.get("overview", "")
            )
            
            print(f"   ✅ 行动计划已生成: {action_plan['title']}")
            
            # 返回结果给发送者
            result = {
                "user_id": user_id,
                "channel": channel,
                "action_plan": action_plan,
                "insights": insights
            }
            
            ws = self.workspace()
            await ws.agent(msg.sender_id).send(json.dumps(result, ensure_ascii=False))
            print(f"   📤 已返回行动计划给 {msg.sender_id}")
            
        except Exception as e:
            print(f"   ❌ 创建行动计划失败: {e}")
            import traceback
            traceback.print_exc()
    
    async def create_action_plan(self, user_id: str, framework: str, 
                                 insights: List[str], context: str) -> Dict:
        """创建行动计划"""
        insights_text = "\n".join([f"{i+1}. {insight}" for i, insight in enumerate(insights)])
        
        prompt = f"""Based on the following analysis insights, create a practical action plan.

Framework: {framework}

Key Insights:
{insights_text}

Original context: {context}

Create an action plan with:
1. Title: A motivating, clear title (max 50 characters)
2. Overview: Brief summary (2-3 sentences)
3. Steps: 3-7 actionable steps, each with:
   - What to do (specific action)
   - Timeline (e.g., "Week 1", "Daily", "This month")
   - Expected benefit

Format as JSON:
{{
  "title": "...",
  "overview": "...",
  "steps": [
    {{"action": "...", "timeline": "...", "benefit": "..."}},
    ...
  ]
}}"""

        # 使用 LLM 生成行动计划
        response = await self.run_agent(prompt)
        
        # 解析响应
        action_plan = self._parse_action_plan(response)
        
        return action_plan
    
    def _parse_action_plan(self, response: str) -> Dict:
        """解析 LLM 响应为行动计划"""
        import re
        
        # 尝试提取 JSON
        json_match = re.search(r'\{[^{}]*"title"[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        # 如果 JSON 解析失败，手动解析
        lines = response.split('\n')
        title = "个人成长行动计划"
        overview = ""
        steps = []
        
        for line in lines:
            line = line.strip()
            if 'title' in line.lower() or '标题' in line:
                title = re.sub(r'.*[:：]\s*', '', line, count=1)
            elif 'overview' in line.lower() or '概述' in line:
                overview = line
            elif re.match(r'^\d+[\.\)]', line) or line.startswith('-'):
                action_match = re.match(r'^\d+[\.\)]\s*(.+)', line)
                if action_match:
                    steps.append({
                        "action": action_match.group(1),
                        "timeline": "本周",
                        "benefit": "个人成长"
                    })
        
        if not steps:
            steps = [
                {"action": "开始实施第一个洞察", "timeline": "本周", "benefit": "建立基础"},
                {"action": "持续跟踪进展", "timeline": "每日", "benefit": "保持动力"},
                {"action": "定期回顾和调整", "timeline": "每月", "benefit": "持续改进"}
            ]
        
        return {
            "title": title[:50] if title else "个人成长行动计划",
            "overview": overview or "基于分析洞察制定的个性化行动计划",
            "steps": steps[:7]
        }


async def main():
    """主函数"""
    print("🚀 启动创作者协作 Agent...")
    
    agent = CreatorCollaborator()
    
    try:
        await agent.async_start(
            network_host="localhost",
            network_port=8700,
            secret="",  # 空 secret 用于无认证网络
        )
        
        print(f"\n✅ 创作者协作 Agent '{agent.agent_id}' 正在运行")
        print("📡 等待分析结果（通过直接消息）")
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
