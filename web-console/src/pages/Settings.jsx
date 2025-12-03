import React, { useState } from 'react'

function Settings() {
  const [settings, setSettings] = useState({
    notificationEnabled: true,
    interventionFrequency: 'medium',
    quietHoursStart: '22:00',
    quietHoursEnd: '08:00',
    dailyLimit: '2',
    agentMode: 'balanced'
  })

  const handleSave = () => {
    // 保存设置的逻辑
    alert('设置已保存！')
  }

  return (
    <div className="space-y-6">
      {/* 标题 */}
      <div>
        <h2 className="text-3xl font-bold text-gray-800">设置</h2>
        <p className="text-gray-600 mt-1">个性化您的AI生产力教练体验</p>
      </div>

      {/* 通知设置 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold mb-4">📢 通知设置</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">启用通知</div>
              <div className="text-sm text-gray-600">接收AI干预提醒</div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notificationEnabled}
                onChange={(e) => setSettings({...settings, notificationEnabled: e.target.checked})}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>

          <div>
            <label className="block font-medium mb-2">干预频率</label>
            <select
              value={settings.interventionFrequency}
              onChange={(e) => setSettings({...settings, interventionFrequency: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="low">低 (每天最多3次)</option>
              <option value="medium">中 (每天最多10次)</option>
              <option value="high">高 (不限制)</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block font-medium mb-2">勿扰开始时间</label>
              <input
                type="time"
                value={settings.quietHoursStart}
                onChange={(e) => setSettings({...settings, quietHoursStart: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <div>
              <label className="block font-medium mb-2">勿扰结束时间</label>
              <input
                type="time"
                value={settings.quietHoursEnd}
                onChange={(e) => setSettings({...settings, quietHoursEnd: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
          </div>
        </div>
      </div>

      {/* AI Agent设置 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold mb-4">🤖 AI Agent设置</h3>
        <div className="space-y-4">
          <div>
            <label className="block font-medium mb-2">Agent模式</label>
            <div className="space-y-2">
              <label className="flex items-center p-3 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-primary transition-colors">
                <input
                  type="radio"
                  name="agentMode"
                  value="gentle"
                  checked={settings.agentMode === 'gentle'}
                  onChange={(e) => setSettings({...settings, agentMode: e.target.value})}
                  className="mr-3"
                />
                <div>
                  <div className="font-medium">温和模式</div>
                  <div className="text-sm text-gray-600">以鼓励为主，减少干预</div>
                </div>
              </label>
              <label className="flex items-center p-3 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-primary transition-colors">
                <input
                  type="radio"
                  name="agentMode"
                  value="balanced"
                  checked={settings.agentMode === 'balanced'}
                  onChange={(e) => setSettings({...settings, agentMode: e.target.value})}
                  className="mr-3"
                />
                <div>
                  <div className="font-medium">平衡模式（推荐）</div>
                  <div className="text-sm text-gray-600">智能判断，适度干预</div>
                </div>
              </label>
              <label className="flex items-center p-3 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-primary transition-colors">
                <input
                  type="radio"
                  name="agentMode"
                  value="strict"
                  checked={settings.agentMode === 'strict'}
                  onChange={(e) => setSettings({...settings, agentMode: e.target.value})}
                  className="mr-3"
                />
                <div>
                  <div className="font-medium">严格模式</div>
                  <div className="text-sm text-gray-600">强制执行，及时干预</div>
                </div>
              </label>
            </div>
          </div>

          <div>
            <label className="block font-medium mb-2">
              每日娱乐时间上限（小时）
            </label>
            <input
              type="number"
              value={settings.dailyLimit}
              onChange={(e) => setSettings({...settings, dailyLimit: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              min="0"
              max="24"
            />
          </div>
        </div>
      </div>

      {/* 数据管理 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold mb-4">💾 数据管理</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <div className="font-medium">导出数据</div>
              <div className="text-sm text-gray-600">下载所有历史数据</div>
            </div>
            <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
              导出
            </button>
          </div>
          <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
            <div>
              <div className="font-medium text-red-600">清除所有数据</div>
              <div className="text-sm text-gray-600">此操作不可恢复</div>
            </div>
            <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
              清除
            </button>
          </div>
        </div>
      </div>

      {/* 服务器设置 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold mb-4">🔗 服务器设置</h3>
        <div className="space-y-4">
          <div>
            <label className="block font-medium mb-2">服务器地址</label>
            <input
              type="text"
              defaultValue="http://localhost:8000"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="http://your-server:8000"
            />
            <p className="text-sm text-gray-600 mt-1">
              修改后需要重启Android应用
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">服务器状态: 已连接</span>
          </div>
        </div>
      </div>

      {/* 保存按钮 */}
      <div className="flex justify-end space-x-4">
        <button className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
          重置
        </button>
        <button
          onClick={handleSave}
          className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-purple-700 transition-colors shadow-md"
        >
          保存设置
        </button>
      </div>
    </div>
  )
}

export default Settings
