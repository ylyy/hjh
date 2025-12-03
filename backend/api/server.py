"""
FastAPI后端服务器 - 双Agent AI系统API
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.planner_agent import PlannerAgent
from agents.director_agent import DirectorAgent

# 初始化FastAPI应用
app = FastAPI(
    title="AI生产力教练API",
    description="双Agent系统API - 策划Agent + 导演Agent",
    version="1.0.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化Agent
planner = PlannerAgent(db_path="data/coach.db")
director = DirectorAgent(db_path="data/coach.db")

# ============= 数据模型 =============

class AppOpenEvent(BaseModel):
    app_name: str
    app_category: str
    timestamp: Optional[str] = None

class UserResponse(BaseModel):
    intervention_id: str
    user_action: str

class GoalCreate(BaseModel):
    goal_type: str
    target_value: float
    duration_days: int
    description: str

class GoalUpdate(BaseModel):
    goal_id: int
    current_value: float

# ============= API端点 =============

@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "running",
        "service": "AI生产力教练",
        "agents": {
            "planner": "策划Agent",
            "director": "导演Agent"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/events/app-opened")
async def handle_app_opened(event: AppOpenEvent, background_tasks: BackgroundTasks):
    """
    处理应用打开事件
    
    这是最核心的API，当Android监控检测到用户打开应用时调用
    """
    try:
        # 导演Agent实时响应
        intervention = director.on_app_opened(
            app_name=event.app_name,
            app_category=event.app_category
        )
        
        # 异步触发策划Agent分析（后台任务）
        background_tasks.add_task(
            planner.analyze_behavior_patterns,
            days=7
        )
        
        return {
            "success": True,
            "intervention": intervention,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interventions/response")
async def handle_user_response(response: UserResponse):
    """处理用户对干预的响应"""
    try:
        result = director.handle_user_response(
            intervention_id=response.intervention_id,
            user_action=response.user_action
        )
        
        return {
            "success": True,
            "next_action": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/behavior")
async def get_behavior_analysis(days: int = 7):
    """获取行为分析报告"""
    try:
        analysis = planner.analyze_behavior_patterns(days=days)
        return {
            "success": True,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/strategy/daily")
async def get_daily_strategy():
    """获取每日策略"""
    try:
        strategy = planner.generate_daily_strategy()
        return {
            "success": True,
            "strategy": strategy
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/goals")
async def create_goal(goal: GoalCreate):
    """创建新目标"""
    try:
        goal_id = planner.create_goal(
            goal_type=goal.goal_type,
            target_value=goal.target_value,
            duration_days=goal.duration_days,
            description=goal.description
        )
        
        return {
            "success": True,
            "goal_id": goal_id,
            "message": "目标创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/goals/progress")
async def update_goal_progress(update: GoalUpdate):
    """更新目标进度"""
    try:
        planner.update_goal_progress(
            goal_id=update.goal_id,
            current_value=update.current_value
        )
        
        return {
            "success": True,
            "message": "目标进度已更新"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/weekly")
async def get_weekly_report():
    """获取周报"""
    try:
        report = planner.get_weekly_report()
        return {
            "success": True,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/achievements")
async def get_achievements():
    """获取所有成就"""
    try:
        import sqlite3
        conn = sqlite3.connect("data/coach.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, achievement_name, unlock_date, description, icon
            FROM achievements
            ORDER BY unlock_date DESC
        """)
        
        achievements = []
        for row in cursor.fetchall():
            achievements.append({
                "id": row[0],
                "name": row[1],
                "unlock_date": row[2],
                "description": row[3],
                "icon": row[4]
            })
        
        conn.close()
        
        return {
            "success": True,
            "achievements": achievements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/goals/active")
async def get_active_goals():
    """获取活跃目标"""
    try:
        import sqlite3
        conn = sqlite3.connect("data/coach.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, goal_type, target_value, current_value, 
                   start_date, end_date, description
            FROM goals
            WHERE status = 'active'
        """)
        
        goals = []
        for row in cursor.fetchall():
            progress = (row[3] / row[2] * 100) if row[2] > 0 else 0
            goals.append({
                "id": row[0],
                "type": row[1],
                "target": row[2],
                "current": row[3],
                "progress": round(progress, 1),
                "start_date": row[4],
                "end_date": row[5],
                "description": row[6]
            })
        
        conn.close()
        
        return {
            "success": True,
            "goals": goals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard")
async def get_dashboard_data():
    """获取仪表盘数据（综合信息）"""
    try:
        # 获取行为分析
        behavior = planner.analyze_behavior_patterns(days=7)
        
        # 获取每日策略
        strategy = planner.generate_daily_strategy()
        
        # 获取活跃目标数量
        import sqlite3
        conn = sqlite3.connect("data/coach.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM goals WHERE status = 'active'")
        active_goals_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM achievements")
        total_achievements = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "dashboard": {
                "productivity_score": behavior['productivity_score'],
                "active_goals": active_goals_count,
                "total_achievements": total_achievements,
                "weekly_entertainment_hours": behavior['total_entertainment_time'],
                "today_strategy": strategy,
                "behavior_summary": behavior
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= 启动配置 =============

if __name__ == "__main__":
    import uvicorn
    
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    
    print("🚀 启动AI生产力教练服务器...")
    print("📊 API文档: http://localhost:8000/docs")
    print("🤖 双Agent系统已就绪")
    print("   - 策划Agent: 长期规划和分析")
    print("   - 导演Agent: 实时决策和干预")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
