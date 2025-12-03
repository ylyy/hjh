package com.productivity.assistant.ai

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Base64
import com.productivity.assistant.ai.modelscope.ModelScopeClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream

/**
 * AI服务 - 封装AI能力，为Agent系统提供统一接口
 */
class AIService(private val context: Context) {
    
    private val modelScopeClient = ModelScopeClient()
    
    /**
     * 生成个性化提醒内容
     */
    suspend fun generatePersonalizedReminder(
        userName: String = "用户",
        entertainmentTime: Int,
        workTime: Float,
        incompleteGoals: List<String>,
        emotionState: String
    ): String {
        val prompt = """
            你是一个智能工作生活助手。用户已经使用娱乐应用${entertainmentTime}分钟了。
            今日工作时长：${workTime}小时
            未完成的目标：${incompleteGoals.joinToString("、")}
            用户当前情绪状态：${emotionState}
            
            请生成一段温和但有效的提醒内容，鼓励用户回到工作中。
            要求：
            1. 语气友好、鼓励性
            2. 不超过50字
            3. 提及用户的成就（如果有）
            4. 提醒未完成的目标
        """.trimIndent()
        
        return modelScopeClient.generateText(
            prompt = prompt,
            maxTokens = 100,
            temperature = 0.8
        ).getOrElse {
            // 如果AI生成失败，使用默认模板
            generateDefaultReminder(entertainmentTime, workTime, incompleteGoals.size)
        }
    }
    
    /**
     * 生成目标建议
     */
    suspend fun generateGoalSuggestions(
        workHistory: String,
        currentGoals: List<String>,
        userPreferences: String
    ): List<String> {
        val prompt = """
            基于以下信息，为用户生成3-5个工作生活目标建议：
            
            工作历史：$workHistory
            当前目标：${currentGoals.joinToString("、")}
            用户偏好：$userPreferences
            
            请生成具体、可量化的目标建议，每个建议不超过20字。
            格式：每行一个建议，直接输出建议内容。
        """.trimIndent()
        
        val result = modelScopeClient.generateText(
            prompt = prompt,
            maxTokens = 200,
            temperature = 0.7
        ).getOrElse { "" }
        
        return result.split("\n")
            .map { it.trim() }
            .filter { it.isNotEmpty() && !it.startsWith("1.") && !it.startsWith("2.") && !it.startsWith("3.") }
            .take(5)
    }
    
    /**
     * 生成成就徽章图片
     */
    suspend fun generateAchievementBadge(
        achievementName: String,
        achievementDescription: String
    ): Bitmap? {
        val prompt = """
            设计一个成就徽章图标，主题：$achievementName
            描述：$achievementDescription
            风格：简洁、现代、有成就感
            尺寸：512x512像素，圆形徽章
        """.trimIndent()
        
        val result = modelScopeClient.generateImage(
            prompt = prompt,
            width = 512,
            height = 512
        )
        
        return result.getOrNull()?.firstOrNull()?.let { imageData ->
            decodeBase64Image(imageData)
        }
    }
    
    /**
     * 生成个性化工作建议
     */
    suspend fun generateWorkAdvice(
        currentTime: String,
        workEfficiency: Float,
        recentPatterns: String
    ): String {
        val prompt = """
            你是一个工作效率专家。基于以下信息，给用户一个简短的工作建议：
            
            当前时间：$currentTime
            工作效率：${(workEfficiency * 100).toInt()}%
            最近模式：$recentPatterns
            
            请给出一个实用的建议，不超过30字。
        """.trimIndent()
        
        return modelScopeClient.generateText(
            prompt = prompt,
            maxTokens = 50,
            temperature = 0.7
        ).getOrElse {
            "保持专注，继续努力！"
        }
    }
    
    /**
     * 生成文本用于分析（内部方法）
     */
    suspend fun generateTextForAnalysis(prompt: String): String {
        return modelScopeClient.generateText(
            prompt = prompt,
            maxTokens = 1000,
            temperature = 0.7
        ).getOrElse { "" }
    }
    
    /**
     * 分析用户情绪并生成建议
     */
    suspend fun analyzeEmotionAndAdvise(
        appUsagePattern: String,
        workCompletionRate: Float,
        stressIndicators: String
    ): String {
        val prompt = """
            分析用户的工作生活状态并给出建议：
            
            应用使用模式：$appUsagePattern
            工作完成率：${(workCompletionRate * 100).toInt()}%
            压力指标：$stressIndicators
            
            请分析用户当前状态，并给出一个鼓励性的建议（不超过40字）。
        """.trimIndent()
        
        return modelScopeClient.generateText(
            prompt = prompt,
            maxTokens = 100,
            temperature = 0.8
        ).getOrElse {
            "状态不错，继续保持！"
        }
    }
    
    /**
     * 生成默认提醒（AI失败时的后备方案）
     */
    private fun generateDefaultReminder(
        entertainmentTime: Int,
        workTime: Float,
        incompleteGoalsCount: Int
    ): String {
        return when {
            workTime > 0 -> "今天已完成${workTime.toInt()}小时工作，很棒！还有$incompleteGoalsCount 个目标待完成，继续加油！"
            incompleteGoalsCount > 0 -> "你已经使用娱乐应用${entertainmentTime}分钟了，还有$incompleteGoalsCount 个目标未完成，该回到工作啦！"
            else -> "已经玩了${entertainmentTime}分钟，记得工作哦~"
        }
    }
    
    /**
     * 解码Base64图片
     */
    private fun decodeBase64Image(base64String: String): Bitmap? {
        return try {
            // 移除可能的数据URL前缀
            val base64Data = if (base64String.contains(",")) {
                base64String.substringAfter(",")
            } else {
                base64String
            }
            
            val imageBytes = Base64.decode(base64Data, Base64.DEFAULT)
            BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)
        } catch (e: Exception) {
            null
        }
    }
}
