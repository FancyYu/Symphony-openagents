"""
基础数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class UserMessage:
    """用户消息"""
    user_id: str
    content: str
    timestamp: str
    message_type: str = "direct_message"
    metadata: Dict = field(default_factory=dict)

@dataclass
class AnalysisResult:
    """分析结果"""
    user_id: str
    framework: str
    insights: List[str]
    timestamp: str
    confidence: float = 0.8

@dataclass  
class ActionPlan:
    """行动计划"""
    user_id: str
    title: str
    steps: List[Dict]
    created_at: str
    due_date: Optional[str] = None