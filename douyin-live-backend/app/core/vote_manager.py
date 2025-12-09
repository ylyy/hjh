"""
投票管理器

功能:
1. 创建投票会话
2. 收集和统计投票
3. 处理VIP/礼物加权投票
4. 投票结果计算
"""
import asyncio
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import uuid
from loguru import logger

from app.models.schemas import VoteMessage, VoteResult
from config import settings


@dataclass
class VoteOption:
    """投票选项"""
    id: str
    name: str
    description: str = ""
    votes: int = 0
    weighted_votes: float = 0.0
    voters: List[str] = field(default_factory=list)


@dataclass
class VoteSession:
    """投票会话"""
    id: str
    room_id: str
    title: str
    options: Dict[str, VoteOption]
    status: str = "active"  # active, closed, cancelled
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_seconds: int = 30
    config: Dict[str, Any] = field(default_factory=dict)
    
    # 投票者记录 (防止重复投票)
    _voted_users: set = field(default_factory=set)
    
    def is_active(self) -> bool:
        """检查投票是否活跃"""
        if self.status != "active":
            return False
        if self.end_time and datetime.utcnow() > self.end_time:
            return False
        return True
    
    def has_voted(self, user_id: str) -> bool:
        """检查用户是否已投票"""
        return user_id in self._voted_users
    
    def add_vote(
        self, 
        user_id: str, 
        option_id: str, 
        weight: float = 1.0,
        username: str = ""
    ) -> bool:
        """
        添加投票
        
        Args:
            user_id: 用户ID
            option_id: 选项ID
            weight: 投票权重
            username: 用户名
            
        Returns:
            是否成功
        """
        if not self.is_active():
            return False
            
        if self.has_voted(user_id):
            return False
            
        if option_id not in self.options:
            return False
            
        option = self.options[option_id]
        option.votes += 1
        option.weighted_votes += weight
        option.voters.append(username or user_id)
        self._voted_users.add(user_id)
        
        return True
    
    def get_results(self) -> Dict[str, Any]:
        """获取投票结果"""
        results = {
            "session_id": self.id,
            "title": self.title,
            "status": self.status,
            "total_votes": len(self._voted_users),
            "options": {},
            "winner": None,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None
        }
        
        max_votes = 0
        winner = None
        
        for opt_id, option in self.options.items():
            results["options"][opt_id] = {
                "name": option.name,
                "votes": option.votes,
                "weighted_votes": option.weighted_votes,
                "percentage": (option.votes / len(self._voted_users) * 100) if self._voted_users else 0
            }
            if option.votes > max_votes:
                max_votes = option.votes
                winner = opt_id
                
        results["winner"] = winner
        return results
    
    def close(self):
        """关闭投票"""
        self.status = "closed"
        self.end_time = datetime.utcnow()


