# 心理目标管理系统

## 核心理念

心理目标管理系统基于**主体性需求**（Subjective Needs）理论，关注用户的深层心理需求而非表面的成就徽章。

### 主体性需求 vs 传统目标

| 传统目标 | 心理目标 |
|---------|---------|
| 完成X个任务 | 满足自主性需求 |
| 工作X小时 | 提升能力感 |
| 减少娱乐时间 | 实现工作生活平衡 |
| 获得徽章 | 满足意义感需求 |

## 核心组件

### 1. SubjectiveNeed（主体性需求）

定义了10种主体性需求类别：

- **AUTONOMY（自主性）**: 希望掌控自己的工作生活
- **COMPETENCE（能力感）**: 希望提升技能和能力
- **RELATEDNESS（归属感）**: 希望与他人建立联系
- **MEANING（意义感）**: 希望工作有意义
- **GROWTH（成长需求）**: 希望持续成长
- **BALANCE（平衡需求）**: 希望工作生活平衡
- **RECOGNITION（认可需求）**: 希望被认可
- **CREATIVITY（创造力需求）**: 希望创造性工作
- **SECURITY（安全感）**: 希望稳定和可预测
- **CHALLENGE（挑战需求）**: 希望有挑战性任务

### 2. SubjectiveNeedAnalyzer（需求分析器）

通过分析用户行为数据，识别和理解用户的深层心理需求：

- **行为模式分析**: 工作时间、娱乐时间、应用切换频率等
- **AI深度分析**: 使用DeepSeek-V3.2分析心理需求
- **变化趋势检测**: 识别需求的变化（增强/减弱/新兴/消退）
- **冲突识别**: 识别需求之间的冲突
- **满足度计算**: 评估需求的满足程度

### 3. EnhancedPlannerAgent（增强策划Agent）

基于主体性需求的目标管理：

- **心理目标推荐**: 根据需求生成目标建议
- **动态调整**: 根据需求变化调整目标
- **冲突解决**: 为需求冲突生成平衡目标
- **心理价值**: 每个目标都关联心理价值

## 工作流程

### 1. 需求分析

```kotlin
val analyzer = SubjectiveNeedAnalyzer(context, appUsageRepository, goalRepository)
val profile = analyzer.analyzeSubjectiveNeeds()

// 获取主导需求
val dominantNeeds = profile.dominantNeeds
// 获取新兴需求
val emergingNeeds = profile.emergingNeeds
// 获取需求冲突
val conflicts = profile.needConflicts
```

### 2. 生成心理目标

```kotlin
val planner = EnhancedPlannerAgent(context, goalRepository, analyzer)
val recommendations = planner.generatePsychologicalGoalRecommendations()

recommendations.forEach { recommendation ->
    println("目标: ${recommendation.goal.title}")
    println("关联需求: ${recommendation.relatedNeed.description}")
    println("心理价值: ${recommendation.psychologicalValue}")
    println("预期满足度: ${recommendation.expectedSatisfaction}")
}
```

### 3. 动态调整目标

```kotlin
// 定期检查并调整目标
val adaptations = planner.adaptGoalsToNeeds()

adaptations.forEach { adaptation ->
    println("调整原因: ${adaptation.reason}")
    println("从: ${adaptation.oldValue}")
    println("到: ${adaptation.newValue}")
}
```

## 示例场景

### 场景1: 自主性需求增强

**检测到**: 用户工作时间变异性高，频繁切换应用

**分析结果**: 
- 自主性需求强度: 0.8
- 变化趋势: INCREASING

**生成目标**:
- "自主安排工作时间" - 每天至少2小时自主时间
- "减少被动任务" - 将被动任务比例降低到30%以下

**心理价值**: 满足自主性需求，增强对工作生活的掌控感

### 场景2: 平衡需求与挑战需求冲突

**检测到**: 
- 平衡需求强度: 0.7
- 挑战需求强度: 0.8

**冲突**: 希望挑战但又需要平衡

**生成目标**:
- "平衡挑战和休息" - 每周完成1个挑战性任务，同时保持工作生活平衡

**心理价值**: 解决需求冲突，找到平衡点

### 场景3: 能力感需求未满足

**检测到**: 
- 工作时间长但完成率低
- 能力感需求强度: 0.7
- 满足度: 0.3

**生成目标**:
- "提升核心技能" - 每周学习新技能或提升现有技能
- "提高目标完成率" - 将完成率提升到80%以上

**心理价值**: 提升能力感，增强自信

## 优势

1. **个性化**: 基于用户真实需求，而非通用模板
2. **动态性**: 随需求变化自动调整
3. **深层性**: 关注心理满足而非表面成就
4. **冲突处理**: 识别并解决需求冲突
5. **价值导向**: 每个目标都有明确的心理价值

## 与AI的集成

- **需求分析**: 使用DeepSeek-V3.2深度分析用户心理需求
- **目标生成**: AI生成个性化的目标建议
- **价值描述**: AI生成目标的心理价值描述

## 未来扩展

1. **需求预测**: 预测未来可能出现的需求
2. **个性化模型**: 为每个用户建立个性化需求模型
3. **社交对比**: 匿名对比相似用户的需求模式
4. **专业建议**: 结合心理学理论提供专业建议
