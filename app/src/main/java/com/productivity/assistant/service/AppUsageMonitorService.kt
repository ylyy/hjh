package com.productivity.assistant.service

import android.app.usage.UsageStats
import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.os.Build
import androidx.annotation.RequiresApi
import androidx.core.app.NotificationCompat
import com.productivity.assistant.ProductivityApplication
import com.productivity.assistant.R
import com.productivity.assistant.data.entity.AppCategory
import com.productivity.assistant.data.entity.AppUsageRecord
import com.productivity.assistant.data.repository.AppUsageRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import java.util.*
import java.util.concurrent.TimeUnit

@RequiresApi(Build.VERSION_CODES.LOLLIPOP_MR1)
class AppUsageMonitorService : ForegroundService() {
    
    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private lateinit var usageStatsManager: UsageStatsManager
    private lateinit var packageManager: PackageManager
    private lateinit var repository: AppUsageRepository
    
    private var currentPackage: String? = null
    private var currentStartTime: Long = 0
    private val checkInterval = 2000L // 2秒检查一次
    
    private val entertainmentApps = mutableSetOf<String>()
    
    override fun onCreate() {
        super.onCreate()
        usageStatsManager = getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager
        packageManager = packageManager
        repository = AppUsageRepository((application as ProductivityApplication).database.appUsageDao())
        
        loadEntertainmentApps()
        startMonitoring()
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, createNotification())
        return START_STICKY
    }
    
    private fun createNotification() = NotificationCompat.Builder(this, CHANNEL_ID)
        .setContentTitle("工作生活助手运行中")
        .setContentText("正在监控应用使用情况")
        .setSmallIcon(R.drawable.ic_notification)
        .setOngoing(true)
        .build()
    
    private fun startMonitoring() {
        serviceScope.launch {
            while (true) {
                checkCurrentApp()
                kotlinx.coroutines.delay(checkInterval)
            }
        }
    }
    
    private suspend fun checkCurrentApp() {
        val currentTime = System.currentTimeMillis()
        val stats = usageStatsManager.queryUsageStats(
            UsageStatsManager.INTERVAL_BEST,
            currentTime - TimeUnit.MINUTES.toMillis(5),
            currentTime
        )
        
        if (stats.isNullOrEmpty()) return
        
        // 获取最近使用的应用
        val recentStats = stats.maxByOrNull { it.lastTimeUsed }
        val topPackage = recentStats?.packageName ?: return
        
        if (topPackage != currentPackage) {
            // 应用切换了
            if (currentPackage != null) {
                // 保存上一个应用的使用记录
                saveAppUsage(currentPackage!!, currentStartTime, currentTime)
            }
            
            // 开始新的应用使用记录
            currentPackage = topPackage
            currentStartTime = recentStats.lastTimeUsed
            
            // 检查是否是娱乐应用
            if (isEntertainmentApp(topPackage)) {
                notifyEntertainmentAppOpened(topPackage)
            }
        }
    }
    
    private suspend fun saveAppUsage(packageName: String, startTime: Long, endTime: Long) {
        try {
            val appName = getAppName(packageName)
            val duration = endTime - startTime
            val isEntertainment = isEntertainmentApp(packageName)
            val category = getAppCategory(packageName)
            
            val record = AppUsageRecord(
                packageName = packageName,
                appName = appName,
                startTime = Date(startTime),
                endTime = Date(endTime),
                duration = duration,
                isEntertainment = isEntertainment,
                category = category
            )
            
            repository.insertRecord(record)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    private fun getAppName(packageName: String): String {
        return try {
            val appInfo = packageManager.getApplicationInfo(packageName, 0)
            packageManager.getApplicationLabel(appInfo).toString()
        } catch (e: Exception) {
            packageName
        }
    }
    
    private fun isEntertainmentApp(packageName: String): Boolean {
        return entertainmentApps.contains(packageName) || 
               isEntertainmentByCategory(packageName)
    }
    
    private fun isEntertainmentByCategory(packageName: String): Boolean {
        return try {
            val appInfo = packageManager.getApplicationInfo(packageName, 0)
            val category = appInfo.category
            category == ApplicationInfo.CATEGORY_GAME ||
            category == ApplicationInfo.CATEGORY_VIDEO ||
            category == ApplicationInfo.CATEGORY_MUSIC
        } catch (e: Exception) {
            false
        }
    }
    
    private fun getAppCategory(packageName: String): AppCategory {
        return try {
            val appInfo = packageManager.getApplicationInfo(packageName, 0)
            when (appInfo.category) {
                ApplicationInfo.CATEGORY_GAME,
                ApplicationInfo.CATEGORY_VIDEO,
                ApplicationInfo.CATEGORY_MUSIC -> AppCategory.ENTERTAINMENT
                ApplicationInfo.CATEGORY_SOCIAL -> AppCategory.SOCIAL
                ApplicationInfo.CATEGORY_PRODUCTIVITY -> AppCategory.PRODUCTIVITY
                ApplicationInfo.CATEGORY_EDUCATION -> AppCategory.EDUCATION
                else -> AppCategory.OTHER
            }
        } catch (e: Exception) {
            AppCategory.OTHER
        }
    }
    
    private fun loadEntertainmentApps() {
        // 从SharedPreferences加载用户配置的娱乐应用列表
        val prefs = getSharedPreferences("app_settings", Context.MODE_PRIVATE)
        val apps = prefs.getStringSet("entertainment_apps", emptySet())
        entertainmentApps.addAll(apps ?: emptySet())
    }
    
    private fun notifyEntertainmentAppOpened(packageName: String) {
        // 通知AI Agent系统
        val intent = Intent(ACTION_ENTERTAINMENT_APP_OPENED).apply {
            putExtra(EXTRA_PACKAGE_NAME, packageName)
        }
        sendBroadcast(intent)
    }
    
    companion object {
        const val CHANNEL_ID = "app_usage_monitor_channel"
        const val NOTIFICATION_ID = 1001
        const val ACTION_ENTERTAINMENT_APP_OPENED = "com.productivity.assistant.ENTERTAINMENT_APP_OPENED"
        const val EXTRA_PACKAGE_NAME = "package_name"
    }
}
