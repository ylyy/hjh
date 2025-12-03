package com.productivity.assistant.agent

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import com.productivity.assistant.ai.AIService
import com.productivity.assistant.data.entity.Goal
import com.productivity.assistant.data.repository.AppUsageRepository
import com.productivity.assistant.data.repository.GoalRepository
import com.productivity.assistant.service.AppUsageMonitorService
import com.productivity.assistant.service.ReminderService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import java.util.*
import java.util.concurrent.TimeUnit

/**
 * 导演Agent - 负责实时行为控制和协调
 * 
 * 职责：
 * 1. 实时监控应用使用情况
 * 2. 执行策划Agent制定的策略
 * 3. 控制提醒时机和方式
 * 4. 协调所有系统行为
 */
class DirectorAgent(
    private val context: Context,
    private val appUsageRepository: AppUsageRepository,
    private val goalRepository: GoalRepository,
    private val reminderService: ReminderService
) {
    
    private val aiService = AIService(context)
    
    private val scope = CoroutineScope(Dispatchers.Default)
    private var entertainmentStartTime: Long = 0
    private var currentEntertainmentPackage: String? = null
    
    // 干预级别配置
    private val interventionLevels = mapOf(
        5L to InterventionLevel.MILD,      // 5分钟 - 温和提醒
        15L to InterventionLevel.MODERATE, // 15分钟 - 强化提醒
        30L to InterventionLevel.STRONG,   // 30分钟 - 强制干预
        60L to InterventionLevel.STRICT    // 60分钟 - 深度干预
    )
    
    init {
        registerBroadcastReceiver()
    }
    
    private fun registerBroadcastReceiver() {
        val filter = IntentFilter(AppUsageMonitorService.ACTION_ENTERTAINMENT_APP_OPENED)
        context.registerReceiver(entertainmentAppReceiver, filter)
    }
    
    private val entertainmentAppReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val packageName = intent?.getStringExtra(AppUsageMonitorService.EXTRA_PACKAGE_NAME)
            packageName?.let { handleEntertainmentAppOpened(it) }
        }
    }
    
    /**
     * 处理娱乐应用打开事件
     */
    private fun handleEntertainmentAppOpened(packageName: String) {
        scope.launch {
            if (currentEntertainmentPackage != packageName) {
                // 切换了娱乐应用
                if (currentEntertainmentPackage != null) {
                    // 重置之前的计时
                    entertainmentStartTime = System.currentTimeMillis()
                } else {
                    // 第一次打开娱乐应用
                    entertainmentStartTime = System.currentTimeMillis()
                }
                currentEntertainmentPackage = packageName
            }
            
            // 检查是否需要干预
            checkAndIntervene()
        }
    }
    
    /**
     * 检查并执行干预
     */
    private suspend fun checkAndIntervene() {
        val currentTime = System.currentTimeMillis()
        val duration = currentTime - entertainmentStartTime
        val durationMinutes = TimeUnit.MILLISECONDS.toMinutes(duration)
        
        // 检查是否达到干预阈值
        interventionLevels.forEach { (threshold, level) ->
            if (durationMinutes >= threshold) {
                executeIntervention(level, durationMinutes)
                return@forEach
            }
        }
        
        // 定期检查（每5分钟）
        if (durationMinutes % 5 == 0L && durationMinutes > 0) {
            executeIntervention(InterventionLevel.MILD, durationMinutes)
        }
    }
    
    /**
     * 执行干预策略
     */
    private suspend fun executeIntervention(level: InterventionLevel, durationMinutes: Long) {
        val activeGoals = goalRepository.getActiveGoals().first()
        val incompleteGoals = activeGoals.filter { !it.isCompleted }
        val todayWorkTime = getTodayWorkTime()
        val goalTitles = incompleteGoals.map { it.title }
        
        when (level) {
            InterventionLevel.MILD -> {
                // 温和提醒 - 使用AI生成个性化内容
                reminderService.showMildReminder(
                    durationMinutes = durationMinutes.toInt(),
                    incompleteGoalsCount = incompleteGoals.size,
                    workTime = todayWorkTime,
                    incompleteGoals = goalTitles,
                    emotionState = "正常"
                )
            }
            InterventionLevel.MODERATE -> {
                // 强化提醒 + 成就展示
                val todayWorkTime = getTodayWorkTime()
                reminderService.showModerateReminder(
                    durationMinutes = durationMinutes.toInt(),
                    workHours = todayWorkTime,
                    incompleteGoalsCount = incompleteGoals.size
                )
            }
            InterventionLevel.STRONG -> {
                // 强制干预 - 显示工作目标
                reminderService.showStrongIntervention(
                    durationMinutes = durationMinutes.toInt(),
                    goals = incompleteGoals.take(3) // 显示前3个目标
                )
            }
            InterventionLevel.STRICT -> {
                // 深度干预 - 需要完成任务才能继续
                reminderService.showStrictIntervention(
                    durationMinutes = durationMinutes.toInt(),
                    goals = incompleteGoals
                )
            }
        }
    }
    
    /**
     * 获取今日工作时长（小时）
     */
    private suspend fun getTodayWorkTime(): Float {
        val calendar = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, 0)
            set(Calendar.MINUTE, 0)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }
        
        val todayStart = calendar.time
        val records = appUsageRepository.getRecordsBetween(todayStart, Date())
            .first()
            .filter { !it.isEntertainment }
        
        val totalMinutes = records.sumOf { it.duration } / 1000 / 60
        return totalMinutes / 60f
    }
    
    /**
     * 重置娱乐应用计时
     */
    fun resetEntertainmentTimer() {
        entertainmentStartTime = 0
        currentEntertainmentPackage = null
    }
    
    fun cleanup() {
        try {
            context.unregisterReceiver(entertainmentAppReceiver)
        } catch (e: Exception) {
            // 可能已经注销
        }
    }
}

enum class InterventionLevel {
    MILD,      // 温和提醒
    MODERATE,  // 强化提醒
    STRONG,    // 强制干预
    STRICT     // 深度干预
}
