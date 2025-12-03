import React, { useState, useEffect } from 'react'
import axios from 'axios'

function Analytics() {
  const [analysis, setAnalysis] = useState(null)
  const [weeklyReport, setWeeklyReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState(7)

  useEffect(() => {
    fetchData()
  }, [timeRange])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [analysisRes, reportRes] = await Promise.all([
        axios.get(`/api/analysis/behavior?days=${timeRange}`),
        axios.get('/api/reports/weekly')
      ])
      
      if (analysisRes.data.success) {
        setAnalysis(analysisRes.data.analysis)
      }
      if (reportRes.data.success) {
        setWeeklyReport(reportRes.data.report)
      }
    } catch (error) {
      console.error('获取分析数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">加载中...</div>
  }

  return (
    <div className="space-y-6">
      {/* 标题和时间范围选择 */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">数据分析</h2>
          <p className="text-gray-600 mt-1">深入了解您的使用习惯和生产力趋势</p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(parseInt(e.target.value))}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
        >
          <option value="7">最近7天</option>
          <option value="14">最近14天</option>
          <option value="30">最近30天</option>
        </select>
      </div>

      {/* 生产力评分卡片 */}
      {analysis && (
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow-lg p-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl mb-2">生产力评分</h3>
              <div className="text-6xl font-bold">
                {analysis.productivity_score.toFixed(0)}
              </div>
              <p className="mt-2 opacity-90">
                {analysis.productivity_score >= 80 ? '优秀！' : 
                 analysis.productivity_score >= 60 ? '良好' : '需要改进'}
              </p>
            </div>
            <div className="text-right">
              <div className="mb-4">
                <div className="text-sm opacity-75">娱乐时间</div>
                <div className="text-2xl font-bold">
                  {analysis.total_entertainment_time.toFixed(1)}小时
                </div>
              </div>
              <div className="text-sm opacity-75">分析周期: {analysis.analysis_period}</div>
            </div>
          </div>
        </div>
      )}

      {/* 应用分类统计 */}
      {analysis?.category_breakdown && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">应用使用分类</h3>
          <div className="space-y-4">
            {Object.entries(analysis.category_breakdown).map(([category, stats]) => (
              <CategoryBar
                key={category}
                category={category}
                hours={(stats.total_duration / 3600).toFixed(1)}
                frequency={stats.frequency}
                totalHours={analysis.total_entertainment_time}
              />
            ))}
          </div>
        </div>
      )}

      {/* 问题应用警告 */}
      {analysis?.problematic_apps && analysis.problematic_apps.length > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-6">
          <div className="flex items-start">
            <span className="text-2xl mr-3">⚠️</span>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-red-800 mb-2">
                需要关注的应用
              </h3>
              <div className="space-y-2">
                {analysis.problematic_apps.map((app, index) => (
                  <div key={index} className="flex items-center justify-between bg-white p-3 rounded">
                    <div>
                      <span className="font-medium">{app.category}</span>
                      <span className="text-sm text-gray-600 ml-2">
                        使用{app.frequency}次
                      </span>
                    </div>
                    <span className="text-red-600 font-bold">
                      {app.hours.toFixed(1)}小时
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 周报总结 */}
      {weeklyReport && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">📊 本周总结</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-3xl font-bold text-green-600">
                {weeklyReport.completed_goals}
              </div>
              <div className="text-sm text-gray-600 mt-1">完成目标</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-3xl font-bold text-yellow-600">
                {weeklyReport.new_achievements}
              </div>
              <div className="text-sm text-gray-600 mt-1">新成就</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-3xl font-bold text-purple-600">
                {weeklyReport.productivity_score.toFixed(0)}
              </div>
              <div className="text-sm text-gray-600 mt-1">周平均分</div>
            </div>
          </div>

          {/* AI建议 */}
          {weeklyReport.recommendations && weeklyReport.recommendations.length > 0 && (
            <div>
              <h4 className="font-semibold mb-3">🤖 AI策划建议</h4>
              <ul className="space-y-2">
                {weeklyReport.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-purple-500 mr-2">▪</span>
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Agent分析洞察 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center mb-4">
            <span className="text-3xl mr-3">🧠</span>
            <h3 className="text-lg font-bold">策划Agent分析</h3>
          </div>
          <p className="text-gray-600 mb-4">
            根据您的行为模式，策划Agent发现：
          </p>
          <ul className="space-y-2 text-sm">
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span>您在工作日的专注度较高</span>
            </li>
            <li className="flex items-start">
              <span className="text-yellow-500 mr-2">!</span>
              <span>周末娱乐时间略有增加</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-500 mr-2">→</span>
              <span>建议设置周末娱乐时间上限</span>
            </li>
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center mb-4">
            <span className="text-3xl mr-3">🎬</span>
            <h3 className="text-lg font-bold">导演Agent反馈</h3>
          </div>
          <p className="text-gray-600 mb-4">
            实时干预效果统计：
          </p>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">干预成功率</span>
              <span className="font-bold text-green-600">75%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-green-500 h-2 rounded-full" style={{ width: '75%' }}></div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              您对AI提醒的响应积极，继续保持！
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function CategoryBar({ category, hours, frequency, totalHours }) {
  const percentage = totalHours > 0 ? (parseFloat(hours) / totalHours * 100) : 0
  
  const colors = {
    '游戏': 'bg-red-500',
    '社交': 'bg-blue-500',
    '视频': 'bg-purple-500',
    '购物': 'bg-yellow-500',
    '默认': 'bg-gray-500'
  }
  
  const color = colors[category] || colors['默认']
  
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center">
          <span className="font-medium">{category}</span>
          <span className="text-sm text-gray-500 ml-2">({frequency}次)</span>
        </div>
        <span className="font-bold">{hours}小时</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className={`${color} h-3 rounded-full transition-all duration-500`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        ></div>
      </div>
    </div>
  )
}

export default Analytics
