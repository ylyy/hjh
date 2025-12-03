package com.productivity.assistant.agent

import android.content.Context
import com.productivity.assistant.data.entity.Goal
import com.productivity.assistant.data.entity.GoalType
import com.productivity.assistant.data.repository.GoalRepository
import com.productivity.assistant.psychology.*
import kotlinx.coroutines.flow.first
import java.util.*
import kotlin.math.max

/**
 * 增强的策划Agent - 基于主体性需求的目标管理
 * 
 * 核心能力：
 * 1. 理解用户的主体性需求（深层心理需求）
 * 2. 根据需求变化动态调整目标
 * 3. 生成与心理需求对齐的目标
 * 4. 追踪目标对需求满足的贡献
 */
class EnhancedPlannerAgent(
    private val context: Context,
    private val goalRepository: GoalRepository,
    private val needAnalyzer: SubjectiveNeedAnalyzer
) {
    
    /**
     * 基于主体性需求生成心理目标建议
     */
    suspend fun generatePsychologicalGoalRecommendations(): List<PsychologicalGoalRecommendation> {
        // 1. 分析当前的主体性需求
        val profile = needAnalyzer.analyzeSubjectiveNeeds()
        
        // 2. 获取现有目标
        val existingGoals = goalRepository.getActiveGoals().first()
        
        // 3. 为每个主导需求生成目标建议
        val recommendations = mutableListOf<PsychologicalGoalRecommendation>()
        
        profile.dominantNeeds.forEach { need ->
            val goalSuggestions = generateGoalsForNeed(need, existingGoals, profile)
            recommendations.addAll(goalSuggestions)
        }
        
        // 4. 处理新兴需求
        profile.emergingNeeds.forEach { need ->
            val goalSuggestions = generateGoalsForNeed(need, existingGoals, profile)
            recommendations.addAll(goalSuggestions)
        }
        
        // 5. 处理需求冲突
        profile.needConflicts.forEach { conflict ->
            val resolutionGoals = generateConflictResolutionGoals(conflict, existingGoals)
            recommendations.addAll(resolutionGoals)
        }
        
        // 6. 按优先级和预期满足度排序
        return recommendations.sortedByDescending { 
            it.priority * 10 + (it.expectedSatisfaction * 10).toInt()
        }
    }
    
    /**
     * 为特定需求生成目标建议
     */
    private suspend fun generateGoalsForNeed(
        need: SubjectiveNeed,
        existingGoals: List<Goal>,
        profile: PsychologicalProfile
    ): List<PsychologicalGoalRecommendation> {
        val recommendations = mutableListOf<PsychologicalGoalRecommendation>()
        
        // 检查是否已有满足该需求的目标
        val existingGoalsForNeed = existingGoals.filter { goal ->
            isGoalAlignedWithNeed(goal, need)
        }
        
        // 如果已有目标且满足度足够，不生成新建议
        if (existingGoalsForNeed.isNotEmpty() && 
            need.satisfactionLevel > 0.6f) {
            return emptyList()
        }
        
        // 根据需求类型生成目标
        val goals = when (need.category) {
            NeedCategory.AUTONOMY -> generateAutonomyGoals(need)
            NeedCategory.COMPETENCE -> generateCompetenceGoals(need)
            NeedCategory.BALANCE -> generateBalanceGoals(need)
            NeedCategory.GROWTH -> generateGrowthGoals(need)
            NeedCategory.MEANING -> generateMeaningGoals(need)
            NeedCategory.RELATEDNESS -> generateRelatednessGoals(need)
            NeedCategory.CREATIVITY -> generateCreativityGoals(need)
            NeedCategory.CHALLENGE -> generateChallengeGoals(need)
            NeedCategory.SECURITY -> generateSecurityGoals(need)
            NeedCategory.RECOGNITION -> generateRecognitionGoals(need)
        }
        
        goals.forEach { goal ->
            recommendations.add(
                PsychologicalGoalRecommendation(
                    goal = goal,
                    relatedNeed = need,
                    recommendationReason = buildRecommendationReason(need, goal),
                    expectedSatisfaction = calculateExpectedSatisfaction(goal, need),
                    priority = need.priority,
                    psychologicalValue = buildPsychologicalValue(need, goal)
                )
            )
        }
        
        return recommendations
    }
    
    /**
     * 生成自主性目标
     */
    private fun generateAutonomyGoals(need: SubjectiveNeed): List<Goal> {
        return listOf(
            Goal(
                title = "自主安排工作时间",
                description = "每天至少2小时可以自主安排的工作时间",
                type = GoalType.DAILY,
                targetValue = 2,
                unit = "小时",
                startDate = Date(),
                priority = need.priority
            ),
            Goal(
                title = "减少被动任务",
                description = "将被动任务比例降低到30%以下",
                type = GoalType.WEEKLY,
                targetValue = 30,
                unit = "%",
                startDate = Date(),
                priority = need.priority
            )
        )
    }
    
    /**
     * 生成能力感目标
     */
    private fun generateCompetenceGoals(need: SubjectiveNeed): List<Goal> {
        return listOf(
            Goal(
                title = "提升核心技能",
                description = "每周学习新技能或提升现有技能",
                type = GoalType.WEEKLY,
                targetValue = 1,
                unit = "项",
                startDate = Date(),
                priority = need.priority
            ),
            Goal(
                title = "提高目标完成率",
                description = "将目标完成率提升到80%以上",
                type = GoalType.MONTHLY,
                targetValue = 80,
                unit = "%",
                startDate = Date(),
                priority = need.priority
            )
        )
    }
    
    /**
     * 生成平衡目标
     */
    private fun generateBalanceGoals(need: SubjectiveNeed): List<Goal> {
        return listOf(
            Goal(
                title = "工作生活平衡",
                description = "每天娱乐时间控制在2小时以内",
                type = GoalType.DAILY,
                targetValue = 2,
                unit = "小时",
                startDate = Date(),
                priority = need.priority
            ),
            Goal(
                title = "规律作息",
                description = "保持规律的作息时间",
                type = GoalType.DAILY,
                targetValue = 1,
                unit = "项",
                startDate = Date(),
                priority = need.priority
            )
        )
    }
    
    /**
     * 生成成长目标
     */
    private fun generateGrowthGoals(need: SubjectiveNeed): List<Goal> {
        return listOf(
            Goal(
                title = "持续学习",
                description = "每周完成至少3个学习任务",
                type = GoalType.WEEKLY,
                targetValue = 3,
                unit = "个",
                startDate = Date(),
                priority = need.priority
            )
        )
    }
    
    /**
     * 生成意义感目标
     */
    private fun generateMeaningGoals(need: SubjectiveNeed): List<Goal> {
        return listOf(
            Goal(
                title = "有意义的工作",
                description = "每天至少完成1个有意义的工作任务",
                type = GoalType.DAILY,
                targetValue = 1,
                unit = "个",
                startDate = Date(),
                priority = need.priority
            )
        )
    }
    
    /**
     * 生成归属感目标
     */
    private fun generateRelatednessGoals(need: SubjectiveNeed): List<Goal> {
        return listOf(
            Goal(
                title = "社交互动",
                description = "每周至少2次有意义的社交互动",
                type = GoalType.WEEKLY,
                targetValue = 2,
                unit = "次",
                startDate = Date(),
                priority = need.priority
            )
        )
    }
    
    /**
     * 生成创造力目标
     */
    private fun generateCreativityGoals(need: SubjectiveNeed): List<Goal> {
        return listOf(
            Goal(
                title = "创造性工作",
                description = "每周至少完成1个创造性项目",
                type = GoalType.WEEKLY,
                targetValue = 1,
                unit = "个",
                startDate = Date(),
                priority = need.priority
            )
        )
    }
    
    /**
     * 生成挑战目标
     */
    private fun generateChallengeGoals(need: SubjectiveNeed): List<Goal> {
        return listOf(
            Goal(
                title = "挑战性任务",
                description = "每周完成至少1个有挑战性的任务",
                type = GoalType.WEEKLY,
                targetValue = 1,
                unit = "个",
                startDate = Date(),
                priority = need.priority
            )
        )
    }
    
    /**
     * 生成安全感目标
     */
    private fun generateSecurityGoals(need: SubjectiveNeed): List<Goal> {
        return listOf(
            Goal(
                title = "稳定工作节奏",
                description = "保持稳定的每日工作时间",
                type = GoalType.DAILY,
                targetValue = 1,
                unit = "项",
                startDate = Date(),
                priority = need.priority
            )
        )
    }
    
    /**
     * 生成认可目标
     */
    private fun generateRecognitionGoals(need: SubjectiveNeed): List<Goal> {
        return listOf(
            Goal(
                title = "展示成果",
                description = "每周至少展示1个工作成果",
                type = GoalType.WEEKLY,
                targetValue = 1,
                unit = "次",
                startDate = Date(),
                priority = need.priority
            )
        )
    }
    
    /**
     * 生成冲突解决目标
     */
    private suspend fun generateConflictResolutionGoals(
        conflict: NeedConflict,
        existingGoals: List<Goal>
    ): List<PsychologicalGoalRecommendation> {
        // 为冲突生成平衡目标
        val resolutionGoal = when (conflict.conflictType) {
            ConflictType.TIME_CONFLICT -> Goal(
                title = "平衡${conflict.need1.category}和${conflict.need2.category}",
                description = "寻找时间分配的平衡点",
                type = GoalType.DAILY,
                targetValue = 1,
                unit = "项",
                startDate = Date(),
                priority = max(conflict.need1.priority, conflict.need2.priority)
            )
            ConflictType.VALUE_CONFLICT -> Goal(
                title = "整合${conflict.need1.category}和${conflict.need2.category}",
                description = "寻找价值观的整合方式",
                type = GoalType.WEEKLY,
                targetValue = 1,
                unit = "项",
                startDate = Date(),
                priority = max(conflict.need1.priority, conflict.need2.priority)
            )
            else -> null
        }
        
        return resolutionGoal?.let {
            listOf(
                PsychologicalGoalRecommendation(
                    goal = it,
                    relatedNeed = conflict.need1,
                    recommendationReason = "解决需求冲突：${conflict.description}",
                    expectedSatisfaction = 0.6f,
                    priority = max(conflict.need1.priority, conflict.need2.priority),
                    psychologicalValue = "平衡和整合不同需求"
                )
            )
        } ?: emptyList()
    }
    
    /**
     * 检查目标是否与需求对齐
     */
    private fun isGoalAlignedWithNeed(goal: Goal, need: SubjectiveNeed): Boolean {
        // 简化的对齐检查逻辑
        return when (need.category) {
            NeedCategory.AUTONOMY -> goal.title.contains("自主") || goal.title.contains("安排")
            NeedCategory.COMPETENCE -> goal.title.contains("技能") || goal.title.contains("能力") || goal.title.contains("提升")
            NeedCategory.BALANCE -> goal.title.contains("平衡") || goal.title.contains("娱乐")
            NeedCategory.GROWTH -> goal.title.contains("学习") || goal.title.contains("成长")
            NeedCategory.MEANING -> goal.title.contains("意义") || goal.description.contains("意义")
            else -> false
        }
    }
    
    /**
     * 构建推荐理由
     */
    private fun buildRecommendationReason(need: SubjectiveNeed, goal: Goal): String {
        return "基于您的${need.description}（强度${(need.intensity * 100).toInt()}%），" +
               "建议设置目标：${goal.title}，这将帮助您${need.underlyingMotivation}"
    }
    
    /**
     * 计算预期满足度
     */
    private fun calculateExpectedSatisfaction(goal: Goal, need: SubjectiveNeed): Float {
        // 基于目标类型和需求强度计算预期满足度
        val baseSatisfaction = need.intensity * 0.7f
        val goalTypeMultiplier = when (goal.type) {
            GoalType.DAILY -> 0.8f
            GoalType.WEEKLY -> 0.9f
            GoalType.MONTHLY -> 1.0f
            else -> 0.7f
        }
        return (baseSatisfaction * goalTypeMultiplier).coerceIn(0f, 1f)
    }
    
    /**
     * 构建心理价值描述
     */
    private fun buildPsychologicalValue(need: SubjectiveNeed, goal: Goal): String {
        return "完成此目标将满足您的${need.description}，" +
               "帮助您${need.underlyingMotivation}，" +
               "带来更深层的心理满足感"
    }
    
    /**
     * 动态调整现有目标以适应需求变化
     */
    suspend fun adaptGoalsToNeeds(): List<GoalAdaptation> {
        val profile = needAnalyzer.analyzeSubjectiveNeeds()
        val existingGoals = goalRepository.getActiveGoals().first()
        val adaptations = mutableListOf<GoalAdaptation>()
        
        existingGoals.forEach { goal ->
            // 检查目标是否仍与当前需求对齐
            val relatedNeeds = profile.dominantNeeds.filter { isGoalAlignedWithNeed(goal, it) }
            
            if (relatedNeeds.isEmpty()) {
                // 目标不再与任何需求对齐，可能需要调整
                val newGoal = adaptGoalToCurrentNeeds(goal, profile)
                if (newGoal != null) {
                    adaptations.add(
                        GoalAdaptation(
                            date = Date(),
                            reason = AdaptationReason.NEED_INTENSITY_CHANGED,
                            oldValue = goal.title,
                            newValue = newGoal.title,
                            needChange = null
                        )
                    )
                }
            } else {
                // 检查需求强度变化
                relatedNeeds.forEach { need ->
                    if (need.changeTrend == ChangeTrend.DECREASING && need.intensity < 0.3f) {
                        // 需求正在消退，可能需要调整目标
                        adaptations.add(
                            GoalAdaptation(
                                date = Date(),
                                reason = AdaptationReason.NEED_FADED,
                                oldValue = goal.title,
                                newValue = "${goal.title}（需求减弱，建议调整）",
                                needChange = need
                            )
                        )
                    }
                }
            }
        }
        
        return adaptations
    }
    
    /**
     * 将目标适应到当前需求
     */
    private fun adaptGoalToCurrentNeeds(
        goal: Goal,
        profile: PsychologicalProfile
    ): Goal? {
        // 找到最相关的需求
        val mostRelevantNeed = profile.dominantNeeds.maxByOrNull { it.priority }
        
        return mostRelevantNeed?.let { need ->
            // 根据需求调整目标
            goal.copy(
                title = "${goal.title}（适应${need.description}）",
                priority = need.priority
            )
        }
    }
}
