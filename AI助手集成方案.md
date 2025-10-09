# 产线测试工具集成AI助手方案

## 需求分析
- **现有系统**：Electron桌面划词AI助手
- **目标系统**：产线测试工具（C++底层 + C#上层）
- **目标功能**：在错误日志处添加按钮，一键获取log并向AI提问解决方法

## 推荐集成方案

### 方案一：HTTP API服务（★★★★★ 推荐）

**架构设计**：
```
C#测试工具 → HTTP Request → Electron App → AI服务 → 返回解决方案
```

**实现步骤**：

#### 1. Electron端改造
在你的Electron应用中添加HTTP服务器：

```javascript
// main.js 或单独的 api-server.js
const express = require('express');
const bodyParser = require('body-parser');

class AIApiServer {
  constructor(port = 8765) {
    this.app = express();
    this.port = port;
    this.setupMiddleware();
    this.setupRoutes();
  }

  setupMiddleware() {
    this.app.use(bodyParser.json({ limit: '10mb' }));
    this.app.use((req, res, next) => {
      res.header('Access-Control-Allow-Origin', '*');
      next();
    });
  }

  setupRoutes() {
    // 接收错误日志并分析
    this.app.post('/api/analyze-error', async (req, res) => {
      try {
        const { errorLog, context } = req.body;
        
        // 调用你的AI分析逻辑
        const solution = await this.analyzeError(errorLog, context);
        
        res.json({
          success: true,
          solution: solution,
          timestamp: Date.now()
        });
      } catch (error) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // 健康检查接口
    this.app.get('/api/health', (req, res) => {
      res.json({ status: 'ok', service: 'AI Assistant' });
    });
  }

  async analyzeError(errorLog, context) {
    // 这里接入你现有的AI逻辑
    const prompt = `分析以下错误日志并给出解决方案：
    
错误日志：
${errorLog}

上下文信息：
${JSON.stringify(context, null, 2)}

请给出：
1. 错误原因分析
2. 可能的解决方案
3. 预防措施`;
    
    // 调用你的AI服务
    return await this.callAIService(prompt);
  }

  start() {
    this.server = this.app.listen(this.port, () => {
      console.log(`AI API Server running on port ${this.port}`);
    });
  }

  stop() {
    if (this.server) {
      this.server.close();
    }
  }
}

// 在Electron启动时初始化
let apiServer;
app.on('ready', () => {
  apiServer = new AIApiServer(8765);
  apiServer.start();
});
```

#### 2. C#端调用

```csharp
// AIAssistantClient.cs
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class AIAssistantClient
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;

    public AIAssistantClient(string baseUrl = "http://localhost:8765")
    {
        _baseUrl = baseUrl;
        _httpClient = new HttpClient
        {
            Timeout = TimeSpan.FromSeconds(30)
        };
    }

    public async Task<bool> IsServiceAvailableAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/api/health");
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }

    public async Task<AISolutionResponse> AnalyzeErrorAsync(string errorLog, object context = null)
    {
        var requestData = new
        {
            errorLog = errorLog,
            context = context ?? new { }
        };

        var json = JsonConvert.SerializeObject(requestData);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        try
        {
            var response = await _httpClient.PostAsync($"{_baseUrl}/api/analyze-error", content);
            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<AISolutionResponse>(responseJson);
        }
        catch (Exception ex)
        {
            return new AISolutionResponse
            {
                Success = false,
                Error = ex.Message
            };
        }
    }
}

public class AISolutionResponse
{
    [JsonProperty("success")]
    public bool Success { get; set; }

    [JsonProperty("solution")]
    public string Solution { get; set; }

    [JsonProperty("error")]
    public string Error { get; set; }

    [JsonProperty("timestamp")]
    public long Timestamp { get; set; }
}
```

#### 3. UI集成示例（WinForms）

