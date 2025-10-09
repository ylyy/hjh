/**
 * Electron AI助手 - API服务器模块
 * 用于接收C#测试工具的错误日志分析请求
 */

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

class AIApiServer {
  constructor(config = {}) {
    this.port = config.port || 8765;
    this.apiToken = config.apiToken || 'your-secret-token-change-this';
    this.app = express();
    this.server = null;
    
    this.setupMiddleware();
    this.setupRoutes();
  }

  /**
   * 配置中间件
   */
  setupMiddleware() {
    // 解析JSON请求体
    this.app.use(bodyParser.json({ limit: '10mb' }));
    this.app.use(bodyParser.urlencoded({ extended: true }));

    // CORS设置（仅允许本地访问）
    this.app.use(cors({
      origin: (origin, callback) => {
        // 允许无origin的请求（如Postman）或本地请求
        if (!origin || origin.includes('localhost') || origin.includes('127.0.0.1')) {
          callback(null, true);
        } else {
          callback(new Error('Not allowed by CORS'));
        }
      }
    }));

    // 请求日志
    this.app.use((req, res, next) => {
      console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
      next();
    });

    // Token认证（可选，建议启用）
    this.app.use((req, res, next) => {
      // 健康检查接口不需要认证
      if (req.path === '/api/health') {
        return next();
      }

      const authHeader = req.headers['authorization'];
      if (authHeader !== `Bearer ${this.apiToken}`) {
        return res.status(401).json({
          success: false,
          error: 'Unauthorized - Invalid or missing token'
        });
      }
      next();
    });
  }

  /**
   * 配置路由
   */
  setupRoutes() {
    // 健康检查接口
    this.app.get('/api/health', (req, res) => {
      res.json({
        status: 'ok',
        service: 'AI Assistant API',
        version: '1.0.0',
        timestamp: Date.now()
      });
    });

    // 分析错误日志接口
    this.app.post('/api/analyze-error', async (req, res) => {
      try {
        const { errorLog, context, options } = req.body;

        // 验证必需参数
        if (!errorLog || errorLog.trim() === '') {
          return res.status(400).json({
            success: false,
            error: 'errorLog is required and cannot be empty'
          });
        }

        console.log(`Analyzing error log (${errorLog.length} characters)...`);

        // 调用AI分析逻辑
        const solution = await this.analyzeError(errorLog, context, options);

        res.json({
          success: true,
          solution: solution,
          timestamp: Date.now()
        });
      } catch (error) {
        console.error('Error analyzing log:', error);
        res.status(500).json({
          success: false,
          error: error.message || 'Internal server error'
        });
      }
    });

    // 批量分析接口
    this.app.post('/api/analyze-batch', async (req, res) => {
      try {
        const { errors } = req.body;

        if (!Array.isArray(errors) || errors.length === 0) {
          return res.status(400).json({
            success: false,
            error: 'errors array is required and cannot be empty'
          });
        }

        const results = await Promise.all(
          errors.map(async (item) => {
            try {
              const solution = await this.analyzeError(item.errorLog, item.context);
              return {
                success: true,
                id: item.id,
                solution: solution
              };
            } catch (error) {
              return {
                success: false,
                id: item.id,
                error: error.message
              };
            }
          })
        );

        res.json({
          success: true,
          results: results,
          timestamp: Date.now()
        });
      } catch (error) {
        console.error('Error in batch analysis:', error);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // 获取AI配置接口
    this.app.get('/api/config', (req, res) => {
      res.json({
        success: true,
        config: {
          maxLogLength: 50000,
          supportedLanguages: ['zh-CN', 'en-US'],
          features: ['error-analysis', 'solution-suggestion', 'code-fix']
        }
      });
    });

    // 404处理
    this.app.use((req, res) => {
      res.status(404).json({
        success: false,
        error: 'Endpoint not found'
      });
    });

    // 错误处理
    this.app.use((err, req, res, next) => {
      console.error('Server error:', err);
      res.status(500).json({
        success: false,
        error: 'Internal server error'
      });
    });
  }

  /**
   * 分析错误日志的核心逻辑
   * @param {string} errorLog - 错误日志内容
   * @param {object} context - 上下文信息（可选）
   * @param {object} options - 分析选项（可选）
   */
  async analyzeError(errorLog, context = {}, options = {}) {
    // 构建提示词
    const prompt = this.buildPrompt(errorLog, context, options);

    // 这里调用你的AI服务
    // 示例：调用OpenAI、Claude、或本地模型
    const solution = await this.callAIService(prompt, options);

    return solution;
  }

  /**
   * 构建AI提示词
   */
  buildPrompt(errorLog, context, options) {
    const language = options.language || 'zh-CN';
    
    let prompt = '';
    
    if (language === 'zh-CN') {
      prompt = `你是一个专业的软件调试助手。请分析以下错误日志并给出解决方案。

## 错误日志
\`\`\`
${errorLog}
\`\`\`

## 上下文信息
${JSON.stringify(context, null, 2)}

请按以下格式回答：

### 1. 错误分析
- 错误类型：
- 错误原因：
- 影响范围：

### 2. 解决方案
请提供2-3个可能的解决方案，按优先级排序：

#### 方案一（推荐）
- 步骤：
- 预计效果：
- 风险评估：

#### 方案二
- 步骤：
- 预计效果：
- 风险评估：

### 3. 预防措施
如何避免此类问题再次发生？

### 4. 相关资源
提供相关文档链接或参考资料（如有）。`;
    } else {
      prompt = `You are a professional software debugging assistant. Please analyze the following error log and provide solutions.

## Error Log
\`\`\`
${errorLog}
\`\`\`

## Context Information
${JSON.stringify(context, null, 2)}

Please provide:
1. Error Analysis (type, cause, impact)
2. Solutions (2-3 options, prioritized)
3. Prevention Measures
4. Related Resources`;
    }

    return prompt;
  }

  /**
   * 调用AI服务
   * 这里需要替换为你实际的AI服务调用逻辑
   */
  async callAIService(prompt, options = {}) {
    // TODO: 接入你的AI服务
    // 例如：OpenAI、Claude、本地模型等
    
    // 示例：模拟AI响应（实际使用时替换为真实API调用）
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(`### 1. 错误分析
- 错误类型：运行时异常
- 错误原因：空指针引用
- 影响范围：当前测试用例

### 2. 解决方案

#### 方案一（推荐）
- 步骤：
  1. 检查变量初始化
  2. 添加空值检查
  3. 使用可选链操作符
- 预计效果：完全解决问题
- 风险评估：低

#### 方案二
- 步骤：
  1. 重构代码结构
  2. 使用工厂模式确保对象创建
- 预计效果：从根本上避免问题
- 风险评估：中（需要较多改动）

### 3. 预防措施
- 启用严格的代码检查
- 添加单元测试覆盖边界情况
- 使用静态代码分析工具

### 4. 相关资源
- 参考官方文档进行最佳实践学习`);
      }, 1000);
    });

