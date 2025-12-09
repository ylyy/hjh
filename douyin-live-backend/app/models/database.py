"""
数据库配置和模型
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from datetime import datetime
from config import settings


class Base(DeclarativeBase):
    """SQLAlchemy基类"""
    pass


# 直播间配置表
class LiveRoom(Base):
    """直播间配置"""
    __tablename__ = "live_rooms"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(64), unique=True, nullable=False, comment="直播间ID")
    name = Column(String(128), comment="直播间名称")
    status = Column(String(20), default="stopped", comment="状态: running/stopped/error")
    game_type = Column(String(50), comment="当前游戏类型")
    game_config = Column(JSON, default={}, comment="游戏配置")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 弹幕记录表
class DanmuRecord(Base):
    """弹幕记录"""
    __tablename__ = "danmu_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(64), comment="用户ID")
    username = Column(String(128), comment="用户名")
    content = Column(Text, comment="弹幕内容")
    msg_type = Column(String(20), comment="消息类型: chat/gift/follow/like/enter")
    extra_data = Column(JSON, default={}, comment="额外数据")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# 礼物记录表
class GiftRecord(Base):
    """礼物记录"""
    __tablename__ = "gift_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(64), comment="用户ID")
    username = Column(String(128), comment="用户名")
    gift_name = Column(String(64), comment="礼物名称")
    gift_count = Column(Integer, default=1, comment="礼物数量")
    gift_value = Column(Float, default=0, comment="礼物价值")
    message = Column(Text, comment="打赏留言")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# 投票记录表
class VoteRecord(Base):
    """投票记录"""
    __tablename__ = "vote_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(64), nullable=False, index=True)
    session_id = Column(String(64), comment="投票会话ID")
    user_id = Column(String(64), comment="用户ID")
    username = Column(String(128), comment="用户名")
    vote_option = Column(String(64), comment="投票选项")
    vote_weight = Column(Float, default=1.0, comment="投票权重")
    is_vip = Column(Boolean, default=False, comment="是否VIP")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# 游戏会话表
class GameSession(Base):
    """游戏会话"""
    __tablename__ = "game_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(64), nullable=False, index=True)
    game_type = Column(String(50), nullable=False, comment="游戏类型")
    status = Column(String(20), default="active", comment="状态: active/paused/finished")
    game_state = Column(JSON, default={}, comment="游戏状态数据")
    config = Column(JSON, default={}, comment="游戏配置")
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)


# 规则配置表
class RuleConfig(Base):
    """规则配置"""
    __tablename__ = "rule_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(64), nullable=False, index=True)
    rule_type = Column(String(50), comment="规则类型: vote/keyword/command/gift")
    pattern = Column(Text, comment="正则表达式模式")
    action = Column(String(50), comment="触发动作")
    priority = Column(Integer, default=0, comment="优先级")
    enabled = Column(Boolean, default=True, comment="是否启用")
    config = Column(JSON, default={}, comment="额外配置")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# 创建异步会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """获取数据库会话"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
