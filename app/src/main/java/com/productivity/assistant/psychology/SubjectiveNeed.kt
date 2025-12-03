package com.productivity.assistant.psychology

import java.util.Date

/**
 * 主体性需求 - 用户深层的心理需求
 * 
 * 主体性需求是用户内在的、主观的、动态变化的需求，
 * 不同于表面的行为目标，它反映了用户真正的心理动机和价值观
 */
data class SubjectiveNeed(
    val id: Long = 0,
    val category: NeedCategory,
    val intensity: Float, // 0.0-1.0，需求强度
    val description: String, // 需求描述
    val underlyingMotivation: String, // 底层动机
    val detectedDate: Date, // 检测到的时间
    val lastUpdated: Date, // 最后更新时间
    val changeTrend: ChangeTrend, // 变化趋势
    val relatedGoals: List<Long> = emptyList(), // 关联的目标ID
    val satisfactionLevel: Float = 0f, // 满足程度 0.0-1.0
    val priority: Int = 0 // 优先级 0-5
)

/**
 * 需求类别
 */
enum class NeedCategory {
    // 马斯洛需求层次理论 + 工作生活场景
    AUTONOMY,           // 自主性 - 希望掌控自己的工作生活
    COMPETENCE,         // 能力感 - 希望提升技能和能力
    RELATEDNESS,        // 归属感 - 希望与他人建立联系
    MEANING,            // 意义感 - 希望工作有意义
    GROWTH,             // 成长需求 - 希望持续成长
    BALANCE,            // 平衡需求 - 希望工作生活平衡
    RECOGNITION,        // 认可需求 - 希望被认可
    CREATIVITY,         // 创造力需求 - 希望创造性工作
    SECURITY,           // 安全感 - 希望稳定和可预测
    CHALLENGE           // 挑战需求 - 希望有挑战性任务
}

/**
 * 变化趋势
 */
enum class ChangeTrend {
    INCREASING,     // 需求在增强
    STABLE,         // 需求稳定
    DECREASING,     // 需求在减弱
    EMERGING,       // 新出现的需求
    FADING          // 正在消失的需求
}

/**
 * 心理需求分析结果
 */
data class PsychologicalProfile(
    val userId: String,
    val analyzedDate: Date,
    val dominantNeeds: List<SubjectiveNeed>, // 主导需求
    val emergingNeeds: List<SubjectiveNeed>, // 新兴需求
    val fadingNeeds: List<SubjectiveNeed>,   // 消退需求
    val needConflicts: List<NeedConflict>,   // 需求冲突
    val overallSatisfaction: Float,          // 整体满足度
    val recommendations: List<String>         // 建议
)

/**
 * 需求冲突
 */
data class NeedConflict(
    val need1: SubjectiveNeed,
    val need2: SubjectiveNeed,
    val conflictType: ConflictType,
    val description: String
)

enum class ConflictType {
    TIME_CONFLICT,      // 时间冲突
    RESOURCE_CONFLICT,  // 资源冲突
    VALUE_CONFLICT      // 价值观冲突
}