class VoteManager:
    """
    投票管理器
    
    管理多个投票会话，支持:
    - 普通投票 (1人1票)
    - 加权投票 (VIP/礼物加权)
    - 连续投票 (多轮投票)
    """
    
    def __init__(self):
        self._sessions: Dict[str, VoteSession] = {}
        self._room_sessions: Dict[str, str] = {}  # room_id -> session_id
        self._callbacks: Dict[str, List[Callable]] = {
            "vote_created": [],
            "vote_received": [],
            "vote_closed": [],
            "vote_result": []
        }
        self._timers: Dict[str, asyncio.Task] = {}
        
    def on(self, event: str, callback: Callable):
        """注册事件回调"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
            
    async def _emit(self, event: str, data: Any):
        """触发事件"""
        for callback in self._callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"投票回调错误: {e}")
    
    async def create_session(
        self,
        room_id: str,
        options: List[str],
        title: str = "投票",
        duration_seconds: int = None,
        config: Dict = None
    ) -> VoteSession:
        """
        创建投票会话
        
        Args:
            room_id: 直播间ID
            options: 选项列表
            title: 投票标题
            duration_seconds: 持续时间
            config: 额外配置
            
        Returns:
            投票会话对象
        """
        # 关闭该房间的现有会话
        await self.close_session_by_room(room_id)
        
        session_id = str(uuid.uuid4())[:8]
        duration = duration_seconds or settings.VOTE_WINDOW_SECONDS
        
        # 创建选项
        vote_options = {}
        for i, opt_name in enumerate(options, 1):
            opt_id = str(i)
            vote_options[opt_id] = VoteOption(
                id=opt_id,
                name=opt_name
            )
            
        session = VoteSession(
            id=session_id,
            room_id=room_id,
            title=title,
            options=vote_options,
            duration_seconds=duration,
            end_time=datetime.utcnow() + timedelta(seconds=duration),
            config=config or {}
        )
        
        self._sessions[session_id] = session
        self._room_sessions[room_id] = session_id
        
        # 设置自动关闭定时器
        self._timers[session_id] = asyncio.create_task(
            self._auto_close(session_id, duration)
        )
        
        await self._emit("vote_created", session)
        logger.info(f"创建投票会话: {session_id}, 房间: {room_id}, 选项: {options}")
        
        return session
    
    async def _auto_close(self, session_id: str, delay: int):
        """自动关闭投票"""
        await asyncio.sleep(delay)
        await self.close_session(session_id)
        
    async def vote(
        self,
        room_id: str,
        user_id: str,
        option: str,
        username: str = "",
        weight: float = 1.0
    ) -> bool:
        """
        投票
        
        Args:
            room_id: 直播间ID
            user_id: 用户ID
            option: 投票选项 (1, 2, 3...)
            username: 用户名
            weight: 投票权重
            
        Returns:
            是否成功
        """
        session_id = self._room_sessions.get(room_id)
        if not session_id:
            return False
            
        session = self._sessions.get(session_id)
        if not session:
            return False
            
        success = session.add_vote(user_id, option, weight, username)
        
        if success:
            await self._emit("vote_received", {
                "session": session,
                "user_id": user_id,
                "username": username,
                "option": option,
                "weight": weight
            })
            logger.debug(f"收到投票: {username}({user_id}) -> {option}")
            
        return success
    
    async def close_session(self, session_id: str) -> Optional[Dict]:
        """关闭投票会话"""
        session = self._sessions.get(session_id)
        if not session:
            return None
            
        session.close()
        
        # 取消定时器
        timer = self._timers.pop(session_id, None)
        if timer:
            timer.cancel()
            
        # 移除房间映射
        if self._room_sessions.get(session.room_id) == session_id:
            del self._room_sessions[session.room_id]
            
        results = session.get_results()
        
        await self._emit("vote_closed", session)
        await self._emit("vote_result", results)
        
        logger.info(f"投票结束: {session_id}, 结果: {results}")
        
        return results
    
    async def close_session_by_room(self, room_id: str) -> Optional[Dict]:
        """关闭指定房间的投票"""
        session_id = self._room_sessions.get(room_id)
        if session_id:
            return await self.close_session(session_id)
        return None
    
    def get_session(self, session_id: str) -> Optional[VoteSession]:
        """获取投票会话"""
        return self._sessions.get(session_id)
    
    def get_room_session(self, room_id: str) -> Optional[VoteSession]:
        """获取房间当前的投票会话"""
        session_id = self._room_sessions.get(room_id)
        if session_id:
            return self._sessions.get(session_id)
        return None
    
    def get_results(self, session_id: str) -> Optional[Dict]:
        """获取投票结果"""
        session = self._sessions.get(session_id)
        if session:
            return session.get_results()
        return None
    
    def get_room_results(self, room_id: str) -> Optional[Dict]:
        """获取房间投票结果"""
        session = self.get_room_session(room_id)
        if session:
            return session.get_results()
        return None
    
    async def process_danmu(self, room_id: str, user_id: str, content: str, username: str = "", is_vip: bool = False):
        """
        处理弹幕投票
        
        自动识别投票内容并记录
        """
        # 检查是否有活跃投票
        session = self.get_room_session(room_id)
        if not session or not session.is_active():
            return False
            
        # 尝试解析投票选项
        option = self._parse_vote(content, len(session.options))
        if not option:
            return False
            
        # 计算权重
        weight = 2.0 if is_vip else 1.0
        
        return await self.vote(room_id, user_id, option, username, weight)
    
    def _parse_vote(self, content: str, max_option: int) -> Optional[str]:
        """解析投票内容"""
        import re
        
        content = content.strip()
        
        # 纯数字
        if content.isdigit():
            opt = int(content)
            if 1 <= opt <= max_option:
                return str(opt)
                
        # 选X / 投X
        match = re.match(r'^[选投](\d+)$', content)
        if match:
            opt = int(match.group(1))
            if 1 <= opt <= max_option:
                return str(opt)
                
        # 字母选项
        match = re.match(r'^([A-Za-z])$', content)
        if match:
            opt = ord(match.group(1).upper()) - ord('A') + 1
            if 1 <= opt <= max_option:
                return str(opt)
                
        return None
    
    def cleanup_expired(self, max_age_hours: int = 24):
        """清理过期会话"""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        expired = [
            sid for sid, session in self._sessions.items()
            if session.start_time < cutoff and session.status != "active"
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)
