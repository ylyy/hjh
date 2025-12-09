"""
AI小说/故事直播游戏

功能:
1. AI生成连续故事
2. 观众投票选择剧情走向
3. 打赏用户可以影响剧情
4. 关键词触发特殊事件
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from loguru import logger

from app.games.base import BaseGame, GameEvent, GameContext
from app.models.schemas import GiftMessage, GameStatus
from app.core.message_processor import ProcessedMessage
from app.core.vote_manager import VoteManager


@dataclass
class StoryChapter:
    """故事章节"""
    chapter_id: int
    content: str
    options: List[str]
    selected_option: Optional[str] = None
    vote_results: Dict[str, int] = field(default_factory=dict)
    triggered_by: Optional[str] = None  # 触发者 (打赏用户等)
    created_at: datetime = field(default_factory=datetime.utcnow)


class AIStoryGame(BaseGame):
    """
    AI小说直播游戏
    
    玩法:
    1. AI生成故事开头
    2. 每段故事结尾提供选项
    3. 观众通过弹幕投票
    4. 打赏用户可以添加自定义剧情元素
    5. 特定关键词可以触发特殊事件
    """
    
    game_type = "story"
    game_name = "AI小说直播"
    game_description = "AI生成的互动故事，观众投票决定剧情走向"
    
    # 默认配置
    DEFAULT_CONFIG = {
        "style": "悬疑",              # 故事风格
        "title": "神秘故事",           # 故事标题
        "vote_duration": 30,          # 投票时间(秒)
        "min_votes": 3,               # 最小投票数
        "auto_continue": True,        # 自动继续
        "gift_influence": True,       # 礼物影响剧情
        "max_chapters": 50,           # 最大章节数
        "chapter_length": "medium",   # 章节长度
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 合并配置
        self.config = {**self.DEFAULT_CONFIG, **self.config}
        
        # 游戏状态
        self.chapters: List[StoryChapter] = []
        self.current_chapter: Optional[StoryChapter] = None
        self.story_context: str = ""
        self.pending_elements: List[str] = []  # 待加入的剧情元素
        
        # 投票管理
        self.vote_manager = VoteManager()
        self._vote_task: Optional[asyncio.Task] = None
        
    def _setup_default_rules(self):
        """设置默认规则"""
        # 添加故事相关的关键词规则
        self.message_processor.add_rule(
            "keyword", "story_continue", r"继续|下一章|开始"
        )
        self.message_processor.add_rule(
            "keyword", "story_skip", r"跳过|快进"
        )
        
    async def on_start(self):
        """启动游戏"""
        logger.info(f"启动AI小说游戏: {self.room_id}")
        
        # 初始化上下文
        self.context.update_state("title", self.config["title"])
        self.context.update_state("style", self.config["style"])
        self.context.update_state("chapter_count", 0)
        
        # 生成故事开头
        await self._generate_opening()
        
    async def on_stop(self) -> Dict[str, Any]:
        """停止游戏"""
        # 取消投票任务
        if self._vote_task:
            self._vote_task.cancel()
            
        # 返回游戏总结
        return {
            "title": self.config["title"],
            "total_chapters": len(self.chapters),
            "story_summary": self._get_story_summary(),
            "chapters": [
                {
                    "id": ch.chapter_id,
                    "content": ch.content[:200] + "...",
                    "selected_option": ch.selected_option
                }
                for ch in self.chapters
            ]
        }
    
    async def on_danmu(self, message: ProcessedMessage):
        """处理弹幕"""
        # 检查投票
        if message.is_vote and self.current_chapter:
            await self._handle_vote(message)
            
        # 检查关键词
        if message.is_keyword:
            for keyword in message.matched_keywords:
                await self._handle_keyword(keyword, message)
                
        # 检查命令
        if message.is_command:
            await self._handle_command(message)
            
    async def on_gift(self, gift: GiftMessage, processed: Dict):
        """处理礼物"""
        if not self.config["gift_influence"]:
            return
            
        logger.info(f"收到礼物: {gift.username} - {gift.gift_name} x{gift.gift_count}")
        
        # 礼物打赏可以添加剧情元素
        if gift.message:
            self.pending_elements.append(f"{gift.username}希望加入: {gift.message}")
            
            await self.emit(GameEvent.ACTION_TRIGGERED, {
                "action": "gift_element",
                "user": gift.username,
                "element": gift.message,
                "gift": gift.gift_name
            })
            
        # 高价值礼物可以直接触发剧情变化
        if gift.gift_value >= 100:
            await self._trigger_special_event(gift)
    
    async def _generate_opening(self):
        """生成故事开头"""
        if not self.ai_service:
            logger.warning("AI服务未配置")
            return
            
        system_prompt = f"""你是一个{self.config['style']}小说作家。