```csharp
// ErrorLogViewer.cs
public partial class ErrorLogViewer : Form
{
    private AIAssistantClient _aiClient;
    private TextBox _errorLogTextBox;
    private Button _analyzeButton;
    private RichTextBox _solutionTextBox;

    public ErrorLogViewer()
    {
        InitializeComponent();
        _aiClient = new AIAssistantClient();
        InitializeControls();
    }

    private void InitializeControls()
    {
        // 在错误日志旁边添加"AI分析"按钮
        _analyzeButton = new Button
        {
            Text = "🤖 AI分析解决方案",
            Location = new Point(10, 10),
            Size = new Size(150, 30)
        };
        _analyzeButton.Click += async (s, e) => await AnalyzeError();
        this.Controls.Add(_analyzeButton);
    }

    private async Task AnalyzeError()
    {
        _analyzeButton.Enabled = false;
        _analyzeButton.Text = "分析中...";

        try
        {
            // 检查服务是否可用
            if (!await _aiClient.IsServiceAvailableAsync())
            {
                MessageBox.Show(
                    "AI助手服务未运行，请先启动AI助手应用。",
                    "服务不可用",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning
                );
                return;
            }

            // 获取错误日志
            string errorLog = _errorLogTextBox.Text;
            
            // 收集上下文信息
            var context = new
            {
                timestamp = DateTime.Now,
                testCase = GetCurrentTestCase(),
                environment = GetEnvironmentInfo()
            };

            // 调用AI分析
            var response = await _aiClient.AnalyzeErrorAsync(errorLog, context);

            if (response.Success)
            {
                _solutionTextBox.Text = response.Solution;
                
                // 可选：保存到日志
                SaveAnalysisToLog(errorLog, response.Solution);
            }
            else
            {
                MessageBox.Show($"分析失败: {response.Error}", "错误");
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show($"请求失败: {ex.Message}", "错误");
        }
        finally
        {
            _analyzeButton.Enabled = true;
            _analyzeButton.Text = "🤖 AI分析解决方案";
        }
    }

    private string GetCurrentTestCase()
    {
        // 返回当前测试用例信息
        return "Test_XXX";
    }

    private object GetEnvironmentInfo()
    {
        return new
        {
            machine = Environment.MachineName,
            os = Environment.OSVersion.ToString(),
            user = Environment.UserName
        };
    }

    private void SaveAnalysisToLog(string errorLog, string solution)
    {
        // 保存分析结果到文件
        string logPath = $"ai_analysis_{DateTime.Now:yyyyMMdd_HHmmss}.txt";
        File.WriteAllText(logPath, $"错误日志:\n{errorLog}\n\n解决方案:\n{solution}");
    }
}
```

**优点**：
- ✅ 松耦合，两个系统独立运行
- ✅ 易于维护和升级
- ✅ 支持跨语言、跨平台
- ✅ 可以同时服务多个客户端
- ✅ 容易调试和测试

**缺点**：
- ❌ 需要Electron应用保持运行
- ❌ 网络延迟（本地通信，延迟很小）

---

### 方案二：Named Pipe / Socket通信（★★★★☆）

**适用场景**：需要更快的通信速度，或者网络受限环境

```csharp
// C# 端使用 Named Pipe
using System.IO.Pipes;

public class AIAssistantPipeClient
{
    private const string PipeName = "AIAssistantPipe";

    public async Task<string> AnalyzeErrorAsync(string errorLog)
    {
        using (var client = new NamedPipeClientStream(".", PipeName, PipeDirection.InOut))
        {
            await client.ConnectAsync(5000);
            
            using (var writer = new StreamWriter(client))
            using (var reader = new StreamReader(client))
            {
                await writer.WriteLineAsync(errorLog);
                await writer.FlushAsync();
                
                return await reader.ReadToEndAsync();
            }
        }
    }
}
```

```javascript
// Electron 端创建 Named Pipe 服务
const net = require('net');
const path = require('path');

const PIPE_NAME = 'AIAssistantPipe';
const PIPE_PATH = process.platform === 'win32' 
  ? `\\\\.\\pipe\\${PIPE_NAME}`
  : path.join('/tmp', PIPE_NAME);

const server = net.createServer((socket) => {
  socket.on('data', async (data) => {
    const errorLog = data.toString();
    const solution = await analyzeError(errorLog);
    socket.write(solution);
    socket.end();
  });
});

server.listen(PIPE_PATH);
```

---

### 方案三：命令行接口（★★★☆☆）

**适用场景**：简单快速的集成，不需要实时通信

```csharp
// C# 调用 Electron CLI
public class AIAssistantCLI
{
    private string _electronAppPath;

    public string AnalyzeError(string errorLog)
    {
        var tempFile = Path.GetTempFileName();
        File.WriteAllText(tempFile, errorLog);

        var process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = _electronAppPath,
                Arguments = $"--analyze-error \"{tempFile}\"",
                RedirectStandardOutput = true,
                UseShellExecute = false
            }
        };

        process.Start();
        string result = process.StandardOutput.ReadToEnd();
        process.WaitForExit();

        File.Delete(tempFile);
        return result;
    }
}
```

