package com.productivity.assistant.data.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "goals")
data class Goal(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val description: String? = null,
    val type: GoalType,
    val targetValue: Int,
    val currentValue: Int = 0,
    val unit: String, // 如 "小时", "个任务"
    val startDate: Date,
    val endDate: Date? = null,
    val isCompleted: Boolean = false,
    val priority: Int = 0 // 0-5, 5最高
)

enum class GoalType {
    DAILY,   // 每日目标
    WEEKLY,  // 每周目标
    MONTHLY, // 每月目标
    CUSTOM   // 自定义
}
