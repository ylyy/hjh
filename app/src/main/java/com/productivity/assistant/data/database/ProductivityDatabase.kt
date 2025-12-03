package com.productivity.assistant.data.database

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.productivity.assistant.data.dao.AppUsageDao
import com.productivity.assistant.data.dao.GoalDao
import com.productivity.assistant.data.dao.AchievementDao
import com.productivity.assistant.data.entity.AppUsageRecord
import com.productivity.assistant.data.entity.Goal
import com.productivity.assistant.data.entity.Achievement

@Database(
    entities = [AppUsageRecord::class, Goal::class, Achievement::class],
    version = 1,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class ProductivityDatabase : RoomDatabase() {
    abstract fun appUsageDao(): AppUsageDao
    abstract fun goalDao(): GoalDao
    abstract fun achievementDao(): AchievementDao
}
