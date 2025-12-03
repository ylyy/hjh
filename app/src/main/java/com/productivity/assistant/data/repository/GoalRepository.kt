package com.productivity.assistant.data.repository

import com.productivity.assistant.data.dao.GoalDao
import com.productivity.assistant.data.entity.Goal
import kotlinx.coroutines.flow.Flow
import java.util.Date

class GoalRepository(private val dao: GoalDao) {
    
    fun getAllGoals(): Flow<List<Goal>> = dao.getAllGoals()
    
    fun getActiveGoals(): Flow<List<Goal>> = dao.getActiveGoals()
    
    suspend fun getGoalById(id: Long): Goal? = dao.getGoalById(id)
    
    fun getGoalsBetween(startDate: Date, endDate: Date): Flow<List<Goal>> {
        return dao.getGoalsBetween(startDate, endDate)
    }
    
    suspend fun insertGoal(goal: Goal): Long = dao.insert(goal)
    
    suspend fun updateGoal(goal: Goal) = dao.update(goal)
    
    suspend fun deleteGoal(goal: Goal) = dao.delete(goal)
    
    suspend fun updateProgress(id: Long, value: Int) = dao.updateProgress(id, value)
    
    // 扩展方法：获取最近使用统计（用于PlannerAgent）
    suspend fun getRecentUsageStats(days: Int): UsageStats {
        // 这里需要从AppUsageRepository获取数据
        // 暂时返回模拟数据
        return UsageStats(
            averageWorkHours = 4.0,
            averageEntertainmentTime = 2.0,
            goalCompletionRate = 0.7
        )
    }
}

data class UsageStats(
    val averageWorkHours: Double,
    val averageEntertainmentTime: Double,
    val goalCompletionRate: Double
)
