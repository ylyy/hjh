package com.productivity.assistant.agent

import android.content.Context
import com.productivity.assistant.data.repository.AppUsageRepository
import com.productivity.assistant.data.repository.GoalRepository
import kotlinx.coroutines.flow.first
import java.util.*

/**
 * 情感Agent - 分析用户情绪状态，调整干预策略
 * 
 * 职责：
 * 1. 识别用户情绪状态
 * 2. 调整干预强度
 * 3. 个性化沟通方式
 * 4. 预测用户需求
 */
class EmotionAgent(
    private val context: Context,
    private val appUsageRepository: AppUsageRepository,
    private val goalRepository: GoalRepository
) {
    
    /**
     * 分析用户当前情绪状态
     */
    suspend fun analyzeEmotionState(): EmotionState {
        val recentUsage = getRecentUsageStats()
        val goals = goalRepository.getActiveGoals().first()
        
        // 分析多个维度
        val stressLevel = analyzeStressLevel(recentUsage)
        val motivationLevel = analyzeMotivationLevel(recentUsage, goals)
        val focusLevel = analyzeFocusLevel(recentUsage)
        
        // 综合判断情绪状态
        val emotionType = determineEmotionType(stressLevel, motivationLevel, focusLevel)
        
        return EmotionState(
            type = emotionType,
            stressLevel = stressLevel,
            motivationLevel = motivationLevel,
            focusLevel = focusLevel,
            recommendation = generateRecommendation(emotionType, recentUsage, goals)
        )
    }
    
    /**
     * 分析压力水平
     */
    private fun analyzeStressLevel(usage: RecentUsageStats): Float {
        var stressScore = 0f
        
        // 频繁切换应用 -> 焦虑
        if (usage.appSwitchFrequency > 20) {
            stressScore += 0.3f
        }
        
        // 深夜使用 -> 压力大
        val hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY)
        if (hour >= 23 || hour <= 2) {
            stressScore += 0.3f
        }
        
        // 娱乐时间过长 -> 逃避压力
        if (usage.entertainmentTime > 3) {
            stressScore += 0.2f
        }
        
        // 社交应用使用频繁 -> 需要陪伴
        if (usage.socialAppUsage > 2) {
            stressScore += 0.2f
        }
        
        return stressScore.coerceIn(0f, 1f)
    }
    
    /**
     * 分析动机水平
     */
    private fun analyzeMotivationLevel(
        usage: RecentUsageStats,
        goals: List<com.productivity.assistant.data.entity.Goal>
    ): Float {
        var motivationScore = 0.5f // 基础分数
        
        // 目标完成率
        val completionRate = goals.count { it.isCompleted }.toFloat() / 
                           goals.size.coerceAtLeast(1)
        motivationScore += completionRate * 0.3f
        
        // 工作时长
        if (usage.workTime > 4) {
            motivationScore += 0.2f
        }
        
        return motivationScore.coerceIn(0f, 1f)
    }
    
    /**
     * 分析专注水平
     */
    private fun analyzeFocusLevel(usage: RecentUsageStats): Float {
        var focusScore = 0.5f
        
        // 应用切换频率低 -> 专注
        if (usage.appSwitchFrequency < 10) {
            focusScore += 0.3f
        }
        
        // 工作时长连续 -> 专注
        if (usage.continuousWorkTime > 2) {
            focusScore += 0.2f
        }
        
        return focusScore.coerceIn(0f, 1f)
    }
    
    /**
     * 确定情绪类型
     */
    private fun determineEmotionType(
        stress: Float,
        motivation: Float,
        focus: Float
    ): EmotionType {
        return when {
            stress > 0.7f -> EmotionType.STRESSED
            motivation < 0.3f -> EmotionType.UNMOTIVATED
            focus < 0.3f -> EmotionType.DISTRACTED
            motivation > 0.7f && focus > 0.7f -> EmotionType.MOTIVATED
            stress < 0.3f && motivation > 0.5f -> EmotionType.CALM
            else -> EmotionType.NEUTRAL
        }
    }
    
    /**
     * 生成个性化建议
     */
    private fun generateRecommendation(
        emotionType: EmotionType,
        usage: RecentUsageStats,
        goals: List<com.productivity.assistant.data.entity.Goal>
    ): String {
        return when (emotionType) {
            EmotionType.STRESSED -> "检测到您可能压力较大，建议先休息一下，调整状态"
            EmotionType.UNMOTIVATED -> "看起来缺乏动力，试试设置一个小目标，完成后给自己奖励"
            EmotionType.DISTRACTED -> "注意力有些分散，建议关闭通知，专注当前任务"
            EmotionType.MOTIVATED -> "状态很好！继续保持这个节奏"
            EmotionType.CALM -> "状态平稳，适合进行深度工作"
            EmotionType.NEUTRAL -> "状态正常，继续努力"
        }
    }
    
    /**
     * 获取最近使用统计
     */
    private suspend fun getRecentUsageStats(): RecentUsageStats {
        val calendar = Calendar.getInstance().apply {
            add(Calendar.HOUR_OF_DAY, -2) // 最近2小时
        }
        
        val records = appUsageRepository.getRecordsBetween(calendar.time, Date()).first()
        
        val entertainmentTime = records
            .filter { it.isEntertainment }
            .sumOf { it.duration } / 1000 / 60 / 60f // 转换为小时
        
        val workTime = records
            .filter { !it.isEntertainment }
            .sumOf { it.duration } / 1000 / 60 / 60f
        
        val appSwitchCount = records.size
        val socialAppUsage = records
            .filter { it.category == com.productivity.assistant.data.entity.AppCategory.SOCIAL }
            .sumOf { it.duration } / 1000 / 60 / 60f
        
        // 计算连续工作时间
        val continuousWorkTime = calculateContinuousWorkTime(records)
        
        return RecentUsageStats(
            entertainmentTime = entertainmentTime,
            workTime = workTime,
            appSwitchFrequency = appSwitchCount,
            socialAppUsage = socialAppUsage,
            continuousWorkTime = continuousWorkTime
        )
    }
    
    private fun calculateContinuousWorkTime(records: List<com.productivity.assistant.data.entity.AppUsageRecord>): Float {
        var maxContinuous = 0L
        var currentContinuous = 0L
        
        records.sortedBy { it.startTime }.forEach { record ->
            if (!record.isEntertainment) {
                currentContinuous += record.duration
                maxContinuous = maxOf(maxContinuous, currentContinuous)
            } else {
                currentContinuous = 0L
            }
        }
        
        return maxContinuous / 1000 / 60 / 60f // 转换为小时
    }
    
    /**
     * 根据情绪状态调整干预强度
     */
    fun adjustInterventionLevel(baseLevel: InterventionLevel, emotionState: EmotionState): InterventionLevel {
        return when (emotionState.type) {
            EmotionType.STRESSED -> {
                // 压力大时，降低干预强度
                when (baseLevel) {
                    InterventionLevel.STRICT -> InterventionLevel.STRONG
                    InterventionLevel.STRONG -> InterventionLevel.MODERATE
                    else -> baseLevel
                }
            }
            EmotionType.UNMOTIVATED -> {
                // 缺乏动力时，增加干预强度
                when (baseLevel) {
                    InterventionLevel.MILD -> InterventionLevel.MODERATE
                    InterventionLevel.MODERATE -> InterventionLevel.STRONG
                    else -> baseLevel
                }
            }
            else -> baseLevel
        }
    }
}

data class EmotionState(
    val type: EmotionType,
    val stressLevel: Float,
    val motivationLevel: Float,
    val focusLevel: Float,
    val recommendation: String
)

enum class EmotionType {
    STRESSED,      // 压力大
    UNMOTIVATED,   // 缺乏动力
    DISTRACTED,    // 注意力分散
    MOTIVATED,     // 有动力
    CALM,          // 平静
    NEUTRAL        // 中性
}

data class RecentUsageStats(
    val entertainmentTime: Float,      // 娱乐时间（小时）
    val workTime: Float,                // 工作时间（小时）
    val appSwitchFrequency: Int,       // 应用切换频率
    val socialAppUsage: Float,         // 社交应用使用时间（小时）
    val continuousWorkTime: Float      // 连续工作时间（小时）
)
