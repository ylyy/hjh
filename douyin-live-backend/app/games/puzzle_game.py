"""
AI解谜投票游戏

功能:
1. AI生成谜题
2. 观众投票选择答案
3. 积分排名系统
4. 礼物用户获得额外权重
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import asyncio
from loguru import logger

from app.games.base import BaseGame, GameEvent
from app.models.schemas import GiftMessage, GameStatus
from app.core.message_processor import ProcessedMessage
from app.core.vote_manager import VoteManager


@dataclass
class Puzzle:
    """谜题"""
    puzzle_id: int
    question: str
    options: List[str]
    correct_answer: int  # 正确答案索引
    hint: str = ""
    explanation: str = ""
    difficulty: str = "medium"
    
    # 投票数据
    votes: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    voters: Dict[str, str] = field(default_factory=dict)  # user_id -> option
    
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlayerScore:
    """玩家分数"""
    user_id: str
    username: str
    score: int = 0
    correct_count: int = 0
    total_count: int = 0
    streak: int = 0  # 连续正确次数
    best_streak: int = 0
    
    def add_result(self, correct: bool, points: int = 10):
        """添加结果"""
        self.total_count += 1
        if correct:
            self.correct_count += 1
            self.score += points
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
        else:
            self.streak = 0


class AIPuzzleGame(BaseGame):
    """
    AI解谜投票游戏
    
    玩法:
    1. AI生成谜题(选择题)
    2. 观众通过弹幕投票选择答案
    3. 统计时间内票数最高的选项
    4. 公布正确答案并计算分数
    5. 打赏用户投票权重增加
    """
    
    game_type = "puzzle"
    game_name = "AI解谜大作战"
    game_description = "AI生成的解谜游戏，观众投票选择答案"
    
    # 默认配置
    DEFAULT_CONFIG = {
        "theme": "综合",              # 谜题主题
        "difficulty": "medium",       # 难度 (easy/medium/hard)
        "vote_duration": 20,          # 投票时间(秒)
        "min_votes": 2,               # 最小投票数
        "puzzle_count": 10,           # 谜题数量
        "points_per_correct": 10,     # 正确得分
        "streak_bonus": 5,            # 连续正确奖励
        "vip_weight": 2.0,            # VIP投票权重
        "gift_weight_bonus": 1.0,     # 礼物权重加成
        "show_hint_after": 10,        # X秒后显示提示
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 合并配置
        self.config = {**self.DEFAULT_CONFIG, **self.config}
        
        # 游戏状态
        self.puzzles: List[Puzzle] = []
        self.current_puzzle: Optional[Puzzle] = None
        self.current_puzzle_idx: int = 0
        
        # 玩家分数
        self.scores: Dict[str, PlayerScore] = {}
        
        # 权重加成 (礼物用户)
        self.weight_bonuses: Dict[str, float] = defaultdict(float)
        
        # 投票管理
        self.vote_manager = VoteManager()
        self._vote_task: Optional[asyncio.Task] = None
        self._hint_task: Optional[asyncio.Task] = None
        
    def _setup_default_rules(self):
        """设置默认规则"""
        # 添加解谜相关规则
        self.message_processor.add_rule(
            "keyword", "puzzle_hint", r"提示|hint"
        )
        self.message_processor.add_rule(
            "keyword", "puzzle_skip", r"跳过|下一题"
        )
        
    async def on_start(self):
        """启动游戏"""
        logger.info(f"启动AI解谜游戏: {self.room_id}")
        
        # 初始化状态
        self.context.update_state("theme", self.config["theme"])
        self.context.update_state("difficulty", self.config["difficulty"])
        self.context.update_state("puzzle_count", 0)
        self.context.update_state("total_puzzles", self.config["puzzle_count"])
        
        # 开始第一题
        await self._next_puzzle()
        
    async def on_stop(self) -> Dict[str, Any]:
        """停止游戏"""
        # 取消任务
        if self._vote_task:
            self._vote_task.cancel()
        if self._hint_task:
            self._hint_task.cancel()
            
        # 计算排名
        rankings = self._get_rankings()
        
        return {
            "theme": self.config["theme"],
            "total_puzzles": len(self.puzzles),
            "rankings": rankings[:10],  # 前10名
            "statistics": self._get_statistics()
        }
        
    async def on_danmu(self, message: ProcessedMessage):
        """处理弹幕"""
        # 检查投票
        if message.is_vote and self.current_puzzle:
            await self._handle_vote(message)
            
        # 检查关键词
        if message.is_keyword:
            for keyword in message.matched_keywords:
                await self._handle_keyword(keyword, message)
                
    async def on_gift(self, gift: GiftMessage, processed: Dict):
        """处理礼物"""
        logger.info(f"收到礼物: {gift.username} - {gift.gift_name}")
        
        # 增加投票权重
        bonus = gift.gift_value * self.config["gift_weight_bonus"] / 100
        self.weight_bonuses[gift.user_id] += bonus
        
        await self.emit(GameEvent.ACTION_TRIGGERED, {
            "action": "gift_bonus",
            "user": gift.username,
            "bonus": bonus,
            "total_bonus": self.weight_bonuses[gift.user_id]
        })
        
    async def _next_puzzle(self):
        """生成下一题"""
        if self.current_puzzle_idx >= self.config["puzzle_count"]:
            # 游戏结束
            await self._end_game()
            return
            
        # 生成谜题
        puzzle = await self._generate_puzzle()
        if not puzzle:
            logger.error("生成谜题失败")
            return
            
        self.puzzles.append(puzzle)
        self.current_puzzle = puzzle
        self.current_puzzle_idx += 1
        
        # 更新状态
        self.context.update_state("puzzle_count", self.current_puzzle_idx)
        self.context.update_state("current_puzzle", {
            "id": puzzle.puzzle_id,
            "question": puzzle.question,
            "options": puzzle.options,
            "difficulty": puzzle.difficulty
        })
        
        await self.emit(GameEvent.AI_GENERATED, {
            "type": "puzzle",
            "puzzle_id": puzzle.puzzle_id,
            "question": puzzle.question,
            "options": puzzle.options,
            "difficulty": puzzle.difficulty
        })
        
        # 开始投票
        await self._start_vote()
        
        # 设置提示定时器
        self._hint_task = asyncio.create_task(
            self._show_hint_delayed()
        )
        
    async def _generate_puzzle(self) -> Optional[Puzzle]:
        """生成谜题"""
        if not self.ai_service:
            logger.warning("AI服务未配置，使用默认谜题")
            return self._get_default_puzzle()
            
        puzzle_data = await self.ai_service.generate_puzzle(
            theme=self.config["theme"],
            difficulty=self.config["difficulty"]
        )
        
        return Puzzle(
            puzzle_id=self.current_puzzle_idx + 1,
            question=puzzle_data["question"],
            options=puzzle_data["options"],
            correct_answer=puzzle_data["answer"],
            hint=puzzle_data.get("hint", ""),
            explanation=puzzle_data.get("explanation", ""),
            difficulty=self.config["difficulty"]
        )
        
    def _get_default_puzzle(self) -> Puzzle:
        """获取默认谜题"""
        return Puzzle(
            puzzle_id=self.current_puzzle_idx + 1,
            question="1 + 1 = ?",
            options=["1", "2", "3", "4"],
            correct_answer=1,
            hint="很简单的数学题",
            explanation="1 + 1 = 2"
        )
        
    async def _start_vote(self):
        """开始投票"""
        if not self.current_puzzle:
            return
            
        session = await self.vote_manager.create_session(
            room_id=self.room_id,
            options=[f"{i+1}. {opt}" for i, opt in enumerate(self.current_puzzle.options)],
            title=f"第{self.current_puzzle.puzzle_id}题",
            duration_seconds=self.config["vote_duration"]
        )
        
        await self.emit(GameEvent.VOTE_STARTED, {
            "session_id": session.id,
            "duration": self.config["vote_duration"],
            "puzzle_id": self.current_puzzle.puzzle_id
        })
        
        # 设置结果回调
        self.vote_manager.on("vote_result", self._on_vote_result)
        
    async def _on_vote_result(self, results: Dict):
        """投票结果处理"""
        if not self.current_puzzle:
            return
            
        # 确定最终答案
        winner = results.get("winner")
        if winner:
            selected_idx = int(winner) - 1
        else:
            selected_idx = -1
            
        correct_idx = self.current_puzzle.correct_answer
        is_correct = selected_idx == correct_idx
        
        # 计算分数
        await self._calculate_scores(is_correct)
        
        # 发送结果
        await self.emit(GameEvent.VOTE_ENDED, {
            "puzzle_id": self.current_puzzle.puzzle_id,
            "question": self.current_puzzle.question,
            "selected_answer": selected_idx,
            "correct_answer": correct_idx,
            "is_correct": is_correct,
            "explanation": self.current_puzzle.explanation,
            "vote_results": results
        })
        
        # 等待一会儿展示结果
        await asyncio.sleep(3)
        
        # 下一题
        if self.status == GameStatus.ACTIVE:
            await self._next_puzzle()
            
    async def _handle_vote(self, message: ProcessedMessage):
        """处理投票弹幕"""
        if not message.vote_option or not self.current_puzzle:
            return
            
        # 检查选项是否有效
        option_idx = int(message.vote_option) - 1
        if option_idx < 0 or option_idx >= len(self.current_puzzle.options):
            return
            
        user_id = message.original.user_id
        username = message.original.username
        
        # 计算权重
        base_weight = 1.0
        if message.original.extra_data.get("is_vip"):
            base_weight = self.config["vip_weight"]
        bonus = self.weight_bonuses.get(user_id, 0)
        weight = base_weight + bonus
        
        # 记录投票
        self.current_puzzle.voters[user_id] = message.vote_option
        self.current_puzzle.votes[message.vote_option] += 1
        
        # 确保玩家记录存在
        if user_id not in self.scores:
            self.scores[user_id] = PlayerScore(
                user_id=user_id,
                username=username
            )
            
        # 投票到投票管理器
        await self.vote_manager.vote(
            room_id=self.room_id,
            user_id=user_id,
            option=message.vote_option,
            username=username,
            weight=weight
        )
        
    async def _calculate_scores(self, group_correct: bool):
        """计算分数"""
        if not self.current_puzzle:
            return
            
        correct_option = str(self.current_puzzle.correct_answer + 1)
        
        for user_id, selected in self.current_puzzle.voters.items():
            if user_id not in self.scores:
                continue
                
            is_correct = selected == correct_option
            player = self.scores[user_id]
            
            # 基础分数
            points = self.config["points_per_correct"] if is_correct else 0
            
            # 连续正确奖励
            if is_correct and player.streak > 0:
                points += self.config["streak_bonus"] * player.streak
                
            player.add_result(is_correct, points)
            
    async def _show_hint_delayed(self):
        """延迟显示提示"""
        await asyncio.sleep(self.config["show_hint_after"])
        
        if self.current_puzzle and self.current_puzzle.hint:
            await self.emit(GameEvent.ACTION_TRIGGERED, {
                "action": "hint",
                "puzzle_id": self.current_puzzle.puzzle_id,
                "hint": self.current_puzzle.hint
            })
            
    async def _handle_keyword(self, keyword: str, message: ProcessedMessage):
        """处理关键词"""
        if "提示" in keyword or "hint" in keyword.lower():
            if self.current_puzzle and self.current_puzzle.hint:
                await self.emit(GameEvent.ACTION_TRIGGERED, {
                    "action": "hint_requested",
                    "puzzle_id": self.current_puzzle.puzzle_id,
                    "hint": self.current_puzzle.hint
                })
                
    async def _end_game(self):
        """结束游戏"""
        self.status = GameStatus.FINISHED
        
        rankings = self._get_rankings()
        
        await self.emit(GameEvent.ENDED, {
            "total_puzzles": len(self.puzzles),
            "rankings": rankings[:10],
            "winner": rankings[0] if rankings else None
        })
        
    def _get_rankings(self) -> List[Dict]:
        """获取排名"""
        sorted_players = sorted(
            self.scores.values(),
            key=lambda p: (p.score, p.correct_count, p.best_streak),
            reverse=True
        )
        
        return [
            {
                "rank": i + 1,
                "user_id": p.user_id,
                "username": p.username,
                "score": p.score,
                "correct_count": p.correct_count,
                "total_count": p.total_count,
                "accuracy": round(p.correct_count / p.total_count * 100, 1) if p.total_count > 0 else 0,
                "best_streak": p.best_streak
            }
            for i, p in enumerate(sorted_players)
        ]
        
    def _get_statistics(self) -> Dict:
        """获取统计数据"""
        total_players = len(self.scores)
        total_votes = sum(p.total_count for p in self.scores.values())
        total_correct = sum(p.correct_count for p in self.scores.values())
        
        return {
            "total_players": total_players,
            "total_votes": total_votes,
            "total_correct": total_correct,
            "average_accuracy": round(total_correct / total_votes * 100, 1) if total_votes > 0 else 0
        }
        
    # ==================== 状态访问 ====================
    
    def get_current_puzzle(self) -> Optional[Dict]:
        """获取当前谜题"""
        if self.current_puzzle:
            return {
                "puzzle_id": self.current_puzzle.puzzle_id,
                "question": self.current_puzzle.question,
                "options": self.current_puzzle.options
            }
        return None
        
    def get_leaderboard(self, top_n: int = 10) -> List[Dict]:
        """获取排行榜"""
        return self._get_rankings()[:top_n]
