"""
游戏模块

提供可插拔的游戏引擎框架
"""
from .base import BaseGame, GameEngine
from .story_game import AIStoryGame
from .puzzle_game import AIPuzzleGame

__all__ = ["BaseGame", "GameEngine", "AIStoryGame", "AIPuzzleGame"]
