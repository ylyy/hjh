/**
 * C# 测试工具 - 错误日志查看器示例
 * 展示如何在UI中集成AI分析功能
 */

using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Threading.Tasks;
using System.Windows.Forms;
using TestTool.AIIntegration;

namespace TestTool.UI
{
    /// <summary>
    /// 错误日志查看器窗体
    /// </summary>
    public partial class ErrorLogViewer : Form
    {
        private AIAssistantClient _aiClient;
        private AIServiceManager _serviceManager;

        // UI控件
        private TextBox _errorLogTextBox;
        private Button _analyzeButton;
        private Button _copyButton;
        private Button _saveButton;
        private RichTextBox _solutionTextBox;
        private ProgressBar _progressBar;
        private Label _statusLabel;
        private Panel _headerPanel;
        private Panel _contentPanel;
        private SplitContainer _splitContainer;

        public ErrorLogViewer()
        {
            InitializeComponent();
            InitializeAI();
            InitializeUI();
        }

        /// <summary>
        /// 初始化AI客户端
        /// </summary>
        private void InitializeAI()
        {
            // 从配置文件读取设置
            var config = LoadConfig();
            
            _aiClient = new AIAssistantClient(
                baseUrl: config.ApiBaseUrl,
                apiToken: config.ApiToken,
                timeout: config.Timeout
            );

            _serviceManager = new AIServiceManager(config.ElectronAppPath);
        }

        /// <summary>
        /// 初始化UI控件
        /// </summary>
        private void InitializeUI()
        {
            this.Text = "错误日志分析器 - AI助手";
            this.Size = new Size(1200, 800);
            this.MinimumSize = new Size(800, 600);
            this.StartPosition = FormStartPosition.CenterScreen;

            // 头部面板
            _headerPanel = new Panel
            {
                Dock = DockStyle.Top,
                Height = 60,
                BackColor = Color.FromArgb(45, 45, 48)
            };

            // AI分析按钮
            _analyzeButton = new Button
            {
                Text = "🤖 AI智能分析",
                Location = new Point(20, 15),
                Size = new Size(150, 35),
                Font = new Font("微软雅黑", 10F, FontStyle.Bold),
                BackColor = Color.FromArgb(0, 122, 204),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Cursor = Cursors.Hand
            };
            _analyzeButton.FlatAppearance.BorderSize = 0;
            _analyzeButton.Click += async (s, e) => await AnalyzeErrorAsync();

            // 复制按钮
            _copyButton = new Button
            {
                Text = "📋 复制方案",
                Location = new Point(180, 15),
                Size = new Size(120, 35),
                Font = new Font("微软雅黑", 9F),
                BackColor = Color.FromArgb(60, 60, 60),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Cursor = Cursors.Hand,
                Enabled = false
            };
            _copyButton.FlatAppearance.BorderSize = 0;
            _copyButton.Click += CopyButton_Click;

            // 保存按钮
            _saveButton = new Button
            {
                Text = "💾 保存分析",
                Location = new Point(310, 15),
                Size = new Size(120, 35),
                Font = new Font("微软雅黑", 9F),
                BackColor = Color.FromArgb(60, 60, 60),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Cursor = Cursors.Hand,
                Enabled = false
            };
            _saveButton.FlatAppearance.BorderSize = 0;
            _saveButton.Click += SaveButton_Click;

            // 状态标签
            _statusLabel = new Label
            {
                Text = "就绪",
                Location = new Point(450, 20),
                AutoSize = true,
                Font = new Font("微软雅黑", 9F),
                ForeColor = Color.LightGray
            };

            _headerPanel.Controls.AddRange(new Control[] {
                _analyzeButton, _copyButton, _saveButton, _statusLabel
            });

            // 内容面板
            _contentPanel = new Panel
            {
                Dock = DockStyle.Fill
            };

            // 分割容器
            _splitContainer = new SplitContainer
            {
                Dock = DockStyle.Fill,
                Orientation = Orientation.Horizontal,
                SplitterDistance = 300,
                BorderStyle = BorderStyle.FixedSingle
            };

            // 上半部分：错误日志输入
            var errorLogLabel = new Label
            {
                Text = "错误日志内容：",
                Location = new Point(10, 10),
                AutoSize = true,
                Font = new Font("微软雅黑", 9F, FontStyle.Bold)
            };

            _errorLogTextBox = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Both,
                Font = new Font("Consolas", 9F),
                Location = new Point(10, 35),
                Size = new Size(_splitContainer.Panel1.Width - 20, _splitContainer.Panel1.Height - 45),
                Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right,
                BackColor = Color.FromArgb(30, 30, 30),
                ForeColor = Color.LightGray,
                BorderStyle = BorderStyle.FixedSingle
            };