请为一个名为《{self.config['title']}》的故事写一个引人入胜的开头。
结尾提供3个选项让观众选择接下来的发展方向。
用【选项1】【选项2】【选项3】的格式标注选项。
"""
        
        content = await self.ai_service.generate_text(
            prompt="请开始写故事的开头",
            system_prompt=system_prompt,
            max_tokens=500,
            temperature=0.8
        )
        
        # 解析选项
        options = self._parse_options(content)
        
        # 创建章节
        chapter = StoryChapter(
            chapter_id=1,
            content=content,
            options=options
        )
        
        self.chapters.append(chapter)
        self.current_chapter = chapter
        self.story_context = content
        
        self.context.update_state("chapter_count", 1)
        self.context.update_state("current_content", content)
        self.context.update_state("options", options)
        
        await self.emit(GameEvent.AI_GENERATED, {
            "type": "chapter",
            "chapter_id": 1,
            "content": content,
            "options": options
        })
        
        # 开始投票
        if options:
            await self._start_vote(options)
            
    async def _generate_next_chapter(self, selected_option: str = None):
        """生成下一章"""
        if not self.ai_service:
            return
            
        if len(self.chapters) >= self.config["max_chapters"]:
            await self._generate_ending()
            return
            
        # 构建提示
        prompt = f"之前的故事:\n{self.story_context[-2000:]}\n\n"
        
        if selected_option:
            prompt += f"观众选择: {selected_option}\n\n"
            
        # 加入待定元素
        if self.pending_elements:
            elements = "\n".join(self.pending_elements[:3])
            prompt += f"请在故事中自然地融入以下元素:\n{elements}\n\n"
            self.pending_elements = self.pending_elements[3:]
            
        prompt += "请继续写下一段故事:"
        
        system_prompt = f"""你是一个{self.config['style']}小说作家。
继续这个故事，保持紧凑有趣。
每段结尾提供2-3个选项让观众选择。
用【选项1】【选项2】【选项3】的格式标注选项。
"""
        
        content = await self.ai_service.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=500,
            temperature=0.8
        )
        
        # 解析选项
        options = self._parse_options(content)
        
        # 创建章节
        chapter_id = len(self.chapters) + 1
        chapter = StoryChapter(
            chapter_id=chapter_id,
            content=content,
            options=options,
            selected_option=selected_option
        )
        
        self.chapters.append(chapter)
        self.current_chapter = chapter
        self.story_context += "\n\n" + content
        
        self.context.update_state("chapter_count", chapter_id)
        self.context.update_state("current_content", content)
        self.context.update_state("options", options)
        
        await self.emit(GameEvent.AI_GENERATED, {
            "type": "chapter",
            "chapter_id": chapter_id,
            "content": content,
            "options": options
        })
        
        # 开始投票
        if options:
            await self._start_vote(options)
            
    async def _generate_ending(self):
        """生成故事结局"""
        if not self.ai_service:
            return
            
        prompt = f"之前的故事:\n{self.story_context[-2000:]}\n\n请为这个故事写一个精彩的结局。"
        
        system_prompt = f"""你是一个{self.config['style']}小说作家。
