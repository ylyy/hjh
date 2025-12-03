package com.productivity.assistant.data.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "app_usage_records")
data class AppUsageRecord(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val packageName: String,
    val appName: String,
    val startTime: Date,
    val endTime: Date? = null,
    val duration: Long, // 毫秒
    val isEntertainment: Boolean = false,
    val category: AppCategory = AppCategory.OTHER
)

enum class AppCategory {
    ENTERTAINMENT, // 娱乐
    SOCIAL,        // 社交
    PRODUCTIVITY,  // 生产力
    EDUCATION,     // 教育
    OTHER          // 其他
}
