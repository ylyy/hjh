package com.productivity.assistant.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.productivity.assistant.data.repository.AppUsageRepository
import com.productivity.assistant.data.repository.GoalRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import java.util.*

class MainViewModel : ViewModel() {
    
    private lateinit var appUsageRepository: AppUsageRepository
    private lateinit var goalRepository: GoalRepository
    
    private val _todayWorkTime = MutableStateFlow(0f)
    val todayWorkTime: StateFlow<Float> = _todayWorkTime.asStateFlow()
    
    private val _todayEntertainmentTime = MutableStateFlow(0f)
    val todayEntertainmentTime: StateFlow<Float> = _todayEntertainmentTime.asStateFlow()
    
    private val _completedGoalsCount = MutableStateFlow(0)
    val completedGoalsCount: StateFlow<Int> = _completedGoalsCount.asStateFlow()
    
    private val _currentStatus = MutableStateFlow("正在监控中...")
    val currentStatus: StateFlow<String> = _currentStatus.asStateFlow()
    
    fun setRepositories(
        appUsageRepository: AppUsageRepository,
        goalRepository: GoalRepository
    ) {
        this.appUsageRepository = appUsageRepository
        this.goalRepository = goalRepository
        refreshData()
    }
    
    fun refreshData() {
        viewModelScope.launch {
            loadTodayStats()
            loadGoalsStatus()
        }
    }
    
    private suspend fun loadTodayStats() {
        val calendar = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, 0)
            set(Calendar.MINUTE, 0)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }
        
        val todayStart = calendar.time
        val records = appUsageRepository.getRecordsBetween(todayStart, Date()).first()
        
        val workTime = records
            .filter { !it.isEntertainment }
            .sumOf { it.duration } / 1000 / 60 / 60f // 转换为小时
        
        val entertainmentTime = records
            .filter { it.isEntertainment }
            .sumOf { it.duration } / 1000 / 60 // 转换为分钟
        
        _todayWorkTime.value = workTime
        _todayEntertainmentTime.value = entertainmentTime
    }
    
    private suspend fun loadGoalsStatus() {
        val goals = goalRepository.getActiveGoals().first()
        val completed = goals.count { it.isCompleted }
        _completedGoalsCount.value = completed
        
        val total = goals.size
        if (total > 0) {
            _currentStatus.value = "已完成 $completed/$total 个目标"
        } else {
            _currentStatus.value = "暂无目标，快去设置吧！"
        }
    }
}
