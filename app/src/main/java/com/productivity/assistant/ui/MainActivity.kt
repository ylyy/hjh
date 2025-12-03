package com.productivity.assistant.ui

import android.Manifest
import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import com.productivity.assistant.ProductivityApplication
import com.productivity.assistant.R
import com.productivity.assistant.agent.DirectorAgent
import com.productivity.assistant.agent.EmotionAgent
import com.productivity.assistant.agent.PlannerAgent
import com.productivity.assistant.data.repository.AppUsageRepository
import com.productivity.assistant.data.repository.GoalRepository
import com.productivity.assistant.databinding.ActivityMainBinding
import com.productivity.assistant.service.AppUsageMonitorService
import com.productivity.assistant.service.ReminderService
import com.productivity.assistant.ui.goal.GoalSettingActivity
import com.productivity.assistant.ui.permission.PermissionActivity
import com.productivity.assistant.ui.statistics.StatisticsActivity
import com.productivity.assistant.ui.viewmodel.MainViewModel
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MainViewModel
    
    private lateinit var plannerAgent: PlannerAgent
    private lateinit var directorAgent: DirectorAgent
    private lateinit var emotionAgent: EmotionAgent
    
    private val usageStatsPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) {
        checkPermissionsAndStartService()
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupViewModel()
        setupAgents()
        setupUI()
        checkPermissionsAndStartService()
    }
    
    private fun setupViewModel() {
        val database = (application as ProductivityApplication).database
        val appUsageRepository = AppUsageRepository(database.appUsageDao())
        val goalRepository = GoalRepository(database.goalDao())
        
        viewModel = ViewModelProvider(this)[MainViewModel::class.java].apply {
            setRepositories(appUsageRepository, goalRepository)
        }
        
        // 观察数据
        lifecycleScope.launch {
            viewModel.todayWorkTime.collect { time ->
                binding.tvWorkTime.text = "${time.toInt()} 小时"
            }
        }
        
        lifecycleScope.launch {
            viewModel.todayEntertainmentTime.collect { time ->
                binding.tvEntertainmentTime.text = "${time.toInt()} 分钟"
            }
        }
        
        lifecycleScope.launch {
            viewModel.completedGoalsCount.collect { count ->
                binding.tvGoalsCompleted.text = "$count 个"
            }
        }
        
        lifecycleScope.launch {
            viewModel.currentStatus.collect { status ->
                binding.tvCurrentStatus.text = status
            }
        }
    }
    
    private fun setupAgents() {
        val database = (application as ProductivityApplication).database
        val appUsageRepository = AppUsageRepository(database.appUsageDao())
        val goalRepository = GoalRepository(database.goalDao())
        val reminderService = ReminderService(this)
        
        plannerAgent = PlannerAgent(this, goalRepository)
        directorAgent = DirectorAgent(this, appUsageRepository, goalRepository, reminderService)
        emotionAgent = EmotionAgent(this, appUsageRepository, goalRepository)
    }
    
    private fun setupUI() {
        binding.btnSetGoals.setOnClickListener {
            startActivity(Intent(this, GoalSettingActivity::class.java))
        }
        
        binding.btnStatistics.setOnClickListener {
            startActivity(Intent(this, StatisticsActivity::class.java))
        }
        
        binding.btnSettings.setOnClickListener {
            // TODO: 打开设置页面
        }
        
        // 刷新数据
        binding.swipeRefresh.setOnRefreshListener {
            viewModel.refreshData()
            binding.swipeRefresh.isRefreshing = false
        }
    }
    
    private fun checkPermissionsAndStartService() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP_MR1) {
            if (!hasUsageStatsPermission()) {
                requestUsageStatsPermission()
                return
            }
        }
        
        // 启动监控服务
        startMonitorService()
    }
    
    private fun hasUsageStatsPermission(): Boolean {
        val appOps = getSystemService(Context.APP_OPS_SERVICE) as android.app.AppOpsManager
        val mode = appOps.checkOpNoThrow(
            android.app.AppOpsManager.OPSTR_GET_USAGE_STATS,
            android.os.Process.myUid(),
            packageName
        )
        return mode == android.app.AppOpsManager.MODE_ALLOWED
    }
    
    private fun requestUsageStatsPermission() {
        val intent = Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS)
        usageStatsPermissionLauncher.launch(intent)
    }
    
    private fun startMonitorService() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP_MR1) {
            val intent = Intent(this, AppUsageMonitorService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(intent)
            } else {
                startService(intent)
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        directorAgent.cleanup()
    }
}
