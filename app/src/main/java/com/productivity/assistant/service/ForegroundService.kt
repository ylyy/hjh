package com.productivity.assistant.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.os.Build
import androidx.core.app.NotificationCompat

abstract class ForegroundService : Service() {
    
    protected fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                getChannelId(),
                getChannelName(),
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = getChannelDescription()
            }
            
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }
    
    protected abstract fun getChannelId(): String
    protected abstract fun getChannelName(): String
    protected abstract fun getChannelDescription(): String
    protected abstract fun createNotification(): android.app.Notification
}
