package com.productivity.assistant.data.dao

import androidx.room.*
import com.productivity.assistant.data.entity.Goal
import kotlinx.coroutines.flow.Flow
import java.util.Date

@Dao
interface GoalDao {
    @Query("SELECT * FROM goals ORDER BY priority DESC, startDate DESC")
    fun getAllGoals(): Flow<List<Goal>>
    
    @Query("SELECT * FROM goals WHERE isCompleted = 0 ORDER BY priority DESC")
    fun getActiveGoals(): Flow<List<Goal>>
    
    @Query("SELECT * FROM goals WHERE id = :id")
    suspend fun getGoalById(id: Long): Goal?
    
    @Query("SELECT * FROM goals WHERE startDate >= :startDate AND startDate <= :endDate")
    fun getGoalsBetween(startDate: Date, endDate: Date): Flow<List<Goal>>
    
    @Insert
    suspend fun insert(goal: Goal): Long
    
    @Update
    suspend fun update(goal: Goal)
    
    @Delete
    suspend fun delete(goal: Goal)
    
    @Query("UPDATE goals SET currentValue = :value WHERE id = :id")
    suspend fun updateProgress(id: Long, value: Int)
}
