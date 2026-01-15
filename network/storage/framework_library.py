#!/usr/bin/env python3
"""
Framework Library - 乐谱库
存储各种人生分析框架的知识库
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class AnalysisFramework:
    """分析框架"""
    name: str
    description: str
    dimensions: List[str]
    analysis_prompts: Dict[str, str]
    interpretation_guide: str
    keywords: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


class FrameworkLibrary:
    """框架知识库"""
    
    def __init__(self):
        self.frameworks: Dict[str, AnalysisFramework] = {}
        self._load_default_frameworks()
    
    def _load_default_frameworks(self):
        """加载默认框架"""
        
        # HUMAN 3.0 框架
        self.frameworks["HUMAN 3.0"] = AnalysisFramework(
            name="HUMAN 3.0",
            description="人类潜能和成长思维框架，关注个人的成长潜力、学习能力和自我实现",
            dimensions=[
                "成长思维 (Growth Mindset)",
                "学习能力 (Learning Capacity)",
                "适应性 (Adaptability)",
                "创造力 (Creativity)",
                "自我认知 (Self-Awareness)",
                "目标导向 (Goal Orientation)"
            ],
            analysis_prompts={
                "growth_mindset": "分析用户的成长思维模式，识别固定思维和成长思维的表现",
                "learning": "评估用户的学习方式、学习动机和学习障碍",
                "adaptability": "分析用户面对变化和挑战时的适应能力",
                "creativity": "识别用户的创造性思维和创新潜力",
                "self_awareness": "评估用户对自己的认知深度和准确性",
                "goals": "分析用户的目标设定、追求和实现能力"
            },
            interpretation_guide="""
HUMAN 3.0 框架解读指南：
1. 成长思维：关注用户是否相信能力可以通过努力提升
2. 学习能力：评估用户的学习策略和元认知能力
3. 适应性：观察用户如何应对不确定性和变化
4. 创造力：识别用户的创新思维和问题解决方式
5. 自我认知：评估用户对自己优势和局限的理解
6. 目标导向：分析用户的目标清晰度和执行力
            """,
            keywords=["成长", "潜能", "学习", "发展", "自我实现", "growth", "potential"],
            examples=[
                "我想提升自己的学习能力",
                "如何发掘自己的潜能？",
                "我想要持续成长"
            ]
        )
        
        # MBTI 框架
        self.frameworks["MBTI"] = AnalysisFramework(
            name="MBTI",
            description="迈尔斯-布里格斯性格类型指标，通过四个维度分析性格类型",
            dimensions=[
                "外向(E) vs 内向(I)",
                "感觉(S) vs 直觉(N)",
                "思考(T) vs 情感(F)",
                "判断(J) vs 知觉(P)"
            ],
            analysis_prompts={
                "energy": "分析用户的能量来源：从外部互动(E)还是内部反思(I)获得能量",
                "information": "评估用户如何收集信息：关注具体细节(S)还是整体模式(N)",
                "decisions": "分析用户的决策方式：基于逻辑(T)还是价值观(F)",
                "lifestyle": "评估用户的生活方式：有计划(J)还是灵活随性(P)"
            },
            interpretation_guide="""
MBTI 框架解读指南：
1. E/I维度：能量方向 - 外向型从社交获得能量，内向型从独处获得能量
2. S/N维度：信息处理 - 感觉型关注现实细节，直觉型关注可能性和模式
3. T/F维度：决策方式 - 思考型重视逻辑，情感型重视价值和影响
4. J/P维度：生活方式 - 判断型喜欢计划，知觉型喜欢灵活

16种性格类型组合，每种都有独特的优势和发展方向。
            """,
            keywords=["性格", "mbti", "personality", "类型", "内向", "外向"],
            examples=[
                "我想了解自己的性格类型",
                "我是内向还是外向？",
                "帮我分析MBTI性格"
            ]
        )
        
        # Big Five 框架
        self.frameworks["Big Five"] = AnalysisFramework(
            name="Big Five",
            description="五大人格特质模型，通过五个维度评估人格特征",
            dimensions=[
                "开放性 (Openness)",
                "尽责性 (Conscientiousness)",
                "外向性 (Extraversion)",
                "宜人性 (Agreeableness)",
                "神经质 (Neuroticism)"
            ],
            analysis_prompts={
                "openness": "评估用户的开放性：对新体验、想法和艺术的接受程度",
                "conscientiousness": "分析用户的尽责性：组织性、可靠性和目标导向",
                "extraversion": "评估用户的外向性：社交性、活力和积极情绪",
                "agreeableness": "分析用户的宜人性：合作性、信任和同理心",
                "neuroticism": "评估用户的情绪稳定性：焦虑、情绪波动和压力应对"
            },
            interpretation_guide="""
