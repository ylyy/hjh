package com.productivity.assistant.psychology

import com.productivity.assistant.data.entity.Goal
import com.productivity.assistant.data.entity.GoalType
import java.util.Date

/**
 * 心理目标 - 基于主体性需求的目标
 * 
 * 心理目标不同于普通目标，它：
 * 1. 直接关联用户的主体性需求
 * 2. 随着需求变化而动态调整
 * 3. 关注心理满足而非表面成就
 * 4. 具有更深层的意义和价值
 */
data class PsychologicalGoal(
    val id: Long = 0,
    val baseGoal: Goal, // 基础目标
    val relatedNeed: SubjectiveNeed, // 关联的主体性需求
    val psychologicalValue: String, // 心理价值描述
    val needSatisfactionTarget: Float, // 需求满足目标（0.0-1.0）
    val adaptationHistory: List<GoalAdaptation> = emptyList(), // 适应历史
    val currentSatisfaction: Float = 0f, // 当前满足度
    val isAlignedWithNeed: Boolean = true // 是否与需求对齐
)

/**
 * 目标适应记录
 */
data class GoalAdaptation(
    val date: Date,
    val reason: AdaptationReason,
    val oldValue: String,
    val newValue: String,
    val needChange: SubjectiveNeed? // 触发适应的需求变化
)

enum class AdaptationReason {
    NEED_INTENSITY_CHANGED,    // 需求强度变化
    NEED_EMERGED,              // 新需求出现
    NEED_FADED,                // 需求消退
    SATISFACTION_LOW,          // 满足度低
    CONFLICT_RESOLUTION        // 冲突解决
}

/**
 * 心理目标推荐
 */
data class PsychologicalGoalRecommendation(
    val goal: Goal,
    val relatedNeed: SubjectiveNeed,
    val recommendationReason: String,
    val expectedSatisfaction: Float,
    val priority: Int,
    val psychologicalValue: String
)
