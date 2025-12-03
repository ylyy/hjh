package com.productivity.assistant.data.dao

import androidx.room.*
import com.productivity.assistant.data.entity.AppUsageRecord
import kotlinx.coroutines.flow.Flow
import java.util.Date

@Dao
interface AppUsageDao {
    @Query("SELECT * FROM app_usage_records ORDER BY startTime DESC")
    fun getAllRecords(): Flow<List<AppUsageRecord>>
    
    @Query("SELECT * FROM app_usage_records WHERE startTime >= :startDate AND startTime <= :endDate")
    fun getRecordsBetween(startDate: Date, endDate: Date): Flow<List<AppUsageRecord>>
    
    @Query("SELECT * FROM app_usage_records WHERE isEntertainment = 1 AND startTime >= :startDate")
    fun getEntertainmentRecords(startDate: Date): Flow<List<AppUsageRecord>>
    
    @Query("SELECT SUM(duration) FROM app_usage_records WHERE isEntertainment = 1 AND startTime >= :startDate")
    suspend fun getTotalEntertainmentTime(startDate: Date): Long?
    
    @Query("SELECT * FROM app_usage_records WHERE packageName = :packageName ORDER BY startTime DESC LIMIT 1")
    suspend fun getLatestRecord(packageName: String): AppUsageRecord?
    
    @Insert
    suspend fun insert(record: AppUsageRecord): Long
    
    @Update
    suspend fun update(record: AppUsageRecord)
    
    @Delete
    suspend fun delete(record: AppUsageRecord)
}
