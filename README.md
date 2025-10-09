# 产线测试工具 × AI助手集成方案

## 📋 项目概述

本方案帮助你将现有的**Electron桌面划词AI助手**集成到**C++/C#产线测试工具**中，实现一键分析错误日志并获取AI解决方案。

## 🎯 核心功能

- ✅ 在错误日志界面添加"AI分析"按钮
- ✅ 自动获取错误日志并发送给AI
- ✅ 实时显示AI分析的解决方案
- ✅ 支持批量分析多个错误
- ✅ 自动启动和管理AI服务
- ✅ 保存分析历史记录

## 🏗️ 架构设计

```
┌─────────────────────┐          HTTP API          ┌──────────────────┐
│   C# 测试工具        │  ◄─────────────────────►  │  Electron        │
│   (上层UI)          │   localhost:8765          │  AI助手          │
└─────────────────────┘                            └──────────────────┘
         │                                                   │
         │                                                   │
         ▼                                                   ▼
┌─────────────────────┐                            ┌──────────────────┐
│   C++ 底层          │                            │  AI服务          │
│   (测试引擎)        │                            │  (OpenAI/本地)   │
└─────────────────────┘                            └──────────────────┘
```

## 📦 文件清单

### 方案文档
- **`AI助手集成方案.md`** - 详细的技术方案和实现方案（多种方案对比）
- **`使用说明.md`** - 完整的使用说明和故障排查指南
- **`README.md`** - 本文件，快速开始指南

### Electron端代码
- **`electron-api-server.js`** - API服务器（在Electron中启动）
- **`package.example.json`** - npm依赖配置示例

### C#端代码
- **`AIAssistantClient.cs`** - AI助手客户端（通信层）
- **`AIServiceManager.cs`** - AI服务管理器（启动/停止服务）
- **`ErrorLogViewer.cs`** - 错误日志查看器UI示例（完整可运行）

### 配置文件
- **`config.example.json`** - 配置文件模板

## 🚀 快速开始

### 前置要求

- Electron应用已安装
- C#项目支持 .NET Framework 4.7+ 或 .NET Core 3.1+
- 已安装Newtonsoft.Json NuGet包

### 第一步：配置Electron端

1. **安装依赖**
```bash
cd YourElectronApp
npm install express body-parser cors
```

2. **复制API服务器文件**
```bash
cp electron-api-server.js YourElectronApp/
```

3. **在main.js中启动API服务器**
```javascript
const AIApiServer = require('./electron-api-server');

let apiServer;

app.on('ready', async () => {
  // 你原有的初始化代码
  createWindow();
  
  // 启动API服务器
  apiServer = new AIApiServer({
    port: 8765,
    apiToken: 'your-secret-token-here'
  });
  
  await apiServer.start();
});

app.on('will-quit', async () => {
  if (apiServer) {
    await apiServer.stop();
  }
});
```

4. **接入你的AI服务**

在 `electron-api-server.js` 中找到 `callAIService` 方法，替换为你的AI调用逻辑。

### 第二步：配置C#端

1. **安装NuGet包**
```bash
Install-Package Newtonsoft.Json
```

2. **创建项目结构**
```
YourTestTool/
├── AIIntegration/
│   ├── AIAssistantClient.cs      ← 复制此文件
│   └── AIServiceManager.cs       ← 复制此文件
├── UI/
│   └── ErrorLogViewer.cs         ← 复制此文件（或参考集成到现有UI）
└── config.json                   ← 基于config.example.json创建
```

3. **创建配置文件**

将 `config.example.json` 复制为 `config.json`，并修改：
```json
{
  "aiService": {
    "apiBaseUrl": "http://localhost:8765",
    "apiToken": "your-secret-token-here",  // 与Electron端一致
    "timeout": 30
  },
  "electronApp": {
    "path": "C:\\路径\\到\\你的\\AI助手.exe",  // 修改为实际路径
    "autoStart": true
  }
}
```

4. **在现有UI中添加AI分析按钮**

参考 `ErrorLogViewer.cs` 中的实现，在你的错误日志界面添加：

