import React from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Goals from './pages/Goals'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        {/* 导航栏 */}
        <nav className="bg-primary text-white shadow-lg">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-8">
                <h1 className="text-2xl font-bold">🎯 AI生产力教练</h1>
                <div className="hidden md:flex space-x-4">
                  <Link to="/" className="hover:bg-purple-700 px-3 py-2 rounded">
                    仪表盘
                  </Link>
                  <Link to="/goals" className="hover:bg-purple-700 px-3 py-2 rounded">
                    目标管理
                  </Link>
                  <Link to="/analytics" className="hover:bg-purple-700 px-3 py-2 rounded">
                    数据分析
                  </Link>
                  <Link to="/settings" className="hover:bg-purple-700 px-3 py-2 rounded">
                    设置
                  </Link>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm">双Agent AI系统</span>
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              </div>
            </div>
          </div>
        </nav>

        {/* 主要内容 */}
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/goals" element={<Goals />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>

        {/* 页脚 */}
        <footer className="bg-white border-t mt-12">
          <div className="container mx-auto px-4 py-6 text-center text-gray-600">
            <p>AI生产力教练 © 2025 - 让您更有成就感地工作生活</p>
            <p className="text-sm mt-2">策划Agent + 导演Agent 双AI系统</p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App