---

### 方案四：嵌入式集成 - Native Node Addon（★★☆☆☆）

**适用场景**：需要深度集成，性能要求极高

这个方案比较复杂，需要：
1. 将Electron的核心逻辑封装为Node Native Addon
2. 通过C++调用Node.js
3. 需要处理V8引擎的初始化和管理

**不推荐**：实现复杂度高，维护成本大

---

## 推荐实施方案

### 🎯 最佳方案：HTTP API服务 + 自动启动

**实施步骤**：

1. **Electron端改造**
   - 添加express HTTP服务器（代码见方案一）
   - 在Electron启动时自动启动API服务
   - 添加托盘图标，显示服务状态
   - 添加配置文件，允许修改端口

2. **C#端改造**
   - 创建AIAssistantClient类（代码见方案一）
   - 在测试工具启动时检查AI服务状态
   - 如果服务未启动，提示用户或自动启动Electron应用
   - 在错误日志界面添加"AI分析"按钮

3. **自动启动机制**

```csharp
// 自动启动 Electron 应用
public class AIServiceManager
{
    private string _electronAppPath;
    private Process _electronProcess;

    public async Task<bool> EnsureServiceRunningAsync()
    {
        var client = new AIAssistantClient();
        
        // 检查服务是否已运行
        if (await client.IsServiceAvailableAsync())
        {
            return true;
        }

        // 尝试启动服务
        return StartElectronApp();
    }

    private bool StartElectronApp()
    {
        try
        {
            _electronProcess = Process.Start(new ProcessStartInfo
            {
                FileName = _electronAppPath,
                Arguments = "--api-server-mode", // 静默启动，仅运行API服务
                WindowStyle = ProcessWindowStyle.Hidden
            });

            // 等待服务启动
            Thread.Sleep(3000);
            return true;
        }
        catch
        {
            return false;
        }
    }
}
```

4. **配置管理**

```json
// config.json（两个应用共享）
{
  "apiServer": {
    "host": "localhost",
    "port": 8765,
    "timeout": 30000
  },
  "electronApp": {
    "path": "C:\\Program Files\\AIAssistant\\AIAssistant.exe"
  }
}
```

---

## 安全考虑

1. **认证机制**
```javascript
// 简单的Token认证
const API_TOKEN = 'your-secret-token';

app.use((req, res, next) => {
  const token = req.headers['authorization'];
  if (token !== `Bearer ${API_TOKEN}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
});
```

2. **限制访问来源**
```javascript
// 只允许本地访问
app.use((req, res, next) => {
  const clientIP = req.ip;
  if (clientIP !== '127.0.0.1' && clientIP !== '::1') {
    return res.status(403).json({ error: 'Forbidden' });
  }
  next();
});
```

---

## 部署建议

### 开发环境
- Electron应用：开发模式运行，热重载
- C#应用：指向 http://localhost:8765

### 生产环境
1. 将Electron应用打包为可执行文件
2. 配置为Windows服务或开机自启
3. C#应用通过配置文件读取API地址
4. 添加服务健康检查和自动重启机制

---

## 示例项目结构

```
AIAssistant/                  # Electron AI助手
├── main.js
├── api-server.js             # 新增：API服务器
├── ai-service.js             # AI逻辑
└── package.json

TestTool/                     # C#测试工具
├── TestTool.csproj
├── AIIntegration/            # 新增：AI集成模块
│   ├── AIAssistantClient.cs
│   ├── AIServiceManager.cs
│   └── Models/
│       └── AISolutionResponse.cs
├── UI/
│   └── ErrorLogViewer.cs     # 修改：添加AI分析按钮
└── config.json               # 配置文件
```

---

## 总结

**推荐使用方案一（HTTP API服务）**，因为：
1. ✅ 实现简单，代码清晰
2. ✅ 易于调试和测试
3. ✅ 松耦合，互不影响
4. ✅ 可扩展性强，未来可以支持更多功能
5. ✅ 跨语言、跨平台兼容性好

如果有特殊需求（如极高性能要求、无网络环境），可以考虑方案二（Named Pipe）。
