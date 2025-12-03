package com.productivity.assistant.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import com.productivity.assistant.R
import com.productivity.assistant.ai.AIService
import com.productivity.assistant.data.entity.Goal
import com.productivity.assistant.ui.MainActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

class ReminderService(private val context: Context) {
    
    private val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    private val aiService = AIService(context)
    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    
    init {
        createNotificationChannel()
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "工作提醒",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "工作生活助手的提醒通知"
            }
            notificationManager.createNotificationChannel(channel)
        }
    }
    
    /**
     * 温和提醒
     */
    fun showMildReminder(
        durationMinutes: Int,
        incompleteGoalsCount: Int,
        workTime: Float = 0f,
        incompleteGoals: List<String> = emptyList(),
        emotionState: String = "正常"
    ) {
        // 使用AI生成个性化提醒
        serviceScope.launch {
            val aiContent = aiService.generatePersonalizedReminder(
                entertainmentTime = durationMinutes,
                workTime = workTime,
                incompleteGoals = incompleteGoals,
                emotionState = emotionState
            )
            
            showNotification(
                title = context.getString(R.string.reminder_title),
                content = aiContent,
                priority = NotificationCompat.PRIORITY_DEFAULT
            )
        }
        
        // 如果AI生成失败，使用默认内容
        val defaultContent = context.getString(
            R.string.reminder_entertainment_time,
            durationMinutes
        )
        showNotification(
            title = context.getString(R.string.reminder_title),
            content = defaultContent,
            priority = NotificationCompat.PRIORITY_DEFAULT
        )
    }
    
    /**
     * 强化提醒
     */
    fun showModerateReminder(
        durationMinutes: Int,
        workHours: Float,
        incompleteGoalsCount: Int
    ) {
        val content = if (workHours > 0) {
            context.getString(R.string.reminder_achievement, workHours.toInt())
        } else {
            context.getString(R.string.reminder_work_goal, incompleteGoalsCount)
        }
        
        showNotification(
            title = "工作提醒",
            content = content,
            priority = NotificationCompat.PRIORITY_HIGH
        )
    }
    
    /**
     * 强制干预
     */
    fun showStrongIntervention(durationMinutes: Int, goals: List<Goal>) {
        val goalsText = goals.joinToString("\n") { "• ${it.title}" }
        val content = """
            你已经使用娱乐应用 $durationMinutes 分钟了
            未完成的目标：
            $goalsText
        """.trimIndent()
        
        showNotification(
            title = "需要专注工作",
            content = content,
            priority = NotificationCompat.PRIORITY_HIGH
        )
    }
    
    /**
     * 深度干预
     */
    fun showStrictIntervention(durationMinutes: Int, goals: List<Goal>) {
        val content = """
            你已经使用娱乐应用 $durationMinutes 分钟了
            建议先完成一个工作目标再继续
        """.trimIndent()
        
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_IMMUTABLE
        )
        
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setContentTitle("需要完成工作目标")
            .setContentText(content)
            .setSmallIcon(R.drawable.ic_notification)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setFullScreenIntent(pendingIntent, true)
            .build()
        
        notificationManager.notify(NOTIFICATION_ID_STRICT, notification)
    }
    
    private fun showNotification(
        title: String,
        content: String,
        priority: Int
    ) {
        val intent = Intent(context, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_IMMUTABLE
        )
        
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(content)
            .setSmallIcon(R.drawable.ic_notification)
            .setPriority(priority)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()
        
        notificationManager.notify(NOTIFICATION_ID_REMINDER, notification)
    }
    
    companion object {
        const val CHANNEL_ID = "reminder_channel"
        const val NOTIFICATION_ID_REMINDER = 2001
        const val NOTIFICATION_ID_STRICT = 2002
    }
}
