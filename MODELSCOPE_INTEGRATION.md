# ModelScope AI集成文档

## 概述

本项目已集成ModelScope的AI能力，包括：
- **DeepSeek-V3.2**: 文本生成模型
- **Z-Image-Turbo**: 文本生成图片模型

## API配置

### Token配置
Token已配置在 `ModelScopeConfig.kt` 中：
```kotlin
const val API_TOKEN = "ms-8d334afb-84a5-4f92-9e23-eb027737ca1f"
```

### API端点
- 基础URL: `https://api.modelscope.cn/api-inference/v1/`
- 文本生成: `POST /models/deepseek-ai/DeepSeek-V3.2/inference`
- 图片生成: `POST /models/Tongyi-MAI/Z-Image-Turbo/inference`

## 集成功能

### 1. 个性化提醒生成
**位置**: `AIService.generatePersonalizedReminder()`

使用DeepSeek-V3.2生成个性化的提醒内容，根据用户的工作状态、娱乐时间、未完成目标等信息，生成温和有效的提醒。

**使用示例**:
```kotlin
val aiService = AIService(context)
val reminder = aiService.generatePersonalizedReminder(
    entertainmentTime = 15,
    workTime = 3.5f,
    incompleteGoals = listOf("完成报告", "回复邮件"),
    emotionState = "正常"
)
```

### 2. 智能目标建议
**位置**: `AIService.generateGoalSuggestions()`

基于用户的工作历史、当前目标和偏好，生成个性化的目标建议。

**使用示例**:
```kotlin
val suggestions = aiService.generateGoalSuggestions(
    workHistory = "平均每日工作4小时",
    currentGoals = listOf("完成项目A", "学习新技术"),
    userPreferences = "偏好高效工作"
)
```

### 3. 成就徽章生成
**位置**: `AIService.generateAchievementBadge()`

使用Z-Image-Turbo为成就生成个性化的徽章图片。

**使用示例**:
```kotlin
val badge = aiService.generateAchievementBadge(
    achievementName = "连续工作7天",
    achievementDescription = "连续7天完成工作目标"
)
```

### 4. 工作建议生成
**位置**: `AIService.generateWorkAdvice()`

根据当前时间、工作效率和最近模式，生成实用的工作建议。

### 5. 情绪分析和建议
**位置**: `AIService.analyzeEmotionAndAdvise()`

分析用户的应用使用模式、工作完成率和压力指标，生成鼓励性建议。

## Agent系统集成

### PlannerAgent增强
- 使用AI生成目标建议
- 智能分析用户数据
- 个性化目标推荐

### DirectorAgent增强
- AI生成个性化提醒内容
- 根据情绪状态调整提醒方式

### EmotionAgent增强
- AI分析用户情绪
- 生成个性化建议
- 智能调整干预策略

## 使用流程

1. **初始化AIService**
```kotlin
val aiService = AIService(context)
```

2. **调用AI功能**
```kotlin
lifecycleScope.launch {
    val result = aiService.generatePersonalizedReminder(...)
    // 使用结果
}
```

3. **错误处理**
所有AI方法都返回`Result<T>`类型，需要处理可能的失败情况：
```kotlin
when (val result = aiService.generateText(...)) {
    is Result.Success -> {
        // 使用result.value
    }
    is Result.Failure -> {
        // 处理错误，使用默认内容
    }
}
```

## 配置管理

通过`ConfigManager`可以控制AI功能的开关：

```kotlin
val configManager = ConfigManager(context)

// 启用/禁用AI功能
configManager.setAIEnabled(true)

// 检查AI是否启用
if (configManager.isAIEnabled()) {
    // 使用AI功能
}
```

## 注意事项

1. **网络请求**: AI功能需要网络连接，建议添加网络状态检查
2. **API限制**: 注意ModelScope API的调用频率限制
3. **错误处理**: 所有AI调用都应该有后备方案（默认内容）
4. **异步处理**: 所有AI调用都是异步的，需要在协程中使用
5. **Token安全**: 生产环境建议将Token存储在安全位置，不要硬编码

## 未来优化

1. **缓存机制**: 缓存常用的AI生成内容
2. **离线模式**: 使用本地模型作为后备
3. **批量请求**: 优化API调用，减少请求次数
4. **用户反馈**: 收集用户对AI生成内容的反馈，持续优化

## API文档参考

ModelScope API文档: https://modelscope.cn/docs/model-service/API-Inference/intro