```csharp
using TestTool.AIIntegration;

// 在你的Form中
private AIAssistantClient _aiClient;

public YourForm()
{
    InitializeComponent();
    
    // 初始化AI客户端
    _aiClient = new AIAssistantClient(
        "http://localhost:8765",
        "your-secret-token-here"
    );
    
    // 添加AI分析按钮
    var aiButton = new Button
    {
        Text = "🤖 AI分析",
        // ... 设置位置和样式
    };
    aiButton.Click += async (s, e) => await AnalyzeError();
}

private async Task AnalyzeError()
{
    string errorLog = GetCurrentErrorLog(); // 获取错误日志
    
    var response = await _aiClient.AnalyzeErrorAsync(errorLog);
    
    if (response.Success)
    {
        MessageBox.Show(response.Solution, "AI分析结果");
    }
}
```

### 第三步：测试集成

1. **启动Electron应用**
```bash
# 确保API服务器已启动
# 查看控制台输出，应该看到：
# 🚀 AI Assistant API Server Started
# 📡 Listening on: http://localhost:8765
```

2. **测试API连接**

打开浏览器访问：`http://localhost:8765/api/health`

应该看到：
```json
{
  "status": "ok",
  "service": "AI Assistant API",
  "version": "1.0.0"
}
```

3. **运行C#测试工具**
   - 打开错误日志界面
   - 点击"AI分析"按钮
   - 查看分析结果

## 📚 详细文档

- **完整技术方案** → 查看 `AI助手集成方案.md`
- **使用说明和故障排查** → 查看 `使用说明.md`

## 🎨 集成示例

### 示例1：简单集成（最小化代码）

```csharp
// 只需3行代码即可实现AI分析
var aiClient = new AIAssistantClient();
var response = await aiClient.AnalyzeErrorAsync(errorLog);
MessageBox.Show(response.Solution);
```

### 示例2：完整集成（带UI）

使用提供的 `ErrorLogViewer.cs`，它包含：
- ✅ 美观的现代UI
- ✅ 自动服务管理
- ✅ 进度显示
- ✅ 复制和保存功能
- ✅ 历史记录

### 示例3：批量分析

```csharp
var errors = GetAllRecentErrors();
var response = await aiClient.AnalyzeBatchAsync(errors);

foreach (var result in response.Results)
{
    Console.WriteLine($"{result.Id}: {result.Solution}");
}
```

## 💡 推荐的集成方式

### 方案A：HTTP API（推荐⭐⭐⭐⭐⭐）

✅ **优点**：
- 实现简单，代码清晰
- 松耦合，易于维护
- 跨语言、跨平台
- 易于调试和扩展

❌ **缺点**：
- 需要Electron应用运行
- 轻微的网络延迟（本地通信，可忽略）

### 方案B：Named Pipe（可选⭐⭐⭐⭐）

适用于需要极高性能或网络受限的场景。实现略复杂。

### 方案C：命令行调用（不推荐⭐⭐⭐）

仅适合简单场景，不支持实时通信。

## 🔧 常见问题

### Q1: 无法连接到AI服务

**A**: 检查以下几点：
1. Electron应用是否正在运行
2. 端口8765是否被占用
3. API Token是否一致
4. 防火墙是否阻止

```bash
# 检查端口
netstat -ano | findstr :8765

# 测试连接
curl http://localhost:8765/api/health
```

### Q2: C#端找不到命名空间

**A**: 确保已添加文件到项目，并检查命名空间：
```csharp
using TestTool.AIIntegration;
```

### Q3: 请求超时

**A**: 增加timeout设置：
```csharp
var aiClient = new AIAssistantClient(
    timeout: 60  // 增加到60秒
);
```

## 🎯 下一步

1. **自定义UI** - 根据你的测试工具风格调整界面
2. **优化提示词** - 在 `electron-api-server.js` 中优化AI提示词
3. **添加缓存** - 缓存相似错误的分析结果
4. **团队分享** - 搭建知识库，分享解决方案
5. **持续优化** - 根据用户反馈改进

## 📞 支持

遇到问题？
1. 查看 `使用说明.md` 中的故障排查章节
2. 检查日志文件：`AIAnalysisLogs/`
3. 查看Electron控制台输出

## 📄 许可证

根据你的项目需求添加相应的许可证信息。

---

**祝你集成顺利！如有问题欢迎反馈。** 🚀
