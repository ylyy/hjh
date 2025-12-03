package com.productivity.assistant.data.dao

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.*
import com.productivity.assistant.data.entity.Achievement
import kotlinx.coroutines.flow.Flow

@Dao
interface AchievementDao {
    @Query("SELECT * FROM achievements ORDER BY unlockedDate DESC")
    fun getAllAchievements(): Flow<List<Achievement>>
    
    @Query("SELECT * FROM achievements WHERE isUnlocked = 1")
    fun getUnlockedAchievements(): Flow<List<Achievement>>
    
    @Query("SELECT * FROM achievements WHERE type = :type")
    fun getAchievementsByType(type: com.productivity.assistant.data.entity.AchievementType): Flow<List<Achievement>>
    
    @Insert
    suspend fun insert(achievement: Achievement): Long
    
    @Update
    suspend fun update(achievement: Achievement)
    
    @Query("UPDATE achievements SET progress = :progress WHERE id = :id")
    suspend fun updateProgress(id: Long, progress: Int)
    
    @Query("UPDATE achievements SET isUnlocked = 1, unlockedDate = :date WHERE id = :id")
    suspend fun unlockAchievement(id: Long, date: java.util.Date)
}
