package com.productivity.assistant.data.repository

import com.productivity.assistant.data.dao.AppUsageDao
import com.productivity.assistant.data.entity.AppUsageRecord
import kotlinx.coroutines.flow.Flow
import java.util.Date

class AppUsageRepository(private val dao: AppUsageDao) {
    
    fun getAllRecords(): Flow<List<AppUsageRecord>> = dao.getAllRecords()
    
    fun getRecordsBetween(startDate: Date, endDate: Date): Flow<List<AppUsageRecord>> {
        return dao.getRecordsBetween(startDate, endDate)
    }
    
    fun getEntertainmentRecords(startDate: Date): Flow<List<AppUsageRecord>> {
        return dao.getEntertainmentRecords(startDate)
    }
    
    suspend fun getTotalEntertainmentTime(startDate: Date): Long {
        return dao.getTotalEntertainmentTime(startDate) ?: 0L
    }
    
    suspend fun getLatestRecord(packageName: String): AppUsageRecord? {
        return dao.getLatestRecord(packageName)
    }
    
    suspend fun insertRecord(record: AppUsageRecord): Long {
        return dao.insert(record)
    }
    
    suspend fun updateRecord(record: AppUsageRecord) {
        dao.update(record)
    }
    
    suspend fun deleteRecord(record: AppUsageRecord) {
        dao.delete(record)
    }
}
