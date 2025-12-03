package com.productivity.assistant.utils

import android.content.Context
import android.content.SharedPreferences

/**
 * 配置管理器 - 管理应用配置和用户设置
 */
class ConfigManager(context: Context) {
    
    private val prefs: SharedPreferences = context.getSharedPreferences(
        "productivity_assistant_prefs",
        Context.MODE_PRIVATE
    )
    
    // 娱乐应用列表
    fun getEntertainmentApps(): Set<String> {
        return prefs.getStringSet("entertainment_apps", emptySet()) ?: emptySet()
    }
    
    fun setEntertainmentApps(apps: Set<String>) {
        prefs.edit().putStringSet("entertainment_apps", apps).apply()
    }
    
    // 工作时段
    fun getWorkStartHour(): Int {
        return prefs.getInt("work_start_hour", 9)
    }
    
    fun getWorkEndHour(): Int {
        return prefs.getInt("work_end_hour", 18)
    }
    
    fun setWorkHours(startHour: Int, endHour: Int) {
        prefs.edit()
            .putInt("work_start_hour", startHour)
            .putInt("work_end_hour", endHour)
            .apply()
    }
    
    // 干预强度
    fun getInterventionLevel(): Int {
        return prefs.getInt("intervention_level", 2) // 0-低, 1-中, 2-高
    }
    
    fun setInterventionLevel(level: Int) {
        prefs.edit().putInt("intervention_level", level).apply()
    }
    
    // AI功能开关
    fun isAIEnabled(): Boolean {
        return prefs.getBoolean("ai_enabled", true)
    }
    
    fun setAIEnabled(enabled: Boolean) {
        prefs.edit().putBoolean("ai_enabled", enabled).apply()
    }
    
    // 提醒方式
    fun getReminderStyle(): Int {
        return prefs.getInt("reminder_style", 0) // 0-通知, 1-弹窗, 2-锁屏
    }
    
    fun setReminderStyle(style: Int) {
        prefs.edit().putInt("reminder_style", style).apply()
    }
    
    // 首次启动标记
    fun isFirstLaunch(): Boolean {
        return prefs.getBoolean("first_launch", true)
    }
    
    fun setFirstLaunch(isFirst: Boolean) {
        prefs.edit().putBoolean("first_launch", isFirst).apply()
    }
}