Big Five 框架解读指南：
1. 开放性 (O)：高分表示好奇、有创造力；低分表示务实、传统
2. 尽责性 (C)：高分表示有组织、可靠；低分表示灵活、自发
3. 外向性 (E)：高分表示社交、活跃；低分表示内敛、独立
4. 宜人性 (A)：高分表示合作、信任；低分表示竞争、怀疑
5. 神经质 (N)：高分表示情绪敏感；低分表示情绪稳定

每个维度都是连续的，没有绝对的好坏。
            """,
            keywords=["五大人格", "big five", "开放性", "尽责性", "外向性"],
            examples=[
                "用Big Five分析我的性格",
                "我的五大人格特质是什么？",
                "帮我做五大人格测评"
            ]
        )
        
        # 通用成长框架
        self.frameworks["general"] = AnalysisFramework(
            name="General Growth",
            description="通用个人成长分析框架，适用于各种成长话题",
            dimensions=[
                "当前状态 (Current State)",
                "挑战与障碍 (Challenges)",
                "优势与资源 (Strengths)",
                "成长机会 (Opportunities)",
                "行动方向 (Action Direction)"
            ],
            analysis_prompts={
                "current": "分析用户当前的状态、感受和处境",
                "challenges": "识别用户面临的主要挑战和障碍",
                "strengths": "发现用户的优势、资源和已有能力",
                "opportunities": "识别成长机会和可能的突破点",
                "actions": "提出具体的行动建议和发展方向"
            },
            interpretation_guide="""
通用成长框架解读指南：
1. 全面评估：从多个角度理解用户的情况
2. 平衡视角：既看到挑战也看到机会
3. 实用导向：提供可操作的建议
4. 个性化：根据用户具体情况调整分析
5. 成长导向：始终关注如何帮助用户成长
            """,
            keywords=["成长", "发展", "提升", "改进", "进步"],
            examples=[
                "帮我分析一下我的情况",
                "我该如何成长？",
                "给我一些建议"
            ]
        )
        
        # 职业发展框架
        self.frameworks["Career Development"] = AnalysisFramework(
            name="Career Development",
            description="职业发展分析框架，关注职业规划和发展",
            dimensions=[
                "职业兴趣 (Career Interests)",
                "技能评估 (Skills Assessment)",
                "价值观匹配 (Values Alignment)",
                "发展路径 (Development Path)",
                "工作生活平衡 (Work-Life Balance)"
            ],
            analysis_prompts={
                "interests": "分析用户的职业兴趣和热情所在",
                "skills": "评估用户的核心技能和待发展领域",
                "values": "识别用户的职业价值观和工作动机",
                "path": "规划用户的职业发展路径和里程碑",
                "balance": "评估用户的工作生活平衡状态"
            },
            interpretation_guide="""
职业发展框架解读指南：
1. 兴趣驱动：找到真正感兴趣的领域
2. 技能匹配：评估现有技能与目标的差距
3. 价值观：确保职业选择符合个人价值观
4. 路径规划：制定清晰的发展步骤
5. 平衡：关注可持续的职业发展
            """,
            keywords=["职业", "工作", "career", "发展", "规划"],
            examples=[
                "我对职业发展感到困惑",
                "如何规划我的职业？",
                "工作压力很大"
            ]
        )
    
    def get_framework(self, name: str) -> Optional[AnalysisFramework]:
        """获取框架"""
        return self.frameworks.get(name)
    
    def list_frameworks(self) -> List[str]:
        """列出所有框架"""
        return list(self.frameworks.keys())
    
    def search_framework(self, query: str) -> Optional[str]:
        """根据查询搜索合适的框架"""
        query_lower = query.lower()
        
        # 检查每个框架的关键词
        for name, framework in self.frameworks.items():
            if any(keyword in query_lower for keyword in framework.keywords):
                return name
        
        # 默认返回通用框架
        return "general"
    
    def get_analysis_prompt(self, framework_name: str, dimension: Optional[str] = None) -> str:
        """获取分析提示"""
        framework = self.get_framework(framework_name)
        if not framework:
            return ""
        
        if dimension and dimension in framework.analysis_prompts:
            return framework.analysis_prompts[dimension]
        
        # 返回所有维度的提示
        prompts = []
        for dim, prompt in framework.analysis_prompts.items():
            prompts.append(f"{dim}: {prompt}")
        
        return "\n".join(prompts)
    
    def get_framework_guide(self, framework_name: str) -> str:
        """获取框架解读指南"""
        framework = self.get_framework(framework_name)
        if not framework:
            return ""
        
        return f"""
框架: {framework.name}
描述: {framework.description}

维度:
{chr(10).join(f"- {dim}" for dim in framework.dimensions)}

{framework.interpretation_guide}
        """


# 全局实例
framework_library = FrameworkLibrary()