            _splitContainer.Panel1.Controls.AddRange(new Control[] {
                errorLogLabel, _errorLogTextBox
            });

            // 下半部分：AI分析结果
            var solutionLabel = new Label
            {
                Text = "AI分析结果：",
                Location = new Point(10, 10),
                AutoSize = true,
                Font = new Font("微软雅黑", 9F, FontStyle.Bold)
            };

            _solutionTextBox = new RichTextBox
            {
                Location = new Point(10, 35),
                Size = new Size(_splitContainer.Panel2.Width - 20, _splitContainer.Panel2.Height - 45),
                Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right,
                Font = new Font("微软雅黑", 9.5F),
                ReadOnly = true,
                BackColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle
            };

            _splitContainer.Panel2.Controls.AddRange(new Control[] {
                solutionLabel, _solutionTextBox
            });

            _contentPanel.Controls.Add(_splitContainer);

            // 进度条
            _progressBar = new ProgressBar
            {
                Dock = DockStyle.Bottom,
                Height = 3,
                Style = ProgressBarStyle.Marquee,
                Visible = false
            };

            // 添加到窗体
            this.Controls.Add(_contentPanel);
            this.Controls.Add(_headerPanel);
            this.Controls.Add(_progressBar);
        }

        /// <summary>
        /// 分析错误日志
        /// </summary>
        private async Task AnalyzeErrorAsync()
        {
            string errorLog = _errorLogTextBox.Text.Trim();

            if (string.IsNullOrWhiteSpace(errorLog))
            {
                MessageBox.Show(
                    "请先输入错误日志内容",
                    "提示",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
                return;
            }

            // 禁用按钮，显示进度
            _analyzeButton.Enabled = false;
            _analyzeButton.Text = "分析中...";
            _progressBar.Visible = true;
            _statusLabel.Text = "正在连接AI服务...";
            _statusLabel.ForeColor = Color.Yellow;
            _solutionTextBox.Clear();

            try
            {
                // 检查服务是否可用
                bool serviceAvailable = await _aiClient.IsServiceAvailableAsync();
                
                if (!serviceAvailable)
                {
                    _statusLabel.Text = "AI服务未运行，正在尝试启动...";
                    
                    bool started = await _serviceManager.EnsureServiceRunningAsync();
                    
                    if (!started)
                    {
                        MessageBox.Show(
                            "无法连接到AI助手服务。\n\n请确保：\n" +
                            "1. AI助手应用已安装\n" +
                            "2. 配置文件中的路径正确\n" +
                            "3. 防火墙未阻止连接",
                            "服务不可用",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Warning
                        );
                        return;
                    }

                    // 等待服务启动
                    await Task.Delay(2000);
                }

                _statusLabel.Text = "正在分析错误日志...";

                // 收集上下文信息
                var context = new Dictionary<string, object>
                {
                    ["timestamp"] = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
                    ["testCase"] = GetCurrentTestCaseName(),
                    ["environment"] = GetEnvironmentInfo(),
                    ["user"] = Environment.UserName,
                    ["machine"] = Environment.MachineName
                };

                // 调用AI分析
                var response = await _aiClient.AnalyzeErrorAsync(
                    errorLog,
                    context,
                    new AnalysisOptions
                    {
                        Language = "zh-CN",
                        DetailLevel = "detailed"
                    }
                );

                if (response.Success)
                {
                    // 显示分析结果
                    DisplaySolution(response.Solution);
                    
                    _statusLabel.Text = "分析完成";
                    _statusLabel.ForeColor = Color.LightGreen;
                    
                    // 启用复制和保存按钮
                    _copyButton.Enabled = true;
                    _saveButton.Enabled = true;

                    // 自动保存到日志
                    await SaveAnalysisToLogAsync(errorLog, response.Solution);
                }
                else
                {
                    _statusLabel.Text = "分析失败";
                    _statusLabel.ForeColor = Color.Red;
                    
                    MessageBox.Show(
                        $"AI分析失败：{response.Error}",
                        "错误",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error
                    );
                }
            }
            catch (Exception ex)
            {
                _statusLabel.Text = "发生错误";
                _statusLabel.ForeColor = Color.Red;
                
                MessageBox.Show(
                    $"分析过程中发生错误：\n{ex.Message}",
                    "错误",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
            finally
            {
                // 恢复按钮状态
                _analyzeButton.Enabled = true;
                _analyzeButton.Text = "🤖 AI智能分析";
                _progressBar.Visible = false;
            }
        }

        /// <summary>
        /// 显示解决方案（带格式）
        /// </summary>
        private void DisplaySolution(string solution)
        {
            _solutionTextBox.Clear();
            _solutionTextBox.Text = solution;

            // 简单的语法高亮
            HighlightSolution();
        }

        /// <summary>
        /// 高亮显示解决方案
        /// </summary>
        private void HighlightSolution()
        {
            string[] keywords = { "###", "####", "- ", "1.", "2.", "3." };
            
            foreach (string keyword in keywords)
            {
                int index = 0;
                while ((index = _solutionTextBox.Text.IndexOf(keyword, index)) != -1)
                {
                    _solutionTextBox.Select(index, keyword.Length);
                    _solutionTextBox.SelectionColor = Color.Blue;
                    _solutionTextBox.SelectionFont = new Font(_solutionTextBox.Font, FontStyle.Bold);
                    index += keyword.Length;
                }
            }

            _solutionTextBox.Select(0, 0);
        }

        /// <summary>
        /// 复制按钮点击
        /// </summary>
        private void CopyButton_Click(object sender, EventArgs e)
        {
            if (!string.IsNullOrWhiteSpace(_solutionTextBox.Text))
            {
                Clipboard.SetText(_solutionTextBox.Text);
                MessageBox.Show("解决方案已复制到剪贴板", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        /// <summary>
        /// 保存按钮点击
        /// </summary>
        private void SaveButton_Click(object sender, EventArgs e)
        {
            var saveDialog = new SaveFileDialog
            {
                Filter = "文本文件 (*.txt)|*.txt|Markdown文件 (*.md)|*.md",
                FileName = $"AI分析_{DateTime.Now:yyyyMMdd_HHmmss}.txt"
            };

            if (saveDialog.ShowDialog() == DialogResult.OK)
            {
                try
                {
                    string content = $"错误日志：\n{_errorLogTextBox.Text}\n\n" +
                                   $"AI分析结果：\n{_solutionTextBox.Text}\n\n" +
                                   $"生成时间：{DateTime.Now}";
                    
                    File.WriteAllText(saveDialog.FileName, content);
                    MessageBox.Show("保存成功", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"保存失败：{ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }

        /// <summary>
        /// 保存分析结果到日志
        /// </summary>
        private async Task SaveAnalysisToLogAsync(string errorLog, string solution)
        {
            await Task.Run(() =>
            {
                try
                {
                    string logDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "AIAnalysisLogs");
                    Directory.CreateDirectory(logDir);

                    string logFile = Path.Combine(logDir, $"analysis_{DateTime.Now:yyyyMMdd}.log");
                    
                    string logEntry = $"\n=== {DateTime.Now:yyyy-MM-dd HH:mm:ss} ===\n" +
                                    $"错误日志：\n{errorLog}\n\n" +
                                    $"AI分析：\n{solution}\n" +
                                    new string('=', 80) + "\n";

                    File.AppendAllText(logFile, logEntry);
                }
                catch
                {
                    // 静默失败
                }
            });
        }

        /// <summary>
        /// 获取当前测试用例名称
        /// </summary>
        private string GetCurrentTestCaseName()
        {
            // TODO: 从实际测试框架获取
            return "TestCase_001";
        }

        /// <summary>
        /// 获取环境信息
        /// </summary>
        private object GetEnvironmentInfo()
        {
            return new
            {
                OS = Environment.OSVersion.ToString(),
                CLR = Environment.Version.ToString(),
                Is64Bit = Environment.Is64BitOperatingSystem,
                ProcessorCount = Environment.ProcessorCount
            };
        }

        /// <summary>
        /// 加载配置
        /// </summary>
        private AIConfig LoadConfig()
        {
            // TODO: 从配置文件读取
            return new AIConfig
            {
                ApiBaseUrl = "http://localhost:8765",
                ApiToken = "your-secret-token",
                Timeout = 30,
                ElectronAppPath = @"C:\Program Files\AIAssistant\AIAssistant.exe"
            };
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            _aiClient?.Dispose();
            base.OnFormClosing(e);
        }
    }

    /// <summary>
    /// AI配置类
    /// </summary>
    public class AIConfig
    {
        public string ApiBaseUrl { get; set; }
        public string ApiToken { get; set; }
        public int Timeout { get; set; }
        public string ElectronAppPath { get; set; }
    }
}
