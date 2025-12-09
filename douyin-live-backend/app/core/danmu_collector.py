"""
抖音直播弹幕采集器

支持多种采集方式:
1. WebSocket直连 (需要解析抖音协议)
2. 第三方API接入
3. 模拟器采集
"""
import asyncio
import json
import re
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
from collections import deque
from loguru import logger
import aiohttp
import hashlib
import time

from app.models.schemas import DanmuMessage, GiftMessage, MessageType
from config import settings


class DanmuCollector:
    """
    弹幕采集器基类
    
    支持:
    - 实时弹幕采集
    - 礼物消息采集
    - 关注/进入事件
    - 消息队列管理
    """
    
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.is_running = False
        self._message_queue: deque = deque(maxlen=settings.DANMU_QUEUE_SIZE)
        self._callbacks: Dict[str, List[Callable]] = {
            "chat": [],
            "gift": [],
            "follow": [],
            "enter": [],
            "like": [],
            "all": []
        }
        self._ws_connection = None
        self._reconnect_delay = 1
        self._max_reconnect_delay = 60
        
    def on(self, event_type: str, callback: Callable):
        """
        注册事件回调
        
        Args:
            event_type: 事件类型 (chat/gift/follow/enter/like/all)
            callback: 回调函数
        """
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)
        else:
            logger.warning(f"未知事件类型: {event_type}")
            
    def off(self, event_type: str, callback: Callable = None):
        """移除事件回调"""
        if event_type in self._callbacks:
            if callback:
                self._callbacks[event_type].remove(callback)
            else:
                self._callbacks[event_type].clear()
                
    async def _emit(self, event_type: str, data: Any):
        """触发事件回调"""
        # 触发特定类型的回调
        for callback in self._callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"回调执行错误: {e}")
        
        # 触发all类型的回调
        for callback in self._callbacks.get("all", []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, data)
                else:
                    callback(event_type, data)
            except Exception as e:
                logger.error(f"回调执行错误: {e}")
    
    async def start(self):
        """启动采集"""
        if self.is_running:
            logger.warning(f"采集器已在运行: {self.room_id}")
            return
            
        self.is_running = True
        logger.info(f"启动弹幕采集: {self.room_id}")
        
        # 启动采集循环
        asyncio.create_task(self._collect_loop())
        
    async def stop(self):
        """停止采集"""
        self.is_running = False
        if self._ws_connection:
            await self._ws_connection.close()
            self._ws_connection = None
        logger.info(f"停止弹幕采集: {self.room_id}")
        
    async def _collect_loop(self):
        """
        采集循环
        
        这里提供一个模拟实现，实际使用需要对接抖音WebSocket协议
        """
        while self.is_running:
            try:
                # 尝试连接并采集
                await self._connect_and_collect()
            except Exception as e:
                logger.error(f"采集错误: {e}")
                if self.is_running:
                    # 重连延迟
                    await asyncio.sleep(self._reconnect_delay)
                    self._reconnect_delay = min(
                        self._reconnect_delay * 2, 
                        self._max_reconnect_delay
                    )
                    
    async def _connect_and_collect(self):
        """
        连接并采集弹幕
        
        注意: 这里是一个框架实现，具体协议需要根据抖音API调整
        实际使用时可以:
        1. 对接第三方弹幕服务
        2. 使用抖音开放平台API
        3. 解析WebSocket协议
        """
        logger.info(f"连接直播间: {self.room_id}")
        
        # 重置重连延迟
        self._reconnect_delay = 1
        
        # 这里是模拟采集，实际需要对接真实API
        # 示例: 使用aiohttp连接WebSocket
        """
        async with aiohttp.ClientSession() as session:
            ws_url = self._build_ws_url()
            async with session.ws_connect(ws_url) as ws:
                self._ws_connection = ws
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await self._handle_message(msg.data)
                    elif msg.type == aiohttp.WSMsgType.BINARY:
                        await self._handle_binary_message(msg.data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
        """
        
        # 模拟模式: 保持运行状态
        while self.is_running:
            await asyncio.sleep(1)
    
    def _build_ws_url(self) -> str:
        """构建WebSocket URL"""
        # 实际需要根据抖音协议构建
        return f"{settings.DOUYIN_LIVE_WS_URL}?room_id={self.room_id}"
    
    async def _handle_message(self, raw_data: str):
        """处理文本消息"""
        try:
            data = json.loads(raw_data)
            await self._parse_and_emit(data)
        except json.JSONDecodeError:
            logger.warning(f"无效JSON数据: {raw_data[:100]}")
            
    async def _handle_binary_message(self, data: bytes):
        """
        处理二进制消息 (protobuf)
        
        抖音使用protobuf协议，需要解码
        """
        # 需要实现protobuf解析
        # 这里是框架代码
        pass
    
    async def _parse_and_emit(self, data: Dict[str, Any]):
        """解析消息并触发事件"""
        msg_type = data.get("type", "")
        
        if msg_type == "chat":
            message = DanmuMessage(
                room_id=self.room_id,
                user_id=data.get("user_id", ""),
                username=data.get("username", ""),
                content=data.get("content", ""),
                msg_type=MessageType.CHAT,
                extra_data=data.get("extra", {})
            )
            self._message_queue.append(message)
            await self._emit("chat", message)
            
        elif msg_type == "gift":
            message = GiftMessage(
                room_id=self.room_id,
                user_id=data.get("user_id", ""),
                username=data.get("username", ""),
                gift_name=data.get("gift_name", ""),
                gift_count=data.get("gift_count", 1),
                gift_value=data.get("gift_value", 0),
                message=data.get("message")
            )
            await self._emit("gift", message)
            
        elif msg_type == "follow":
            await self._emit("follow", data)
            
        elif msg_type == "enter":
            await self._emit("enter", data)
            
        elif msg_type == "like":
            await self._emit("like", data)
    
    # ==================== 模拟数据接口 ====================
    
    async def inject_message(self, message: DanmuMessage):
        """
        注入消息 (用于测试或模拟)
        
        可以用于:
        1. 测试游戏逻辑
        2. 接入其他弹幕源
        3. 手动触发事件
        """
        self._message_queue.append(message)
        await self._emit("chat", message)
        
    async def inject_gift(self, gift: GiftMessage):
        """注入礼物消息"""
        await self._emit("gift", gift)
        
    def get_recent_messages(self, count: int = 50) -> List[DanmuMessage]:
        """获取最近的消息"""
        messages = list(self._message_queue)
        return messages[-count:] if len(messages) > count else messages


