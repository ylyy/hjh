"""
Pydantic数据模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== 枚举类型 ====================

class MessageType(str, Enum):
    """消息类型"""
    CHAT = "chat"          # 普通弹幕
    GIFT = "gift"          # 礼物
    FOLLOW = "follow"      # 关注
    LIKE = "like"          # 点赞
    ENTER = "enter"        # 进入直播间
    SHARE = "share"        # 分享
    SUBSCRIBE = "subscribe" # 订阅


class GameType(str, Enum):
    """游戏类型"""
    STORY = "story"           # AI小说/故事
    PUZZLE = "puzzle"         # AI解谜游戏
    BATTLE = "battle"         # 对战游戏
    QUIZ = "quiz"             # 问答游戏
    CUSTOM = "custom"         # 自定义游戏


class RoomStatus(str, Enum):
    """直播间状态"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    CONNECTING = "connecting"


class GameStatus(str, Enum):
    """游戏状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    FINISHED = "finished"
    WAITING = "waiting"


# ==================== 基础模式 ====================

class DanmuMessage(BaseModel):
    """弹幕消息"""
    room_id: str
    user_id: str
    username: str
    content: str
    msg_type: MessageType = MessageType.CHAT
    extra_data: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class GiftMessage(BaseModel):
    """礼物消息"""
    room_id: str
    user_id: str
    username: str
    gift_name: str
    gift_count: int = 1
    gift_value: float = 0
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VoteMessage(BaseModel):
    """投票消息"""
    room_id: str
    session_id: str
    user_id: str
    username: str
    vote_option: str
    vote_weight: float = 1.0
    is_vip: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==================== API请求/响应模式 ====================

class LiveRoomCreate(BaseModel):
    """创建直播间"""
    room_id: str = Field(..., description="直播间ID")
    name: Optional[str] = Field(None, description="直播间名称")
    game_type: Optional[GameType] = Field(None, description="游戏类型")
    game_config: Dict[str, Any] = Field(default={}, description="游戏配置")


class LiveRoomUpdate(BaseModel):
    """更新直播间"""
    name: Optional[str] = None
    game_type: Optional[GameType] = None
    game_config: Optional[Dict[str, Any]] = None


class LiveRoomResponse(BaseModel):
    """直播间响应"""
    id: int
    room_id: str
    name: Optional[str]
    status: RoomStatus
    game_type: Optional[str]
    game_config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RuleConfigCreate(BaseModel):
    """创建规则配置"""
    room_id: str
    rule_type: str = Field(..., description="规则类型: vote/keyword/command/gift")
    pattern: str = Field(..., description="正则表达式模式")
    action: str = Field(..., description="触发动作")
    priority: int = Field(default=0, description="优先级")
    enabled: bool = Field(default=True, description="是否启用")
    config: Dict[str, Any] = Field(default={}, description="额外配置")


class RuleConfigResponse(BaseModel):
    """规则配置响应"""
    id: int
    room_id: str
    rule_type: str
    pattern: str
    action: str
    priority: int
    enabled: bool
    config: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class GameSessionCreate(BaseModel):
    """创建游戏会话"""
    room_id: str
    game_type: GameType
    config: Dict[str, Any] = {}


class GameSessionResponse(BaseModel):
    """游戏会话响应"""
    id: int
    room_id: str
    game_type: str
    status: str
    game_state: Dict[str, Any]
    config: Dict[str, Any]
    started_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


class VoteSessionCreate(BaseModel):
    """创建投票会话"""
    room_id: str
    options: List[str] = Field(..., description="投票选项列表")
    duration_seconds: int = Field(default=30, description="投票持续时间")
    title: Optional[str] = Field(None, description="投票标题")


class VoteResult(BaseModel):
    """投票结果"""
    session_id: str
    options: Dict[str, int]  # 选项: 票数
    winner: Optional[str]
    total_votes: int
    started_at: datetime
    ended_at: datetime


class AIGenerateRequest(BaseModel):
    """AI生成请求"""
    prompt: str
    context: Optional[str] = None
    max_tokens: int = 500
    temperature: float = 0.7


class AIGenerateResponse(BaseModel):
    """AI生成响应"""
    content: str
    tokens_used: int
    model: str


# ==================== WebSocket消息模式 ====================

class WSMessage(BaseModel):
    """WebSocket消息"""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WSCommand(BaseModel):
    """WebSocket命令"""
    action: str  # start/stop/pause/config
    room_id: str
    params: Dict[str, Any] = {}
