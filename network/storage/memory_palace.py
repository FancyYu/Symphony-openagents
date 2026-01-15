#!/usr/bin/env python3
"""
Memory Palace - 记忆殿堂
使用 SQLite 实现的轻量级记忆存储系统
支持语义搜索、上下文检索和长期记忆管理
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import hashlib


class MemoryPalace:
    """记忆殿堂 - 轻量级记忆存储系统"""
    
    def __init__(self, db_path="data/memory_palace.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 短期记忆表 (最近的对话和交互)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS short_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT DEFAULT 'message',
                importance REAL DEFAULT 0.5,
                timestamp TEXT NOT NULL,
                expires_at TEXT,
                metadata TEXT DEFAULT '{}'
            )
        ''')
        
        # 长期记忆表 (重要的洞察和模式)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                keywords TEXT NOT NULL,
                importance REAL DEFAULT 0.7,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                created_at TEXT NOT NULL,
                metadata TEXT DEFAULT '{}'
            )
        ''')
        
        # 用户画像表 (用户的持久特征和偏好)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                personality_traits TEXT DEFAULT '{}',
                preferences TEXT DEFAULT '{}',
                goals TEXT DEFAULT '[]',
                frameworks_used TEXT DEFAULT '[]',
                interaction_stats TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # 关联记忆表 (记忆之间的关联)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_associations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id_1 INTEGER NOT NULL,
                memory_id_2 INTEGER NOT NULL,
                association_type TEXT NOT NULL,
                strength REAL DEFAULT 0.5,
                created_at TEXT NOT NULL,
                FOREIGN KEY (memory_id_1) REFERENCES long_term_memory(id),
                FOREIGN KEY (memory_id_2) REFERENCES long_term_memory(id)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stm_user ON short_term_memory(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stm_timestamp ON short_term_memory(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ltm_user ON long_term_memory(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ltm_type ON long_term_memory(memory_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ltm_keywords ON long_term_memory(keywords)')
        
        conn.commit()
        conn.close()
    
    # ==================== 短期记忆管理 ====================
    
    def add_short_term_memory(
        self, 
        user_id: str, 
        content: str, 
        content_type: str = "message",
        importance: float = 0.5,
        ttl_hours: int = 24,
        metadata: Dict = None
    ) -> int:
        """添加短期记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        expires_at = now + timedelta(hours=ttl_hours)
        
        cursor.execute('''
            INSERT INTO short_term_memory 
            (user_id, content, content_type, importance, timestamp, expires_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            content,
            content_type,
            importance,
            now.isoformat(),
            expires_at.isoformat(),
            json.dumps(metadata or {})
        ))
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return memory_id
    
    def get_recent_memories(
        self, 
        user_id: str, 
        limit: int = 10,
        content_type: Optional[str] = None
    ) -> List[Dict]:
        """获取最近的短期记忆"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 清理过期记忆
        self._cleanup_expired_memories(cursor)
        
        query = '''
            SELECT * FROM short_term_memory 
            WHERE user_id = ?
        '''
        params = [user_id]
        
        if content_type:
            query += ' AND content_type = ?'
            params.append(content_type)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def _cleanup_expired_memories(self, cursor):
        """清理过期的短期记忆"""
        now = datetime.now().isoformat()
        cursor.execute('DELETE FROM short_term_memory WHERE expires_at < ?', (now,))
    
    # ==================== 长期记忆管理 ====================
    
    def add_long_term_memory(
        self,
        user_id: str,
        memory_type: str,
        content: str,
        keywords: List[str],
        importance: float = 0.7,
        metadata: Dict = None
    ) -> int:
        """添加长期记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        keywords_str = ','.join(keywords)
        
        cursor.execute('''
            INSERT INTO long_term_memory 
            (user_id, memory_type, content, keywords, importance, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            memory_type,
            content,
            keywords_str,
            importance,
            datetime.now().isoformat(),
            json.dumps(metadata or {})
        ))
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return memory_id
    
    def search_memories(
        self,
        user_id: str,
        keywords: List[str],
        memory_type: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """搜索长期记忆（基于关键词）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 构建搜索条件
        query = '''
            SELECT *, 
                   (importance * access_count * 0.1) as relevance_score
            FROM long_term_memory 
            WHERE user_id = ?
        '''
        params = [user_id]
        
        if memory_type:
            query += ' AND memory_type = ?'
            params.append(memory_type)
        
        # 关键词匹配
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append('keywords LIKE ?')
                params.append(f'%{keyword}%')
            
            query += ' AND (' + ' OR '.join(keyword_conditions) + ')'
        
        query += ' ORDER BY relevance_score DESC, importance DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 更新访问计数
        for row in rows:
            cursor.execute('''
                UPDATE long_term_memory 
                SET access_count = access_count + 1,
                    last_accessed = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), row['id']))
        
        conn.commit()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_important_memories(
        self,
        user_id: str,
        min_importance: float = 0.7,
        limit: int = 10
    ) -> List[Dict]:
        """获取重要的长期记忆"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM long_term_memory 
            WHERE user_id = ? AND importance >= ?
            ORDER BY importance DESC, access_count DESC
            LIMIT ?
        ''', (user_id, min_importance, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== 用户画像管理 ====================
    
    def get_or_create_profile(self, user_id: str) -> Dict:
        """获取或创建用户画像"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            conn.close()
            return dict(row)
        
        # 创建新画像
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO user_profiles 
            (user_id, created_at, updated_at)
            VALUES (?, ?, ?)
        ''', (user_id, now, now))
        
        conn.commit()
        
        cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row)
    
    def update_profile(
        self,
        user_id: str,
        personality_traits: Optional[Dict] = None,
        preferences: Optional[Dict] = None,
        goals: Optional[List[str]] = None,
        frameworks_used: Optional[List[str]] = None,
        interaction_stats: Optional[Dict] = None
    ):
        """更新用户画像"""
        profile = self.get_or_create_profile(user_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if personality_traits is not None:
            updates.append('personality_traits = ?')
            params.append(json.dumps(personality_traits))
        
        if preferences is not None:
            updates.append('preferences = ?')
            params.append(json.dumps(preferences))
        
        if goals is not None:
            updates.append('goals = ?')
            params.append(json.dumps(goals))
        
        if frameworks_used is not None:
            updates.append('frameworks_used = ?')
            params.append(json.dumps(frameworks_used))
        
        if interaction_stats is not None:
            updates.append('interaction_stats = ?')
            params.append(json.dumps(interaction_stats))
        
        updates.append('updated_at = ?')
        params.append(datetime.now().isoformat())
        
        params.append(user_id)
        
        query = f'UPDATE user_profiles SET {", ".join(updates)} WHERE user_id = ?'
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
    
    def add_framework_usage(self, user_id: str, framework: str):
        """记录框架使用"""
        profile = self.get_or_create_profile(user_id)
        frameworks = json.loads(profile.get('frameworks_used', '[]'))
        
        if framework not in frameworks:
            frameworks.append(framework)
            self.update_profile(user_id, frameworks_used=frameworks)
    
    # ==================== 记忆关联 ====================
    
    def create_association(
        self,
        memory_id_1: int,
        memory_id_2: int,
        association_type: str,
        strength: float = 0.5
    ):
        """创建记忆关联"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memory_associations 
            (memory_id_1, memory_id_2, association_type, strength, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            memory_id_1,
            memory_id_2,
            association_type,
            strength,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_associated_memories(
        self,
        memory_id: int,
        min_strength: float = 0.3
    ) -> List[Dict]:
        """获取关联的记忆"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ltm.*, ma.association_type, ma.strength
            FROM memory_associations ma
            JOIN long_term_memory ltm ON (
                CASE 
                    WHEN ma.memory_id_1 = ? THEN ltm.id = ma.memory_id_2
                    WHEN ma.memory_id_2 = ? THEN ltm.id = ma.memory_id_1
                END
            )
            WHERE (ma.memory_id_1 = ? OR ma.memory_id_2 = ?)
            AND ma.strength >= ?
            ORDER BY ma.strength DESC
        ''', (memory_id, memory_id, memory_id, memory_id, min_strength))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== 上下文构建 ====================
    
    def build_context(
        self,
        user_id: str,
        current_topic: Optional[str] = None,
        max_short_term: int = 5,
        max_long_term: int = 3
    ) -> Dict:
        """构建对话上下文"""
        context = {
            "user_id": user_id,
            "profile": self.get_or_create_profile(user_id),
            "recent_memories": self.get_recent_memories(user_id, limit=max_short_term),
            "relevant_long_term": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 如果有当前话题，搜索相关长期记忆
        if current_topic:
            keywords = self._extract_keywords(current_topic)
            context["relevant_long_term"] = self.search_memories(
                user_id, 
                keywords, 
                limit=max_long_term
            )
        else:
            # 否则获取最重要的记忆
            context["relevant_long_term"] = self.get_important_memories(
                user_id,
                limit=max_long_term
            )
        
        return context
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简化版）"""
        # 移除常见停用词
        stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        
        # 简单分词（按空格和标点）
        import re
        words = re.findall(r'\w+', text.lower())
        
        # 过滤停用词和短词
        keywords = [w for w in words if w not in stopwords and len(w) > 1]
        
        # 返回前5个关键词
        return keywords[:5]
    
    # ==================== 统计和维护 ====================
    
    def get_memory_stats(self, user_id: str) -> Dict:
        """获取记忆统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 短期记忆数量
        cursor.execute(
            'SELECT COUNT(*) FROM short_term_memory WHERE user_id = ?',
            (user_id,)
        )
        stats['short_term_count'] = cursor.fetchone()[0]
        
        # 长期记忆数量
        cursor.execute(
            'SELECT COUNT(*) FROM long_term_memory WHERE user_id = ?',
            (user_id,)
        )
        stats['long_term_count'] = cursor.fetchone()[0]
        
        # 按类型统计长期记忆
        cursor.execute('''
            SELECT memory_type, COUNT(*) as count
            FROM long_term_memory 
            WHERE user_id = ?
            GROUP BY memory_type
        ''', (user_id,))
        stats['memory_by_type'] = dict(cursor.fetchall())
        
        conn.close()
        
        return stats


# 全局实例
memory_palace = MemoryPalace()
