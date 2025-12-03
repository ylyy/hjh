"""
策划Agent - 负责长期规划、目标设定和行为模式分析
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3


class PlannerAgent:
    """
    策划Agent职责:
    1. 分析用户的长期行为模式
    2. 制定个性化的目标和策略
    3. 生成每日/每周/每月报告
    4. 优化干预策略
    """
    
    def __init__(self, db_path: str = "data/coach.db"):
        self.db_path = db_path
        self.personality_profile = {}
        self.initialize_database()
    
    def initialize_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表格
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_behavior (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                app_name TEXT,
                app_category TEXT,
                duration INTEGER,
                intervention_result TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_type TEXT,
                target_value REAL,
                current_value REAL,
                start_date DATE,
                end_date DATE,
                status TEXT,
                description TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                achievement_name TEXT,
                unlock_date DATETIME,
                description TEXT,
                icon TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT,
                conditions TEXT,
                actions TEXT,
                priority INTEGER,
                effectiveness_score REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def analyze_behavior_patterns(self, days: int = 7) -> Dict:
        """
        分析用户行为模式
        
        Args:
            days: 分析最近多少天的数据
            
        Returns:
            行为分析报告
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取最近N天的数据
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT app_category, SUM(duration), COUNT(*)
            FROM user_behavior
            WHERE DATE(timestamp) >= ?
            GROUP BY app_category
        """, (start_date,))
        
        category_stats = {}
        total_time = 0
        for row in cursor.fetchall():
            category, duration, count = row
            category_stats[category] = {
                'total_duration': duration,
                'frequency': count,
                'avg_duration': duration / count if count > 0 else 0
            }
            total_time += duration
        
        # 识别问题应用
        problematic_apps = []
        for category, stats in category_stats.items():
            if category in ['游戏', '社交', '视频'] and stats['total_duration'] > 3600:  # 超过1小时
                problematic_apps.append({
                    'category': category,
                    'hours': stats['total_duration'] / 3600,
                    'frequency': stats['frequency']
                })
        
        conn.close()
        
        return {
            'analysis_period': f'{days}天',
            'total_entertainment_time': total_time / 3600,  # 转换为小时
            'category_breakdown': category_stats,
            'problematic_apps': problematic_apps,
            'productivity_score': self._calculate_productivity_score(category_stats, total_time)
        }
    
    def _calculate_productivity_score(self, category_stats: Dict, total_time: int) -> float:
        """
        计算生产力评分 (0-100)
        """
        if total_time == 0:
            return 100
        
        entertainment_time = sum(
            stats['total_duration'] 
            for cat, stats in category_stats.items() 
            if cat in ['游戏', '社交', '视频']
        )
        
        # 娱乐时间占比越低，分数越高
        entertainment_ratio = entertainment_time / total_time if total_time > 0 else 0
        score = max(0, 100 - (entertainment_ratio * 100))
        
        return round(score, 2)
    
    def create_goal(self, goal_type: str, target_value: float, 
                    duration_days: int, description: str) -> int:
        """
        创建新目标
        
        Args:
            goal_type: 目标类型 (例如: '减少游戏时间', '提高专注时间')
            target_value: 目标值
            duration_days: 目标持续天数
            description: 目标描述
            
        Returns:
            目标ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=duration_days)
        
        cursor.execute("""
            INSERT INTO goals (goal_type, target_value, current_value, 
                             start_date, end_date, status, description)
            VALUES (?, ?, 0, ?, ?, 'active', ?)
        """, (goal_type, target_value, start_date, end_date, description))
        
        goal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return goal_id
    
    def update_goal_progress(self, goal_id: int, current_value: float):
        """更新目标进度"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE goals
            SET current_value = ?
            WHERE id = ?
        """, (current_value, goal_id))
        
        # 检查是否完成
        cursor.execute("""
            SELECT target_value, current_value FROM goals WHERE id = ?
        """, (goal_id,))
        target, current = cursor.fetchone()
        
        if current >= target:
            cursor.execute("""
                UPDATE goals SET status = 'completed' WHERE id = ?
            """, (goal_id,))
            self._unlock_achievement(goal_id)
        
        conn.commit()
        conn.close()
    
    def _unlock_achievement(self, goal_id: int):
        """解锁成就"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT goal_type FROM goals WHERE id = ?", (goal_id,))
        goal_type = cursor.fetchone()[0]
        
        achievement_name = f"完成目标: {goal_type}"
        cursor.execute("""
            INSERT INTO achievements (achievement_name, description, icon)
            VALUES (?, ?, ?)
        """, (achievement_name, f"成功完成{goal_type}目标", "🏆"))
        
        conn.commit()
        conn.close()
    
    def generate_daily_strategy(self) -> Dict:
        """
        生成每日策略
        
        Returns:
            包含今日目标、建议和预警的策略字典
        """
        behavior_analysis = self.analyze_behavior_patterns(days=7)
        
        strategies = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'focus_areas': [],
            'recommended_actions': [],
            'alerts': []
        }
        
        # 根据问题应用生成策略
        for app in behavior_analysis['problematic_apps']:
            strategies['focus_areas'].append(app['category'])
            strategies['recommended_actions'].append(
                f"尝试将{app['category']}使用时间减少50%"
            )
        
        # 生产力评分低于60分时发出警报
        if behavior_analysis['productivity_score'] < 60:
            strategies['alerts'].append({
                'level': 'warning',
                'message': f"您的生产力评分为{behavior_analysis['productivity_score']}，需要调整习惯"
            })
        
        return strategies
    
    def create_intervention_strategy(self, trigger_app: str, 
                                    trigger_conditions: Dict) -> Dict:
        """
        创建干预策略
        
        Args:
            trigger_app: 触发应用名称
            trigger_conditions: 触发条件
            
        Returns:
            干预策略
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 根据历史数据分析最有效的干预方式
        cursor.execute("""
            SELECT intervention_result, COUNT(*) as count
            FROM user_behavior
            WHERE app_name = ?
            GROUP BY intervention_result
            ORDER BY count DESC
            LIMIT 1
        """, (trigger_app,))
        
        result = cursor.fetchone()
        most_effective = result[0] if result else 'gentle_reminder'
        
        strategy = {
            'strategy_name': f'干预_{trigger_app}',
            'trigger': trigger_app,
            'conditions': trigger_conditions,
            'actions': [
                {'type': 'notification', 'message': f'您打开了{trigger_app}，记得完成今日目标！'},
                {'type': 'show_progress', 'data': 'current_goals'},
            ],
            'preferred_method': most_effective,
            'priority': 5
        }
        
        # 保存策略到数据库
        cursor.execute("""
            INSERT INTO strategies (strategy_name, conditions, actions, priority)
            VALUES (?, ?, ?, ?)
        """, (strategy['strategy_name'], 
              json.dumps(strategy['conditions']),
              json.dumps(strategy['actions']),
              strategy['priority']))
        
        conn.commit()
        conn.close()
        
        return strategy
    
    def get_weekly_report(self) -> Dict:
        """
        生成周报
        """
        behavior_analysis = self.analyze_behavior_patterns(days=7)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取本周完成的目标
        cursor.execute("""
            SELECT COUNT(*) FROM goals
            WHERE status = 'completed'
            AND DATE(end_date) >= DATE('now', '-7 days')
        """)
        completed_goals = cursor.fetchone()[0]
        
        # 获取本周解锁的成就
        cursor.execute("""
            SELECT COUNT(*) FROM achievements
            WHERE DATE(unlock_date) >= DATE('now', '-7 days')
        """)
        new_achievements = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'week': f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} 到 {datetime.now().strftime('%Y-%m-%d')}",
            'productivity_score': behavior_analysis['productivity_score'],
            'completed_goals': completed_goals,
            'new_achievements': new_achievements,
            'total_entertainment_hours': behavior_analysis['total_entertainment_time'],
            'recommendations': self._generate_recommendations(behavior_analysis)
        }
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """根据分析生成建议"""
        recommendations = []
        
        if analysis['productivity_score'] < 70:
            recommendations.append("建议设置每日娱乐时间上限")
        
        if analysis['total_entertainment_time'] > 14:  # 一周超过14小时
            recommendations.append("娱乐时间偏高，尝试培养新的兴趣爱好")
        
        if len(analysis['problematic_apps']) > 0:
            top_app = analysis['problematic_apps'][0]['category']
            recommendations.append(f"重点关注{top_app}的使用时间")
        
        return recommendations


if __name__ == "__main__":
    # 测试代码
    planner = PlannerAgent()
    
    # 创建目标
    goal_id = planner.create_goal(
        goal_type="减少游戏时间",
        target_value=10,  # 10小时
        duration_days=7,
        description="本周游戏时间控制在10小时以内"
    )
    print(f"创建目标ID: {goal_id}")
    
    # 生成策略
    strategy = planner.generate_daily_strategy()
    print("\n每日策略:", json.dumps(strategy, ensure_ascii=False, indent=2))
