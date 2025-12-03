import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('/api/dashboard')
      if (response.data.success) {
        setDashboardData(response.data.dashboard)
      }
    } catch (error) {
      console.error('获取仪表盘数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl">加载中...</div>
      </div>
    )
  }

  const productivityScore = dashboardData?.productivity_score || 0
  const activeGoals = dashboardData?.active_goals || 0
  const totalAchievements = dashboardData?.total_achievements || 0
  const weeklyHours = dashboardData?.weekly_entertainment_hours || 0

  return (
    <div className="space-y-6">
      {/* 标题 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">欢迎回来！</h2>
        <p className="text-gray-600">
          AI双Agent系统正在为您分析和优化生产力表现
        </p>
      </div>

      {/* 核心指标卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="生产力评分"
          value={productivityScore.toFixed(1)}
          unit="分"
          icon="📊"
          color="bg-blue-500"
        />
        <MetricCard
          title="活跃目标"
          value={activeGoals}
          unit="个"
          icon="🎯"
          color="bg-green-500"
        />
        <MetricCard
          title="解锁成就"
          value={totalAchievements}
          unit="个"
          icon="🏆"
          color="bg-yellow-500"
        />
        <MetricCard
          title="本周娱乐"
          value={weeklyHours.toFixed(1)}
          unit="小时"
          icon="⏱️"
          color="bg-purple-500"
        />
      </div>

      {/* Agent状态 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <AgentCard
          name="策划Agent"
          icon="🧠"
          status="工作中"
          description="正在分析您的行为模式，优化长期策略"
          tasks={[
            '✅ 完成本周行为分析',
            '🔄 生成今日策略',
            '📋 规划下周目标'
          ]}
        />
        <AgentCard
          name="导演Agent"
          icon="🎬"
          status="监控中"
          description="实时响应您的行为，在需要时提供干预"
          tasks={[
            '👀 监控应用使用',
            '💡 准备智能提醒',
            '🎯 追踪目标进度'
          ]}
        />
      </div>

      {/* 今日策略 */}
      {dashboardData?.today_strategy && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4 flex items-center">
            <span className="mr-2">📅</span>
            今日策略
          </h3>
          <div className="space-y-4">
            {dashboardData.today_strategy.focus_areas?.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">重点关注</h4>
                <div className="flex flex-wrap gap-2">
                  {dashboardData.today_strategy.focus_areas.map((area, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm"
                    >
                      {area}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {dashboardData.today_strategy.recommended_actions?.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">建议行动</h4>
                <ul className="space-y-2">
                  {dashboardData.today_strategy.recommended_actions.map((action, index) => (
                    <li key={index} className="flex items-start">
                      <span className="mr-2">💪</span>
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 快速操作 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold mb-4">快速操作</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ActionButton
            icon="➕"
            text="创建新目标"
            onClick={() => window.location.href = '/goals'}
          />
          <ActionButton
            icon="📈"
            text="查看分析报告"
            onClick={() => window.location.href = '/analytics'}
          />
          <ActionButton
            icon="⚙️"
            text="调整设置"
            onClick={() => window.location.href = '/settings'}
          />
        </div>
      </div>
    </div>
  )
}

function MetricCard({ title, value, unit, icon, color }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-gray-600 text-sm font-medium">{title}</h3>
        <span className="text-2xl">{icon}</span>
      </div>
      <div className="flex items-end">
        <span className="text-3xl font-bold text-gray-800">{value}</span>
        <span className="text-gray-500 ml-2 mb-1">{unit}</span>
      </div>
      <div className={`mt-3 h-2 ${color} rounded-full opacity-20`}></div>
    </div>
  )
}

function AgentCard({ name, icon, status, description, tasks }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <span className="text-3xl mr-3">{icon}</span>
          <div>
            <h3 className="text-lg font-bold">{name}</h3>
            <span className="text-sm text-green-600 flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
              {status}
            </span>
          </div>
        </div>
      </div>
      <p className="text-gray-600 mb-4">{description}</p>
      <div className="space-y-2">
        {tasks.map((task, index) => (
          <div key={index} className="text-sm text-gray-700">
            {task}
          </div>
        ))}
      </div>
    </div>
  )
}

function ActionButton({ icon, text, onClick }) {
  return (
    <button
      onClick={onClick}
      className="flex items-center justify-center p-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg hover:from-purple-600 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
    >
      <span className="text-2xl mr-3">{icon}</span>
      <span className="font-medium">{text}</span>
    </button>
  )
}

export default Dashboard