为这个故事写一个令人满意的结局。
不需要提供选项。
"""
        
        content = await self.ai_service.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=600,
            temperature=0.8
        )
        
        # 创建最终章节
        chapter = StoryChapter(
            chapter_id=len(self.chapters) + 1,
            content=content,
            options=[]
        )
        
        self.chapters.append(chapter)
        self.story_context += "\n\n" + content
        
        await self.emit(GameEvent.AI_GENERATED, {
            "type": "ending",
            "content": content
        })
        
        # 结束游戏
        self.status = GameStatus.FINISHED
        await self.emit(GameEvent.ENDED, await self.on_stop())
    
    def _parse_options(self, content: str) -> List[str]:
        """解析选项"""
        import re
        options = []
        
        # 匹配【选项X】格式
        pattern = r'【选项(\d+)】[：:]\s*(.+?)(?=【|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if matches:
            for _, option_text in matches:
                options.append(option_text.strip())
        else:
            # 尝试匹配其他格式
            pattern2 = r'(\d+)[.、）]\s*(.+?)(?=\d+[.、）]|$)'
            matches2 = re.findall(pattern2, content[-500:], re.DOTALL)
            for _, option_text in matches2[:3]:
                clean = option_text.strip()
                if clean and len(clean) < 100:
                    options.append(clean)
                    
        return options[:3]  # 最多3个选项
    
    async def _start_vote(self, options: List[str]):
        """开始投票"""
        session = await self.vote_manager.create_session(
            room_id=self.room_id,
            options=options,
            title=f"第{len(self.chapters)}章走向",
            duration_seconds=self.config["vote_duration"]
        )
        
        await self.emit(GameEvent.VOTE_STARTED, {
            "session_id": session.id,
            "options": options,
            "duration": self.config["vote_duration"]
        })
        
        # 设置投票结束回调
        self.vote_manager.on("vote_result", self._on_vote_result)
        
    async def _on_vote_result(self, results: Dict):
        """投票结果处理"""
        if results["total_votes"] < self.config["min_votes"]:
            # 投票人数不足，随机选择
            import random
            winner = random.choice(list(results["options"].keys()))
        else:
            winner = results["winner"]
            
        # 获取选项内容
        selected_option = None
        if self.current_chapter and winner:
            idx = int(winner) - 1
            if idx < len(self.current_chapter.options):
                selected_option = self.current_chapter.options[idx]
                self.current_chapter.selected_option = selected_option
                self.current_chapter.vote_results = results["options"]
                
        await self.emit(GameEvent.VOTE_ENDED, {
            "results": results,
            "selected": selected_option
        })
        
        # 生成下一章
        if self.config["auto_continue"] and self.status == GameStatus.ACTIVE:
            await self._generate_next_chapter(selected_option)
            
    async def _handle_vote(self, message: ProcessedMessage):
        """处理投票弹幕"""
        if message.vote_option:
            await self.vote_manager.vote(
                room_id=self.room_id,
                user_id=message.original.user_id,
                option=message.vote_option,
                username=message.original.username
            )
            
    async def _handle_keyword(self, keyword: str, message: ProcessedMessage):
        """处理关键词"""
        if "继续" in keyword or "开始" in keyword:
            # 强制继续
            if not self._vote_task or self._vote_task.done():
                await self._generate_next_chapter()
                
    async def _handle_command(self, message: ProcessedMessage):
        """处理命令"""
        cmd = message.command
        
        if cmd == "status":
            # 返回状态
            await self.emit(GameEvent.STATE_CHANGED, self.get_state())
            
        elif cmd == "skip":
            # 跳过投票
            await self.vote_manager.close_session_by_room(self.room_id)
            
    async def _trigger_special_event(self, gift: GiftMessage):
        """触发特殊事件"""
        # 高价值礼物可以触发剧情转折
        prompt = f"""
故事背景: {self.story_context[-1000:]}

用户 {gift.username} 送出了 {gift.gift_name}，请写一个简短的剧情转折，
让故事变得更加精彩。这个转折应该是意外但合理的。
"""
        
        if self.ai_service:
            twist = await self.ai_service.generate_text(
                prompt=prompt,
                max_tokens=200,
                temperature=0.9
            )
            
            self.story_context += f"\n\n[剧情转折 - 感谢{gift.username}]\n{twist}"
            
            await self.emit(GameEvent.AI_GENERATED, {
                "type": "twist",
                "triggered_by": gift.username,
                "content": twist
            })
            
    def _get_story_summary(self) -> str:
        """获取故事摘要"""
        if not self.chapters:
            return ""
        return self.story_context[:500] + "..."
    
    # ==================== 状态访问 ====================
    
    def get_current_chapter(self) -> Optional[Dict]:
        """获取当前章节"""
        if self.current_chapter:
            return {
                "chapter_id": self.current_chapter.chapter_id,
                "content": self.current_chapter.content,
                "options": self.current_chapter.options
            }
        return None
    
    def get_vote_status(self) -> Optional[Dict]:
        """获取投票状态"""
        return self.vote_manager.get_room_results(self.room_id)