    // 真实的OpenAI调用示例（需要安装openai包）:
    /*
    const OpenAI = require('openai');
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });

    const completion = await openai.chat.completions.create({
      model: options.model || "gpt-4",
      messages: [
        {
          role: "system",
          content: "你是一个专业的软件调试助手。"
        },
        {
          role: "user",
          content: prompt
        }
      ],
      temperature: 0.7,
      max_tokens: 2000
    });

    return completion.choices[0].message.content;
    */
  }

  /**
   * 启动服务器
   */
  start() {
    return new Promise((resolve, reject) => {
      try {
        this.server = this.app.listen(this.port, () => {
          console.log('=================================');
          console.log('🚀 AI Assistant API Server Started');
          console.log(`📡 Listening on: http://localhost:${this.port}`);
          console.log(`🔑 API Token: ${this.apiToken}`);
          console.log('=================================');
          resolve();
        });

        this.server.on('error', (error) => {
          if (error.code === 'EADDRINUSE') {
            console.error(`❌ Port ${this.port} is already in use`);
          } else {
            console.error('❌ Server error:', error);
          }
          reject(error);
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 停止服务器
   */
  stop() {
    return new Promise((resolve) => {
      if (this.server) {
        this.server.close(() => {
          console.log('🛑 AI Assistant API Server Stopped');
          resolve();
        });
      } else {
        resolve();
      }
    });
  }
}

// 如果直接运行此文件，启动服务器
if (require.main === module) {
  const server = new AIApiServer({
    port: process.env.PORT || 8765,
    apiToken: process.env.API_TOKEN || 'your-secret-token'
  });

  server.start().catch((error) => {
    console.error('Failed to start server:', error);
    process.exit(1);
  });

  // 优雅关闭
  process.on('SIGINT', async () => {
    console.log('\nReceived SIGINT, shutting down gracefully...');
    await server.stop();
    process.exit(0);
  });
}

module.exports = AIApiServer;
