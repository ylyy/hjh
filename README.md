# 🎯 AI生产力教练 - 智能助手系统

## 📋 项目概述

这是一个基于双Agent AI架构的智能生产力管理系统，帮助您监控娱乐应用使用，建立良好的工作生活习惯，通过成就感激励提升生产力。

## 🌟 核心特性

### 双Agent AI架构
- **策划Agent (Planner)**: 分析用户行为模式，制定个性化目标和策略
- **导演Agent (Director)**: 实时决策和干预，控制所有交互行为

### 主要功能
1. **智能监控** - 实时检测娱乐应用的启动和使用时长
2. **主动提醒** - 多渠道智能提醒（通知、语音、可视化）
3. **目标管理** - 设定和追踪工作/生活目标
4. **成就系统** - 游戏化设计，获得徽章和奖励
5. **数据洞察** - 可视化分析使用习惯和生产力趋势
6. **跨平台支持** - Android App + Web控制台

## 🏗️ 项目架构

```
ai-productivity-coach/
├── android-app/          # Android监控应用
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/com/aicoach/
│   │   │   │   ├── service/      # 监控服务
│   │   │   │   ├── ui/           # UI界面
│   │   │   │   └── network/      # 网络通信
│   │   │   ├── res/              # 资源文件
│   │   │   └── AndroidManifest.xml
│   │   └── build.gradle
│   └── build.gradle
│
├── backend/              # 后端服务（双Agent AI系统）
│   ├── agents/
│   │   ├── planner_agent.py      # 策划Agent
│   │   └── director_agent.py     # 导演Agent
│   ├── api/
│   │   └── server.py             # Flask/FastAPI服务器
│   ├── models/
│   │   └── database.py           # 数据模型
│   └── requirements.txt
│
├── web-console/          # Web控制台
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── package.json
│
└── docs/                 # 文档
    ├── 架构设计.md
    ├── 部署指南.md
    └── 使用手册.md
```

## 🚀 快速开始

### 1. 后端服务器启动
```bash
cd backend
pip install -r requirements.txt
python api/server.py
```

### 2. Web控制台启动
```bash
cd web-console
npm install
npm run dev
```

### 3. Android App安装
1. 使用Android Studio打开 `android-app/` 目录
2. 连接手机或启动模拟器
3. 点击Run构建安装

## 💡 使用场景

1. **工作场景**: 检测到打开游戏，AI提醒当前任务进度
2. **学习场景**: 追踪学习时长，达成目标获得成就徽章
3. **健康场景**: 提醒过度使用，建议休息或运动

## 🤖 AI Agent工作流程

```
用户打开娱乐App
    ↓
[Android监控] → 发送事件
    ↓
[导演Agent] → 实时分析决策
    ↓
    ├─ 立即提醒？
    ├─ 记录数据？
    └─ 触发策略？
    ↓
[策划Agent] → 每日分析（异步）
    ↓
    ├─ 调整目标
    ├─ 制定新策略
    └─ 生成报告
```

## 📊 数据隐私

- 所有数据本地存储
- 支持自托管部署
- 不上传敏感信息到第三方

## 🔧 技术栈

- **Android**: Kotlin + Jetpack Compose + WorkManager
- **后端**: Python + FastAPI + SQLite
- **AI**: OpenAI API / 本地LLM
- **前端**: React + Vite + TailwindCSS + Chart.js

## 📝 开发计划

- [x] 项目架构设计
- [x] 双Agent系统实现
- [x] Android监控服务
- [x] Web控制台
- [x] 目标和成就系统
- [ ] 语音提醒功能
- [ ] 多用户支持
- [ ] 云同步功能

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交Issue和Pull Request！
