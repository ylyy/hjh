# 工作生活助手 - Android应用

## 项目简介

这是一个智能工作生活助手Android应用，通过AI Agent系统监控应用使用情况，帮助用户提高工作效率，获得更多成就感。

## 核心功能

### 1. 应用使用监控
- 实时监控用户打开的应用
- 识别娱乐类应用
- 记录使用时长和频率

### 2. AI Agent系统
采用三Agent协作架构：

#### 🎯 策划Agent (Planner Agent)
- 分析用户历史数据
- 制定个性化目标
- 生成每日工作计划
- 评估目标完成度

#### 🎬 导演Agent (Director Agent)
- 实时监控应用使用
- 执行干预策略
- 控制提醒时机和方式
- 协调所有系统行为

#### 💭 情感Agent (Emotion Agent)
- 识别用户情绪状态
- 调整干预强度
- 个性化沟通方式
- 预测用户需求

### 3. 智能干预系统
渐进式干预机制：
- **Level 1 (5分钟)**: 温和提醒
- **Level 2 (15分钟)**: 强化提醒 + 成就展示
- **Level 3 (30分钟)**: 强制干预 - 显示工作目标
- **Level 4 (60分钟)**: 深度干预 - 需要完成任务

### 4. 目标管理
- 设置每日/每周/每月目标
- 追踪目标进度
- 可视化展示完成情况

### 5. 成就系统
- 时间成就：连续工作X小时
- 效率成就：完成X个任务
- 自律成就：减少娱乐时间X%
- 成长成就：达成长期目标

## 技术架构

### 技术栈
- **语言**: Kotlin
- **架构**: MVVM + Clean Architecture
- **数据库**: Room Database
- **异步**: Kotlin Coroutines + Flow
- **UI**: Material Design 3
- **AI**: TensorFlow Lite (本地) + API (云端)

### 项目结构
```
app/src/main/java/com/productivity/assistant/
├── agent/              # AI Agent系统
│   ├── PlannerAgent.kt      # 策划Agent
│   ├── DirectorAgent.kt     # 导演Agent
│   └── EmotionAgent.kt      # 情感Agent
├── data/               # 数据层
│   ├── database/           # Room数据库
│   ├── entity/             # 实体类
│   ├── dao/                # 数据访问对象
│   └── repository/         # 仓库层
├── service/            # 服务层
│   ├── AppUsageMonitorService.kt  # 应用监控服务
│   └── ReminderService.kt          # 提醒服务
└── ui/                 # UI层
    ├── MainActivity.kt
    ├── goal/               # 目标设置
    ├── statistics/         # 统计页面
    └── viewmodel/          # ViewModel
```

## 安装和使用

### 前置要求
- Android Studio Hedgehog | 2023.1.1 或更高版本
- Android SDK 26 (Android 8.0) 或更高版本
- Kotlin 1.9.20+

### 构建步骤

1. 克隆项目
```bash
git clone <repository-url>
cd ProductivityAssistant
```

2. 打开项目
- 使用Android Studio打开项目
- 等待Gradle同步完成

3. 配置权限
应用需要以下权限：
- `PACKAGE_USAGE_STATS` - 应用使用统计权限（需要用户手动授予）
- `POST_NOTIFICATIONS` - 通知权限
- `FOREGROUND_SERVICE` - 前台服务权限

4. 运行应用
- 连接Android设备或启动模拟器
- 点击运行按钮
- 首次启动需要授予应用使用统计权限

## 配置说明

### 设置娱乐应用
在设置页面可以配置哪些应用被视为娱乐应用，系统会自动监控这些应用的使用情况。

### 设置工作时间
可以配置工作时段，在工作时间内系统会采用更严格的干预策略。

### 干预强度
可以调整干预强度：
- 低：仅在长时间使用时提醒
- 中：中等频率提醒
- 高：频繁提醒和干预

## 开发计划

### 已完成
- ✅ 项目基础架构
- ✅ 数据库设计
- ✅ AI Agent系统框架
- ✅ 应用监控服务
- ✅ 提醒系统

### 待完成
- ⏳ UI界面完善
- ⏳ 统计图表展示
- ⏳ 成就系统实现
- ⏳ TensorFlow Lite模型集成
- ⏳ 云端AI API集成
- ⏳ 自适应学习机制
- ⏳ 用户设置界面

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过Issue反馈。
