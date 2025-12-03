"""
导演Agent - 负责实时决策和行为干预
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
import random


class DirectorAgent:
    """
    导演Agent职责:
    1. 实时响应用户行为事件
    2. 做出即时干预决策
    3. 控制提醒的时机和方式
    4. 与策划Agent协作执行策略
    """
    
    def __init__(self, db_path: str = "data/coach.db"):
        self.db_path = db_path
        self.intervention_cooldown = {}  # 防止过度打扰
        self.context = {
            'last_intervention_time': None,
            'user_mood': 'neutral',  # neutral, focused, stressed
            'daily_interruption_count': 0
        }
    
    def on_app_opened(self, app_name: str, app_category: str) -> Dict:
        """
        当用户打开应用时的处理
        
        Args:
            app_name: 应用名称
            app_category: 应用分类 (工作/娱乐/社交等)
            
        Returns:
            干预决策
        """
        timestamp = datetime.now()
        
        # 记录行为
        self._log_behavior(app_name, app_category, timestamp)
        
        # 判断是否需要干预
        should_intervene = self._should_intervene(app_name, app_category, timestamp)
        
        if not should_intervene:
            return {
                'action': 'observe',
                'message': '继续观察，不干预'
            }
        
        # 选择干预策略
        intervention = self._select_intervention_strategy(app_name, app_category)
        
        # 执行干预
        response = self._execute_intervention(intervention)
        
        # 更新上下文
        self.context['last_intervention_time'] = timestamp
        self.context['daily_interruption_count'] += 1
        
        return response
    
    def _should_intervene(self, app_name: str, app_category: str, 
                          timestamp: datetime) -> bool:
        """
        决定是否应该干预
        """
        # 1. 检查应用类型
        if app_category not in ['游戏', '社交', '视频', '购物']:
            return False  # 非娱乐应用不干预
        
        # 2. 检查冷却时间（避免频繁打扰）
        if self.context['last_intervention_time']:
            time_since_last = (timestamp - self.context['last_intervention_time']).seconds
            if time_since_last < 1800:  # 30分钟内不重复干预
                return False
        
        # 3. 检查每日干预次数
        if self.context['daily_interruption_count'] >= 10:  # 每天最多10次
            return False
        
        # 4. 检查时间段
        hour = timestamp.hour
        if hour < 8 or hour > 23:  # 休息时间不打扰
            return False
        
        # 5. 检查用户状态
        if self.context['user_mood'] == 'stressed':
            return False  # 用户压力大时减少干预
        
        # 6. 查询当前目标进度
        goals_at_risk = self._check_goals_status()
        if goals_at_risk:
            return True
        
        # 7. 随机干预（保持用户警觉）
        return random.random() < 0.3  # 30%概率
    
    def _select_intervention_strategy(self, app_name: str, 
                                     app_category: str) -> Dict:
        """
        选择干预策略
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查询该应用的历史干预效果
        cursor.execute("""
            SELECT intervention_result, COUNT(*) as effectiveness
            FROM user_behavior
            WHERE app_name = ? AND intervention_result IS NOT NULL
            GROUP BY intervention_result
            ORDER BY effectiveness DESC
            LIMIT 1
        """, (app_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        # 根据历史效果选择策略
        if result and result[0] == 'dismissed':
            # 如果用户经常忽略，使用更有吸引力的方式
            strategy_type = 'achievement_reminder'
        elif result and result[0] == 'accepted':
            # 如果用户积极响应，使用鼓励性提醒
            strategy_type = 'gentle_reminder'
        else:
            # 默认策略
            strategy_type = 'goal_progress'
        
        strategies = {
            'gentle_reminder': {
                'type': 'notification',
                'title': '💡 温馨提示',
                'message': f'您打开了{app_name}，别忘了今天的目标哦！',
                'actions': ['我知道了', '查看目标'],
                'tone': 'supportive'
            },
            'goal_progress': {
                'type': 'progress_popup',
                'title': '🎯 目标进度',
                'message': self._get_goal_progress_message(),
                'actions': ['继续努力', '调整目标'],
                'tone': 'motivating'
            },
            'achievement_reminder': {
                'type': 'achievement_preview',
                'title': '🏆 即将解锁',
                'message': '再坚持3天，您将解锁"自律大师"成就！',
                'actions': ['看看成就', '稍后提醒'],
                'tone': 'exciting'
            },
            'time_limit_warning': {
                'type': 'warning',
                'title': '⏰ 时间预警',
                'message': f'今日{app_category}时间已达上限70%',
                'actions': ['立即停止', '再给我5分钟'],
                'tone': 'urgent'
            }
        }
        
        return strategies.get(strategy_type, strategies['gentle_reminder'])
    
    def _execute_intervention(self, intervention: Dict) -> Dict:
        """
        执行干预动作
        """
        execution_result = {
            'timestamp': datetime.now().isoformat(),
            'intervention_type': intervention['type'],
            'title': intervention['title'],
            'message': intervention['message'],
            'actions': intervention['actions'],
            'tone': intervention['tone'],
            'status': 'sent'
        }
        
        # 根据干预类型执行不同的动作
        if intervention['type'] == 'notification':
            execution_result['display_method'] = 'android_notification'
        elif intervention['type'] == 'progress_popup':
            execution_result['display_method'] = 'fullscreen_overlay'
        elif intervention['type'] == 'achievement_preview':
            execution_result['display_method'] = 'animated_card'
        
        return execution_result
    
    def _log_behavior(self, app_name: str, app_category: str, timestamp: datetime):
        """记录用户行为"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_behavior (timestamp, app_name, app_category)
            VALUES (?, ?, ?)
        """, (timestamp, app_name, app_category))
        
        conn.commit()
        conn.close()
    
    def _check_goals_status(self) -> List[Dict]:
        """检查目标状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, goal_type, target_value, current_value
            FROM goals
            WHERE status = 'active'
        """)
        
        goals_at_risk = []
        for row in cursor.fetchall():
            goal_id, goal_type, target, current = row
            progress = (current / target * 100) if target > 0 else 0
            
            if progress < 30:  # 进度低于30%
                goals_at_risk.append({
                    'goal_id': goal_id,
                    'goal_type': goal_type,
                    'progress': progress
                })
        
        conn.close()
        return goals_at_risk
    
    def _get_goal_progress_message(self) -> str:
        """获取目标进度消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT goal_type, current_value, target_value
            FROM goals
            WHERE status = 'active'
            ORDER BY id DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            goal_type, current, target = result
            progress = int((current / target * 100)) if target > 0 else 0
            return f"{goal_type}: {progress}% 完成 ({current}/{target})"
        
        return "暂无活跃目标，去设置一个吧！"
    
    def handle_user_response(self, intervention_id: str, 
                            user_action: str) -> Dict:
        """
        处理用户对干预的响应
        
        Args:
            intervention_id: 干预ID
            user_action: 用户选择的动作
            
        Returns:
            后续动作
        """
        # 记录用户响应
        response_result = 'accepted' if user_action in ['查看目标', '继续努力', '立即停止'] else 'dismissed'
        
        # 更新数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE user_behavior
            SET intervention_result = ?
            WHERE id = (SELECT MAX(id) FROM user_behavior)
        """, (response_result,))
        
        conn.commit()
        conn.close()
        
        # 根据用户响应调整后续行为
        if user_action == '查看目标':
            return {'action': 'show_goals_page'}
        elif user_action == '看看成就':
            return {'action': 'show_achievements_page'}
        elif user_action == '立即停止':
            return {
                'action': 'praise',
                'message': '太棒了！您的自律值+10 ⭐'
            }
        else:
            return {'action': 'dismiss'}
    
    def evaluate_user_mood(self, recent_actions: List[Dict]) -> str:
        """
        评估用户当前情绪状态
        
        Args:
            recent_actions: 最近的用户行为列表
            
        Returns:
            情绪状态: focused, neutral, stressed
        """
        # 简单的情绪评估逻辑
        entertainment_count = sum(
            1 for action in recent_actions 
            if action.get('category') in ['游戏', '视频']
        )
        
        if entertainment_count > 5:
            return 'stressed'  # 频繁使用娱乐应用可能表示压力大
        elif entertainment_count == 0:
            return 'focused'  # 专注工作
        else:
            return 'neutral'
    
    def generate_smart_notification(self, context: Dict) -> str:
        """
        生成智能通知内容
        
        Args:
            context: 上下文信息
            
        Returns:
            通知文本
        """
        templates = {
            'morning': [
                "🌅 早上好！今天的目标是：{goal}",
                "💪 新的一天，让我们一起加油！",
            ],
            'afternoon': [
                "☀️ 下午好，休息一下，喝杯水吧！",
                "🎯 距离今日目标还差{progress}%",
            ],
            'evening': [
                "🌙 晚上好，回顾一下今天的成就吧！",
                "⭐ 今日生产力得分：{score}分",
            ],
            'achievement': [
                "🏆 恭喜！您解锁了新成就：{achievement}",
                "🎉 太棒了！连续{days}天保持好习惯！",
            ]
        }
        
        hour = datetime.now().hour
        if hour < 12:
            period = 'morning'
        elif hour < 18:
            period = 'afternoon'
        else:
            period = 'evening'
        
        template = random.choice(templates.get(period, templates['morning']))
        
        # 填充模板
        return template.format(**context)


if __name__ == "__main__":
    # 测试代码
    director = DirectorAgent()
    
    # 模拟用户打开应用
    result = director.on_app_opened("王者荣耀", "游戏")
    print("干预结果:", json.dumps(result, ensure_ascii=False, indent=2))
    
    # 模拟用户响应
    response = director.handle_user_response("intervention_1", "查看目标")
    print("\n用户响应处理:", json.dumps(response, ensure_ascii=False, indent=2))
