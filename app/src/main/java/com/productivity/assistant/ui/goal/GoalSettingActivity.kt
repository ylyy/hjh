package com.productivity.assistant.ui.goal

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.productivity.assistant.ProductivityApplication
import com.productivity.assistant.agent.PlannerAgent
import com.productivity.assistant.data.entity.GoalType
import com.productivity.assistant.data.repository.GoalRepository
import kotlinx.coroutines.launch

class GoalSettingActivity : AppCompatActivity() {
    
    private lateinit var goalRepository: GoalRepository
    private lateinit var plannerAgent: PlannerAgent
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val database = (application as ProductivityApplication).database
        goalRepository = GoalRepository(database.goalDao())
        plannerAgent = PlannerAgent(this, goalRepository)
        
        // TODO: 设置布局和UI
        // 这里可以添加目标设置的UI界面
    }
}
