package com.productivity.assistant.agent

import android.content.Context
import com.productivity.assistant.ai.AIService
import com.productivity.assistant.data.entity.Goal
import com.productivity.assistant.data.entity.GoalType
import com.productivity.assistant.data.repository.GoalRepository
import com.productivity.assistant.data.repository.UsageStats
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import java.util.*

/**
 * 策划Agent - 负责长期规划和目标设定
 * 
 * 职责：
 * 1. 分析用户历史数据
 * 2. 制定个性化目标
 * 3. 生成每日工作计划
 * 4. 评估目标完成度
 */
class PlannerAgent(
    private val context: Context,
    private val goalRepository: GoalRepository
) {
    
    private val scope = CoroutineScope(Dispatchers.Default)
    private val aiService = AIService(context)
    
    /**
     * 分析用户数据并生成建议目标（使用AI增强）
     */
    suspend fun analyzeAndSuggestGoals(): List<GoalSuggestion> {
        val activeGoals = goalRepository.getActiveGoals().first()
        val recentUsage = goalRepository.getRecentUsageStats(7) // 最近7天
        
        // 使用AI生成目标建议
        val workHistory = "平均每日工作${recentUsage.averageWorkHours}小时，娱乐${recentUsage.averageEntertainmentTime}小时"
        val currentGoals = activeGoals.map { it.title }
        val userPreferences = "目标完成率${(recentUsage.goalCompletionRate * 100).toInt()}%"
        
        val aiSuggestions = try {
            aiService.generateGoalSuggestions(
                workHistory = workHistory,
                currentGoals = currentGoals,
                userPreferences = userPreferences
            )
        } catch (e: Exception) {
            emptyList()
        }
        
        // 将AI建议转换为GoalSuggestion对象
        val suggestions = aiSuggestions.mapIndexed { index, title ->
            GoalSuggestion(
                title = title,
                description = "AI智能建议",
                type = GoalType.DAILY,
                targetValue = when {
                    title.contains("小时") -> 4
                    title.contains("分钟") -> 30
                    title.contains("任务") -> 3
                    else -> 1
                },
                unit = when {
                    title.contains("小时") -> "小时"
                    title.contains("分钟") -> "分钟"
                    title.contains("任务") -> "个任务"
                    else -> "项"
                }
            )
        }.toMutableList()
        
        // 如果AI没有生成足够的建议，添加默认建议
        if (suggestions.isEmpty()) {
            val avgWorkHours = recentUsage.averageWorkHours
            if (avgWorkHours < 4) {
                suggestions.add(
                    GoalSuggestion(
                        title = "增加每日工作时间",
                        description = "建议设置每日工作4小时以上的目标",
                        type = GoalType.DAILY,
                        targetValue = 4,
                        unit = "小时"
                    )
                )
            }
            
            val avgEntertainmentTime = recentUsage.averageEntertainmentTime
            if (avgEntertainmentTime > 2) {
                suggestions.add(
                    GoalSuggestion(
                        title = "减少娱乐时间",
                        description = "建议将每日娱乐时间控制在2小时以内",
                        type = GoalType.DAILY,
                        targetValue = 2,
                        unit = "小时"
                    )
                )
            }
            
            val completionRate = recentUsage.goalCompletionRate
            if (completionRate < 0.7) {
                suggestions.add(
                    GoalSuggestion(
                        title = "提高目标完成率",
                        description = "建议设置更合理的目标，提高完成率",
                        type = GoalType.DAILY,
                        targetValue = 3,
                        unit = "个任务"
                    )
                )
            }
        }
        
        return suggestions
    }
    
    /**
     * 生成每日工作计划
     */
    suspend fun generateDailyPlan(): DailyPlan {
        val activeGoals = goalRepository.getActiveGoals().first()
        val today = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, 0)
            set(Calendar.MINUTE, 0)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }
        
        val dailyGoals = activeGoals.filter { goal ->
            goal.type == GoalType.DAILY && 
            goal.startDate.after(today.time) == false &&
            !goal.isCompleted
        }
        
        return DailyPlan(
            date = today.time,
            goals = dailyGoals,
            estimatedWorkHours = dailyGoals.sumOf { it.targetValue },
            priority = calculatePriority(dailyGoals)
        )
    }
    
    /**
     * 评估目标完成度
     */
    suspend fun evaluateGoalProgress(goalId: Long): GoalEvaluation {
        val goal = goalRepository.getGoalById(goalId) ?: return GoalEvaluation(
            progress = 0f,
            status = GoalStatus.UNKNOWN,
            message = "目标不存在"
        )
        
        val progress = goal.currentValue.toFloat() / goal.targetValue
        val status = when {
            progress >= 1.0f -> GoalStatus.COMPLETED
            progress >= 0.8f -> GoalStatus.NEAR_COMPLETION
            progress >= 0.5f -> GoalStatus.IN_PROGRESS
            progress > 0f -> GoalStatus.STARTED
            else -> GoalStatus.NOT_STARTED
        }
        
        val message = when (status) {
            GoalStatus.COMPLETED -> "恭喜！目标已完成！"
            GoalStatus.NEAR_COMPLETION -> "目标即将完成，继续加油！"
            GoalStatus.IN_PROGRESS -> "目标进展良好，保持节奏！"
            GoalStatus.STARTED -> "目标已开始，继续努力！"
            GoalStatus.NOT_STARTED -> "目标尚未开始，现在就开始吧！"
            GoalStatus.UNKNOWN -> ""
        }
        
        return GoalEvaluation(progress, status, message)
    }
    
    private fun calculatePriority(goals: List<Goal>): Int {
        if (goals.isEmpty()) return 0
        return goals.maxOfOrNull { it.priority } ?: 0
    }
    
    /**
     * 创建目标
     */
    suspend fun createGoal(suggestion: GoalSuggestion): Goal {
        val calendar = Calendar.getInstance()
        val endDate = when (suggestion.type) {
            GoalType.DAILY -> {
                calendar.add(Calendar.DAY_OF_YEAR, 1)
                calendar.time
            }
            GoalType.WEEKLY -> {
                calendar.add(Calendar.WEEK_OF_YEAR, 1)
                calendar.time
            }
            GoalType.MONTHLY -> {
                calendar.add(Calendar.MONTH, 1)
                calendar.time
            }
            GoalType.CUSTOM -> null
        }
        
        return Goal(
            title = suggestion.title,
            description = suggestion.description,
            type = suggestion.type,
            targetValue = suggestion.targetValue,
            unit = suggestion.unit,
            startDate = Date(),
            endDate = endDate,
            priority = 3 // 默认优先级
        )
    }
}

data class GoalSuggestion(
    val title: String,
    val description: String,
    val type: GoalType,
    val targetValue: Int,
    val unit: String
)

data class DailyPlan(
    val date: Date,
    val goals: List<Goal>,
    val estimatedWorkHours: Int,
    val priority: Int
)

data class GoalEvaluation(
    val progress: Float,
    val status: GoalStatus,
    val message: String
)

enum class GoalStatus {
    NOT_STARTED,
    STARTED,
    IN_PROGRESS,
    NEAR_COMPLETION,
    COMPLETED,
    UNKNOWN
}

