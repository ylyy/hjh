import React, { useState, useEffect } from 'react'
import axios from 'axios'

function Goals() {
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    fetchGoals()
  }, [])

  const fetchGoals = async () => {
    try {
      const response = await axios.get('/api/goals/active')
      if (response.data.success) {
        setGoals(response.data.goals || [])
      }
    } catch (error) {
      console.error('获取目标失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const createGoal = async (goalData) => {
    try {
      const response = await axios.post('/api/goals', goalData)
      if (response.data.success) {
        setShowCreateModal(false)
        fetchGoals() // 刷新目标列表
      }
    } catch (error) {
      console.error('创建目标失败:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-12">加载中...</div>
  }

  return (
    <div className="space-y-6">
      {/* 标题和创建按钮 */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">目标管理</h2>
          <p className="text-gray-600 mt-1">设定目标，追踪进度，获得成就</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-purple-700 transition-colors shadow-md"
        >
          ➕ 创建新目标
        </button>
      </div>

      {/* 目标列表 */}
      {goals.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="text-6xl mb-4">🎯</div>
          <h3 className="text-xl font-bold mb-2">还没有目标</h3>
          <p className="text-gray-600 mb-6">创建您的第一个目标，开始提升生产力之旅！</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            立即创建
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {goals.map(goal => (
            <GoalCard key={goal.id} goal={goal} />
          ))}
        </div>
      )}

      {/* 创建目标模态框 */}
      {showCreateModal && (
        <CreateGoalModal
          onClose={() => setShowCreateModal(false)}
          onCreate={createGoal}
        />
      )}
    </div>
  )
}

function GoalCard({ goal }) {
  const progressColor = goal.progress >= 80 ? 'bg-green-500' : 
                        goal.progress >= 50 ? 'bg-yellow-500' : 'bg-red-500'

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-800">{goal.type}</h3>
          <p className="text-sm text-gray-500 mt-1">
            {goal.start_date} 至 {goal.end_date}
          </p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-primary">{goal.progress.toFixed(0)}%</div>
          <div className="text-xs text-gray-500">完成度</div>
        </div>
      </div>

      <p className="text-gray-600 mb-4">{goal.description}</p>

      {/* 进度条 */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>当前: {goal.current}</span>
          <span>目标: {goal.target}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`${progressColor} h-3 rounded-full transition-all duration-500`}
            style={{ width: `${Math.min(goal.progress, 100)}%` }}
          ></div>
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="flex space-x-3">
        <button className="flex-1 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
          查看详情
        </button>
        <button className="flex-1 py-2 bg-primary text-white rounded hover:bg-purple-700 transition-colors">
          更新进度
        </button>
      </div>
    </div>
  )
}

function CreateGoalModal({ onClose, onCreate }) {
  const [formData, setFormData] = useState({
    goal_type: '',
    target_value: '',
    duration_days: '7',
    description: ''
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onCreate({
      ...formData,
      target_value: parseFloat(formData.target_value),
      duration_days: parseInt(formData.duration_days)
    })
  }

  const goalTemplates = [
    { type: '减少游戏时间', target: 10, desc: '本周游戏时间控制在10小时以内' },
    { type: '增加工作时长', target: 40, desc: '本周工作时长达到40小时' },
    { type: '阅读打卡', target: 7, desc: '连续7天阅读打卡' },
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold">创建新目标</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {/* 模板选择 */}
        <div className="mb-6">
          <h4 className="font-semibold mb-3">快速模板</h4>
          <div className="grid grid-cols-3 gap-3">
            {goalTemplates.map((template, index) => (
              <button
                key={index}
                onClick={() => setFormData({
                  goal_type: template.type,
                  target_value: template.target.toString(),
                  duration_days: '7',
                  description: template.desc
                })}
                className="p-3 border-2 border-gray-200 rounded-lg hover:border-primary transition-colors text-left"
              >
                <div className="font-medium text-sm">{template.type}</div>
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              目标类型
            </label>
            <input
              type="text"
              value={formData.goal_type}
              onChange={(e) => setFormData({ ...formData, goal_type: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="例如: 减少游戏时间"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                目标值
              </label>
              <input
                type="number"
                value={formData.target_value}
                onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="10"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                持续天数
              </label>
              <select
                value={formData.duration_days}
                onChange={(e) => setFormData({ ...formData, duration_days: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="1">1天</option>
                <option value="7">7天</option>
                <option value="14">14天</option>
                <option value="30">30天</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              目标描述
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              rows="3"
              placeholder="详细描述您的目标..."
              required
            />
          </div>

          <div className="flex space-x-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              className="flex-1 py-3 bg-primary text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              创建目标
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Goals
