"""
应用配置文件
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "抖音直播AIGC后台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/douyin_live.db"
    
    # 抖音直播配置
    DOUYIN_LIVE_WS_URL: str = "wss://webcast3-ws-web-lq.douyin.com/webcast/im/push/v2/"
    DOUYIN_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # AI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # 弹幕采集配置
    DANMU_QUEUE_SIZE: int = 1000
    DANMU_BATCH_SIZE: int = 50
    DANMU_PROCESS_INTERVAL: float = 0.5  # 秒
    
    # 投票配置
    VOTE_WINDOW_SECONDS: int = 30  # 投票窗口时间
    VOTE_MIN_COUNT: int = 3  # 最小投票数
    
    # 礼物配置
    GIFT_TRIGGER_THRESHOLD: int = 1  # 礼物触发阈值
    
    # 正则配置 - 默认规则
    DEFAULT_VOTE_PATTERN: str = r"^[1-9]$|^选[1-9]$|^投[1-9]$"
    DEFAULT_COMMAND_PATTERN: str = r"^[/!！](\w+)(?:\s+(.*))?$"
    DEFAULT_KEYWORD_PATTERNS: List[str] = [
        r"继续|下一个|开始",
        r"暂停|停止|结束",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()


# 确保数据目录存在
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)
