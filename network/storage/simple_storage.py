"""
简化存储 - 使用SQLite
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class SimpleStorage:
    """简化存储"""
    
    def __init__(self, db_path="data/symphony_mvp.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户消息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'direct_message',
                metadata TEXT DEFAULT '{}',
                timestamp TEXT NOT NULL
            )
        ''')
        
        # 分析结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                framework TEXT NOT NULL,
                insights TEXT NOT NULL,
                confidence REAL DEFAULT 0.8,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # 行动计划表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                steps TEXT NOT NULL,
                created_at TEXT NOT NULL,
                due_date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_message(self, user_id: str, content: str, message_type="direct_message", metadata=None):
        """保存用户消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_messages 
            (user_id, content, message_type, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id, 
            content, 
            message_type,
            json.dumps(metadata or {}),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def get_user_messages(self, user_id: str, limit=50) -> List[Dict]:
        """获取用户消息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_messages 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def save_analysis(self, user_id: str, framework: str, insights: List[str], confidence=0.8):
        """保存分析结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_results 
            (user_id, framework, insights, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            framework,
            json.dumps(insights),
            confidence,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def save_action_plan(self, user_id: str, title: str, steps: List[Dict], overview: str = ""):
        """保存行动计划"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        plan_data = {
            "overview": overview,
            "steps": steps
        }
        
        cursor.execute('''
            INSERT INTO action_plans 
            (user_id, title, steps, created_at)
            VALUES (?, ?, ?, ?)
        ''', (
            user_id,
            title,
            json.dumps(plan_data),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def get_action_plans(self, user_id: str, limit=10) -> List[Dict]:
        """获取用户的行动计划"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM action_plans 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

# 全局存储实例
storage = SimpleStorage()