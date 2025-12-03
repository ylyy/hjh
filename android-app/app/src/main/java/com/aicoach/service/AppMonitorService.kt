package com.aicoach.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.app.usage.UsageStats
import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.util.Log
import androidx.core.app.NotificationCompat
import com.aicoach.network.ApiClient
import com.aicoach.network.AppOpenEvent
import kotlinx.coroutines.*
import java.util.*

/**
 * 应用监控服务 - 核心监控组件
 * 
 * 功能:
 * 1. 后台监控用户打开的应用
 * 2. 识别娱乐类应用
 * 3. 实时上报到后端AI系统
 * 4. 显示AI干预提醒
 */
class AppMonitorService : Service() {

    companion object {
        private const val TAG = "AppMonitorService"
        private const val CHANNEL_ID = "app_monitor_channel"
        private const val NOTIFICATION_ID = 1001
        private const val CHECK_INTERVAL = 2000L // 2秒检查一次
    }

    private val handler = Handler(Looper.getMainLooper())
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    private var lastForegroundApp: String? = null
    private var isMonitoring = false

    private val entertainmentApps = setOf(
        "com.tencent.tmgp.sgame",  // 王者荣耀
        "com.tencent.mm",           // 微信
        "com.ss.android.ugc.aweme", // 抖音
        "com.tencent.qqlive",       // 腾讯视频
        "com.youku.phone",          // 优酷
        "tv.danmaku.bili",          // 哔哩哔哩
        "com.taobao.taobao",        // 淘宝
        "com.jd.jdmobile",          // 京东
        // 添加更多娱乐应用包名
    )

    private val categoryMap = mapOf(
        "游戏" to listOf("sgame", "game", "play"),
        "社交" to listOf("mm", "qq", "weibo", "twitter", "facebook"),
        "视频" to listOf("video", "tv", "bili", "youku", "iqiyi"),
        "购物" to listOf("taobao", "jd", "shopping", "mall")
    )

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "监控服务创建")
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, createNotification("AI生产力教练正在运行..."))
        
        if (!isMonitoring) {
            startMonitoring()
        }
        
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "应用监控",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "监控应用使用情况"
                setShowBadge(false)
            }

            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(content: String): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("AI生产力教练")
            .setContentText(content)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .build()
    }

    private fun startMonitoring() {
        isMonitoring = true
        Log.d(TAG, "开始监控应用使用")
        
        handler.post(object : Runnable {
            override fun run() {
                checkForegroundApp()
                if (isMonitoring) {
                    handler.postDelayed(this, CHECK_INTERVAL)
                }
            }
        })
    }

    private fun checkForegroundApp() {
        try {
            val currentApp = getForegroundApp()
            
            if (currentApp != null && currentApp != lastForegroundApp) {
                lastForegroundApp = currentApp
                
                // 判断是否为娱乐应用
                if (isEntertainmentApp(currentApp)) {
                    val appName = getAppName(currentApp)
                    val category = getAppCategory(currentApp)
                    
                    Log.d(TAG, "检测到娱乐应用: $appName ($category)")
                    
                    // 上报到后端AI系统
                    reportToBackend(appName, category)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "检查前台应用失败", e)
        }
    }

    private fun getForegroundApp(): String? {
        val usageStatsManager = getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager
        val currentTime = System.currentTimeMillis()
        
        val stats = usageStatsManager.queryUsageStats(
            UsageStatsManager.INTERVAL_DAILY,
            currentTime - 1000 * 10,  // 最近10秒
            currentTime
        )

        if (stats.isEmpty()) {
            Log.w(TAG, "无法获取使用统计，请检查权限")
            return null
        }

        // 找到最近使用的应用
        val sortedStats = stats.sortedByDescending { it.lastTimeUsed }
        return sortedStats.firstOrNull()?.packageName
    }

    private fun isEntertainmentApp(packageName: String): Boolean {
        // 检查是否在预定义的娱乐应用列表中
        if (entertainmentApps.contains(packageName)) {
            return true
        }
        
        // 根据包名特征判断
        val lowerPackage = packageName.lowercase()
        return categoryMap.values.flatten().any { keyword ->
            lowerPackage.contains(keyword)
        }
    }

    private fun getAppCategory(packageName: String): String {
        val lowerPackage = packageName.lowercase()
        
        for ((category, keywords) in categoryMap) {
            if (keywords.any { lowerPackage.contains(it) }) {
                return category
            }
        }
        
        return "娱乐"  // 默认分类
    }

    private fun getAppName(packageName: String): String {
        return try {
            val packageManager = applicationContext.packageManager
            val appInfo = packageManager.getApplicationInfo(packageName, 0)
            packageManager.getApplicationLabel(appInfo).toString()
        } catch (e: Exception) {
            packageName
        }
    }

    private fun reportToBackend(appName: String, category: String) {
        serviceScope.launch {
            try {
                val event = AppOpenEvent(
                    appName = appName,
                    appCategory = category,
                    timestamp = System.currentTimeMillis()
                )
                
                val response = ApiClient.apiService.reportAppOpened(event)
                
                if (response.success) {
                    // 处理AI干预响应
                    val intervention = response.intervention
                    if (intervention?.action != "observe") {
                        // 显示干预通知
                        withContext(Dispatchers.Main) {
                            showInterventionNotification(intervention)
                        }
                    }
                }
                
                Log.d(TAG, "事件上报成功: $appName")
            } catch (e: Exception) {
                Log.e(TAG, "事件上报失败", e)
            }
        }
    }

    private fun showInterventionNotification(intervention: Map<String, Any>?) {
        if (intervention == null) return
        
        val title = intervention["title"] as? String ?: "提醒"
        val message = intervention["message"] as? String ?: "记得完成今日目标！"
        
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(message)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setVibrate(longArrayOf(0, 500, 200, 500))
            .build()

        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify((System.currentTimeMillis() % 10000).toInt(), notification)
    }

    override fun onDestroy() {
        super.onDestroy()
        isMonitoring = false
        handler.removeCallbacksAndMessages(null)
        serviceScope.cancel()
        Log.d(TAG, "监控服务销毁")
    }
}
