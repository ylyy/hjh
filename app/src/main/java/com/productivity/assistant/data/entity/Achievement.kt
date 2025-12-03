package com.productivity.assistant.data.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "achievements")
data class Achievement(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val description: String,
    val type: AchievementType,
    val unlockedDate: Date? = null,
    val progress: Int = 0,
    val target: Int,
    val isUnlocked: Boolean = false,
    val iconResId: Int = 0,
    val iconImagePath: String? = null // AI生成的图片路径
)

enum class AchievementType {
    WORK_STREAK,      // 连续工作
    EFFICIENCY,       // 效率
    SELF_DISCIPLINE,  // 自律
    GOAL_COMPLETION   // 目标完成
}
