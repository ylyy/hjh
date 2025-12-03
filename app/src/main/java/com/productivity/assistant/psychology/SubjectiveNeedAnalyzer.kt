package com.productivity.assistant.psychology

import android.content.Context
import com.productivity.assistant.ai.AIService
import com.productivity.assistant.data.entity.AppUsageRecord
import com.productivity.assistant.data.entity.Goal
import com.productivity.assistant.data.repository.AppUsageRepository
import com.productivity.assistant.data.repository.GoalRepository
import kotlinx.coroutines.flow.first
import java.util.*
import kotlin.math.max
import kotlin.math.min

/**
 * 主体性需求分析器
 * 
 * 通过分析用户的行为模式、目标设置、应用使用等数据，
 * 识别和理解用户的深层心理需求（主体性需求）
 */
class SubjectiveNeedAnalyzer(
    private val context: Context,
    private val appUsageRepository: AppUsageRepository,
    private val goalRepository: GoalRepository
) {
    
    private val aiService = AIService(context)
    
    /**
     * 分析用户的主体性需求
     */
    suspend fun analyzeSubjectiveNeeds(
        timeWindow: Int = 30 // 分析最近N天的数据
    ): PsychologicalProfile {
        val calendar = Calendar.getInstance().apply {
            add(Calendar.DAY_OF_YEAR, -timeWindow)
        }
        val startDate = calendar.time
        
        // 收集数据
        val appUsageRecords = appUsageRepository.getRecordsBetween(startDate, Date()).first()
        val goals = goalRepository.getGoalsBetween(startDate, Date()).first()
        val completedGoals = goals.filter { it.isCompleted }
        
        // 分析行为模式
        val behaviorPattern = analyzeBehaviorPattern(appUsageRecords, goals)
        
        // 使用AI深度分析心理需求
        val aiAnalysis = analyzeWithAI(behaviorPattern, goals, completedGoals)
        
        // 检测需求变化趋势
        val needHistory = getNeedHistory(timeWindow)
        val changeTrends = detectChangeTrends(aiAnalysis, needHistory)
        
        // 识别需求冲突
        val conflicts = identifyConflicts(aiAnalysis)
        
        // 计算整体满足度
        val satisfaction = calculateOverallSatisfaction(aiAnalysis, completedGoals, goals)
        
        // 生成建议
        val recommendations = generateRecommendations(aiAnalysis, conflicts, satisfaction)
        
        return PsychologicalProfile(
            userId = "current_user", // TODO: 从用户系统获取
            analyzedDate = Date(),
            dominantNeeds = aiAnalysis.filter { it.intensity > 0.7f }.sortedByDescending { it.priority },
            emergingNeeds = changeTrends.filter { it.changeTrend == ChangeTrend.EMERGING },
            fadingNeeds = changeTrends.filter { it.changeTrend == ChangeTrend.FADING },
            needConflicts = conflicts,
            overallSatisfaction = satisfaction,
            recommendations = recommendations
        )
    }
    
    /**
     * 分析行为模式
     */
    private fun analyzeBehaviorPattern(
        records: List<AppUsageRecord>,
        goals: List<Goal>
    ): BehaviorPattern {
        val totalWorkTime = records.filter { !it.isEntertainment }
            .sumOf { it.duration } / 1000 / 60 / 60f // 转换为小时
        
        val totalEntertainmentTime = records.filter { it.isEntertainment }
            .sumOf { it.duration } / 1000 / 60 / 60f
        
        val appSwitchFrequency = records.size
        val socialAppUsage = records.filter { it.category == com.productivity.assistant.data.entity.AppCategory.SOCIAL }
            .sumOf { it.duration } / 1000 / 60 / 60f
        
        val goalCompletionRate = if (goals.isNotEmpty()) {
            goals.count { it.isCompleted }.toFloat() / goals.size
        } else 0f
        
        val workTimeVariability = calculateVariability(records.filter { !it.isEntertainment })
        val entertainmentTimeVariability = calculateVariability(records.filter { it.isEntertainment })
        
        return BehaviorPattern(
            totalWorkTime = totalWorkTime,
            totalEntertainmentTime = totalEntertainmentTime,
            appSwitchFrequency = appSwitchFrequency,
            socialAppUsage = socialAppUsage,
            goalCompletionRate = goalCompletionRate,
            workTimeVariability = workTimeVariability,
            entertainmentTimeVariability = entertainmentTimeVariability,
            preferredWorkTime = findPreferredWorkTime(records),
            goalTypes = goals.map { it.type.name }
        )
    }
    
    /**
     * 使用AI深度分析心理需求
     */
    private suspend fun analyzeWithAI(
        behaviorPattern: BehaviorPattern,
        goals: List<Goal>,
        completedGoals: List<Goal>
    ): List<SubjectiveNeed> {
        val prompt = buildAIAnalysisPrompt(behaviorPattern, goals, completedGoals)
        
        val aiResult = try {
            aiService.generateTextForAnalysis(prompt)
        } catch (e: Exception) {
            ""
        }
        
        return parseAIAnalysis(aiResult, behaviorPattern)
    }
    
    /**
     * 构建AI分析提示词
     */
    private fun buildAIAnalysisPrompt(
        pattern: BehaviorPattern,
        goals: List<Goal>,
        completedGoals: List<Goal>
    ): String {
        return """
            你是一个专业的心理学分析专家。请分析用户的行为数据，识别用户的深层心理需求（主体性需求）。
            
            行为数据：
            - 总工作时间：${pattern.totalWorkTime}小时
            - 娱乐时间：${pattern.totalEntertainmentTime}小时
            - 应用切换频率：${pattern.appSwitchFrequency}次
            - 社交应用使用：${pattern.socialAppUsage}小时
            - 目标完成率：${(pattern.goalCompletionRate * 100).toInt()}%
            - 工作时间变异性：${pattern.workTimeVariability}
            - 偏好工作时间：${pattern.preferredWorkTime}
            
            目标设置：
            - 总目标数：${goals.size}
            - 已完成：${completedGoals.size}
            - 目标类型：${pattern.goalTypes.joinToString("、")}
            
            请分析用户可能的主体性需求，包括：
            1. 自主性需求（AUTONOMY）- 希望掌控自己的工作生活
            2. 能力感需求（COMPETENCE）- 希望提升技能和能力
            3. 归属感需求（RELATEDNESS）- 希望与他人建立联系
            4. 意义感需求（MEANING）- 希望工作有意义
            5. 成长需求（GROWTH）- 希望持续成长
            6. 平衡需求（BALANCE）- 希望工作生活平衡
            7. 认可需求（RECOGNITION）- 希望被认可
            8. 创造力需求（CREATIVITY）- 希望创造性工作
            9. 安全感需求（SECURITY）- 希望稳定和可预测
            10. 挑战需求（CHALLENGE）- 希望有挑战性任务
            
            请为每个需求评估：
            - 需求强度（0.0-1.0）
            - 底层动机
            - 优先级（0-5）
            
            格式：每行一个需求，格式为：需求类别|强度|底层动机|优先级
            例如：AUTONOMY|0.8|希望自主安排工作时间，不受外部干扰|4
        """.trimIndent()
    }
    
    /**
     * 解析AI分析结果
     */
    private fun parseAIAnalysis(
        aiResult: String,
        behaviorPattern: BehaviorPattern
    ): List<SubjectiveNeed> {
        val needs = mutableListOf<SubjectiveNeed>()
        val lines = aiResult.split("\n").filter { it.isNotBlank() }
        
        lines.forEach { line ->
            try {
                val parts = line.split("|")
                if (parts.size >= 4) {
                    val category = NeedCategory.valueOf(parts[0].trim())
                    val intensity = parts[1].trim().toFloat().coerceIn(0f, 1f)
                    val motivation = parts[2].trim()
                    val priority = parts[3].trim().toInt().coerceIn(0, 5)
                    
                    // 根据行为模式调整需求强度
                    val adjustedIntensity = adjustIntensityByBehavior(category, intensity, behaviorPattern)
                    
                    needs.add(
                        SubjectiveNeed(
                            category = category,
                            intensity = adjustedIntensity,
                            description = generateDescription(category, adjustedIntensity),
                            underlyingMotivation = motivation,
                            detectedDate = Date(),
                            lastUpdated = Date(),
                            changeTrend = ChangeTrend.STABLE,
                            priority = priority
                        )
                    )
                }
            } catch (e: Exception) {
                // 忽略解析错误
            }
        }
        
        // 如果AI没有返回结果，使用基于规则的分析
        if (needs.isEmpty()) {
            needs.addAll(ruleBasedAnalysis(behaviorPattern))
        }
        
        return needs
    }
    
    /**
     * 基于规则的分析（AI失败时的后备方案）
     */
    private fun ruleBasedAnalysis(pattern: BehaviorPattern): List<SubjectiveNeed> {
        val needs = mutableListOf<SubjectiveNeed>()
        
        // 工作时间长但完成率低 -> 能力感需求
        if (pattern.totalWorkTime > 6 && pattern.goalCompletionRate < 0.5) {
            needs.add(createNeed(NeedCategory.COMPETENCE, 0.7f, "希望提升工作效率和能力"))
        }
        
        // 工作时间变异性高 -> 自主性需求
        if (pattern.workTimeVariability > 0.5) {
            needs.add(createNeed(NeedCategory.AUTONOMY, 0.6f, "希望自主安排工作时间"))
        }
        
        // 社交应用使用多 -> 归属感需求
        if (pattern.socialAppUsage > 2) {
            needs.add(createNeed(NeedCategory.RELATEDNESS, 0.7f, "希望与他人建立联系"))
        }
        
        // 娱乐时间多 -> 平衡需求
        if (pattern.totalEntertainmentTime > 3) {
            needs.add(createNeed(NeedCategory.BALANCE, 0.8f, "希望工作生活平衡"))
        }
        
        // 目标完成率高 -> 成长需求
        if (pattern.goalCompletionRate > 0.8) {
            needs.add(createNeed(NeedCategory.GROWTH, 0.7f, "希望持续成长和进步"))
        }
        
        return needs
    }
    
    private fun createNeed(
        category: NeedCategory,
        intensity: Float,
        motivation: String
    ): SubjectiveNeed {
        return SubjectiveNeed(
            category = category,
            intensity = intensity,
            description = generateDescription(category, intensity),
            underlyingMotivation = motivation,
            detectedDate = Date(),
            lastUpdated = Date(),
            changeTrend = ChangeTrend.STABLE,
            priority = (intensity * 5).toInt()
        )
    }
    
    private fun generateDescription(category: NeedCategory, intensity: Float): String {
        return when (category) {
            NeedCategory.AUTONOMY -> "自主性需求（${(intensity * 100).toInt()}%）"
            NeedCategory.COMPETENCE -> "能力感需求（${(intensity * 100).toInt()}%）"
            NeedCategory.RELATEDNESS -> "归属感需求（${(intensity * 100).toInt()}%）"
            NeedCategory.MEANING -> "意义感需求（${(intensity * 100).toInt()}%）"
            NeedCategory.GROWTH -> "成长需求（${(intensity * 100).toInt()}%）"
            NeedCategory.BALANCE -> "平衡需求（${(intensity * 100).toInt()}%）"
            NeedCategory.RECOGNITION -> "认可需求（${(intensity * 100).toInt()}%）"
            NeedCategory.CREATIVITY -> "创造力需求（${(intensity * 100).toInt()}%）"
            NeedCategory.SECURITY -> "安全感需求（${(intensity * 100).toInt()}%）"
            NeedCategory.CHALLENGE -> "挑战需求（${(intensity * 100).toInt()}%）"
        }
    }
    
    /**
     * 根据行为模式调整需求强度
     */
    private fun adjustIntensityByBehavior(
        category: NeedCategory,
        baseIntensity: Float,
        pattern: BehaviorPattern
    ): Float {
        return when (category) {
            NeedCategory.AUTONOMY -> {
                baseIntensity * (1 + pattern.workTimeVariability * 0.3f)
            }
            NeedCategory.COMPETENCE -> {
                baseIntensity * (1 + (1 - pattern.goalCompletionRate) * 0.3f)
            }
            NeedCategory.BALANCE -> {
                baseIntensity * (1 + min(pattern.totalEntertainmentTime / 5f, 0.3f))
            }
            else -> baseIntensity
        }.coerceIn(0f, 1f)
    }
    
    /**
     * 检测需求变化趋势
     */
    private suspend fun detectChangeTrends(
        currentNeeds: List<SubjectiveNeed>,
        history: List<SubjectiveNeed>
    ): List<SubjectiveNeed> {
        return currentNeeds.map { currentNeed ->
            val historicalNeed = history.find { it.category == currentNeed.category }
            
            val trend = when {
                historicalNeed == null -> ChangeTrend.EMERGING
                currentNeed.intensity > historicalNeed.intensity + 0.2f -> ChangeTrend.INCREASING
                currentNeed.intensity < historicalNeed.intensity - 0.2f -> ChangeTrend.DECREASING
                currentNeed.intensity < 0.3f -> ChangeTrend.FADING
                else -> ChangeTrend.STABLE
            }
            
            currentNeed.copy(changeTrend = trend)
        }
    }
    
    /**
     * 识别需求冲突
     */
    private fun identifyConflicts(needs: List<SubjectiveNeed>): List<NeedConflict> {
        val conflicts = mutableListOf<NeedConflict>()
        
        // 自主性 vs 安全感
        val autonomy = needs.find { it.category == NeedCategory.AUTONOMY }
        val security = needs.find { it.category == NeedCategory.SECURITY }
        if (autonomy != null && security != null && 
            autonomy.intensity > 0.7f && security.intensity > 0.7f) {
            conflicts.add(
                NeedConflict(
                    need1 = autonomy,
                    need2 = security,
                    conflictType = ConflictType.VALUE_CONFLICT,
                    description = "自主性需求与安全感需求存在冲突：希望自主但又需要稳定"
                )
            )
        }
        
        // 挑战 vs 平衡
        val challenge = needs.find { it.category == NeedCategory.CHALLENGE }
        val balance = needs.find { it.category == NeedCategory.BALANCE }
        if (challenge != null && balance != null &&
            challenge.intensity > 0.7f && balance.intensity > 0.7f) {
            conflicts.add(
                NeedConflict(
                    need1 = challenge,
                    need2 = balance,
                    conflictType = ConflictType.TIME_CONFLICT,
                    description = "挑战需求与平衡需求存在冲突：希望挑战但需要平衡"
                )
            )
        }
        
        return conflicts
    }
    
    /**
     * 计算整体满足度
     */
    private fun calculateOverallSatisfaction(
        needs: List<SubjectiveNeed>,
        completedGoals: List<Goal>,
        allGoals: List<Goal>
    ): Float {
        val needSatisfaction = needs.map { it.satisfactionLevel }.average().toFloat()
        val goalSatisfaction = if (allGoals.isNotEmpty()) {
            completedGoals.size.toFloat() / allGoals.size
        } else 0.5f
        
        return (needSatisfaction * 0.6f + goalSatisfaction * 0.4f).coerceIn(0f, 1f)
    }
    
    /**
     * 生成建议
     */
    private suspend fun generateRecommendations(
        needs: List<SubjectiveNeed>,
        conflicts: List<NeedConflict>,
        satisfaction: Float
    ): List<String> {
        val recommendations = mutableListOf<String>()
        
        // 基于主导需求生成建议
        needs.filter { it.intensity > 0.7f }.forEach { need ->
            recommendations.add(generateNeedBasedRecommendation(need))
        }
        
        // 基于冲突生成建议
        conflicts.forEach { conflict ->
            recommendations.add("注意需求冲突：${conflict.description}，建议寻找平衡点")
        }
        
        // 基于满足度生成建议
        if (satisfaction < 0.5f) {
            recommendations.add("整体满足度较低，建议重新审视目标和需求")
        }
        
        return recommendations
    }
    
    private fun generateNeedBasedRecommendation(need: SubjectiveNeed): String {
        return when (need.category) {
            NeedCategory.AUTONOMY -> "建议设置更灵活的工作时间安排，增强自主性"
            NeedCategory.COMPETENCE -> "建议设置技能提升目标，增强能力感"
            NeedCategory.BALANCE -> "建议合理分配工作和娱乐时间，保持平衡"
            NeedCategory.GROWTH -> "建议设置长期成长目标，持续进步"
            else -> "建议关注${need.description}，满足${need.underlyingMotivation}"
        }
    }
    
    // 辅助方法
    private fun calculateVariability(records: List<AppUsageRecord>): Float {
        if (records.isEmpty()) return 0f
        val durations = records.map { it.duration.toFloat() }
        val mean = durations.average().toFloat()
        val variance = durations.map { (it - mean) * (it - mean) }.average().toFloat()
        return (variance / mean).coerceIn(0f, 1f)
    }
    
    private fun findPreferredWorkTime(records: List<AppUsageRecord>): String {
        // 简化实现：返回工作时间最多的时段
        return "9:00-12:00" // TODO: 实际分析
    }
    
    private suspend fun getNeedHistory(days: Int): List<SubjectiveNeed> {
        // TODO: 从数据库获取历史需求数据
        return emptyList()
    }
    
}

/**
 * 行为模式数据
 */
data class BehaviorPattern(
    val totalWorkTime: Float,
    val totalEntertainmentTime: Float,
    val appSwitchFrequency: Int,
    val socialAppUsage: Float,
    val goalCompletionRate: Float,
    val workTimeVariability: Float,
    val entertainmentTimeVariability: Float,
    val preferredWorkTime: String,
    val goalTypes: List<String>
)