class DouyinOpenPlatformCollector(DanmuCollector):
    """
    抖音开放平台弹幕采集器
    
    使用抖音开放平台API获取弹幕
    需要配置开放平台应用信息
    """
    
    def __init__(self, room_id: str, app_id: str, app_secret: str):
        super().__init__(room_id)
        self.app_id = app_id
        self.app_secret = app_secret
        self._access_token = None
        
    async def _get_access_token(self) -> str:
        """获取访问令牌"""
        # 实现抖音开放平台OAuth流程
        pass
    
    async def _connect_and_collect(self):
        """使用开放平台API采集"""
        # 实现开放平台WebSocket连接
        pass


class ThirdPartyCollector(DanmuCollector):
    """
    第三方服务弹幕采集器
    
    对接第三方弹幕服务API
    """
    
    def __init__(self, room_id: str, api_url: str, api_key: str = None):
        super().__init__(room_id)
        self.api_url = api_url
        self.api_key = api_key
        
    async def _connect_and_collect(self):
        """连接第三方服务"""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        async with aiohttp.ClientSession() as session:
            ws_url = f"{self.api_url}/ws/{self.room_id}"
            try:
                async with session.ws_connect(ws_url, headers=headers) as ws:
                    self._ws_connection = ws
                    logger.info(f"已连接第三方服务: {ws_url}")
                    
                    async for msg in ws:
                        if not self.is_running:
                            break
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await self._handle_message(msg.data)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error(f"WebSocket错误: {ws.exception()}")
                            break
            except aiohttp.ClientError as e:
                logger.error(f"连接错误: {e}")
                raise
