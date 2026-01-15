"""
简化事件总线 - 支持多进程通信
"""

import asyncio
from typing import Dict, List, Callable
import json

class SimpleEventBus:
    """简化事件总线 - 单进程版本"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_queue = None  # 延迟创建
        self._processor_task = None
        self._started = False
    
    async def publish(self, event_type: str, source: str, payload: dict):
        """发布事件"""
        # 确保事件队列和处理器已启动
        if self._event_queue is None:
            try:
                loop = asyncio.get_running_loop()
                self._event_queue = asyncio.Queue()
                if self._processor_task is None:
                    self._processor_task = loop.create_task(self._process_events())
                    self._started = True
            except RuntimeError:
                # 如果没有运行的事件循环，创建一个新的队列（但处理器无法启动）
                # 这种情况下事件会丢失，但至少不会崩溃
                self._event_queue = asyncio.Queue()
                print(f"⚠️  警告: 没有运行的事件循环，事件可能无法处理")
                return
        
        # 获取时间戳
        try:
            timestamp = asyncio.get_event_loop().time()
        except RuntimeError:
            import time
            timestamp = time.time()
        
        event = {
            "type": event_type,
            "source": source,
            "payload": payload,
            "timestamp": timestamp
        }
        
        await self._event_queue.put(event)
        print(f"📤 发布事件: {event_type} from {source}")
    
    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        print(f"👂 订阅事件: {event_type}")
    
    async def _process_events(self):
        """处理事件队列"""
        if self._event_queue is None:
            return
        
        while True:
            try:
                event = await self._event_queue.get()
                event_type = event["type"]
                
                # 通知订阅者
                if event_type in self._subscribers:
                    for callback in self._subscribers[event_type]:
                        try:
                            await callback(event)
                        except Exception as e:
                            print(f"⚠️  事件处理错误: {e}")
                
                self._event_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️  事件处理循环错误: {e}")
                await asyncio.sleep(0.1)  # 避免快速循环

# 全局实例
event_bus = SimpleEventBus()