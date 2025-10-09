/**
 * C# 测试工具 - AI服务管理器
 * 负责启动、停止和管理Electron AI助手服务
 */

using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using TestTool.AIIntegration;

namespace TestTool.UI
{
    /// <summary>
    /// AI服务管理器
    /// </summary>
    public class AIServiceManager
    {
        private readonly string _electronAppPath;
        private Process _electronProcess;
        private readonly AIAssistantClient _healthCheckClient;

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="electronAppPath">Electron应用程序路径</param>
        public AIServiceManager(string electronAppPath)
        {
            _electronAppPath = electronAppPath;
            _healthCheckClient = new AIAssistantClient();
        }

        /// <summary>
        /// 确保AI服务正在运行
        /// </summary>
        /// <returns>服务是否可用</returns>
        public async Task<bool> EnsureServiceRunningAsync()
        {
            // 先检查服务是否已经在运行
            if (await IsServiceRunningAsync())
            {
                return true;
            }

            // 尝试启动服务
            bool started = StartElectronApp();
            
            if (!started)
            {
                return false;
            }

            // 等待服务启动，最多等待30秒
            return await WaitForServiceStartAsync(timeout: 30);
        }

        /// <summary>
        /// 检查服务是否正在运行
        /// </summary>
        public async Task<bool> IsServiceRunningAsync()
        {
            try
            {
                return await _healthCheckClient.IsServiceAvailableAsync();
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// 启动Electron应用
        /// </summary>
        /// <returns>是否成功启动</returns>
        private bool StartElectronApp()
        {
            try
            {
                // 检查应用程序是否存在
                if (!File.Exists(_electronAppPath))
                {
                    Debug.WriteLine($"Electron应用不存在: {_electronAppPath}");
                    return false;
                }

                // 检查是否已有实例在运行
                string processName = Path.GetFileNameWithoutExtension(_electronAppPath);
                var existingProcesses = Process.GetProcessesByName(processName);
                
                if (existingProcesses.Length > 0)
                {
                    Debug.WriteLine($"Electron应用已在运行 (PID: {existingProcesses[0].Id})");
                    // 即使进程存在，也等待服务就绪
                    return true;
                }

                // 启动Electron应用
                var startInfo = new ProcessStartInfo
                {
                    FileName = _electronAppPath,
                    Arguments = "--api-server-mode", // 静默模式，仅运行API服务
                    UseShellExecute = false,
                    CreateNoWindow = false, // 开发时可以看到窗口，生产环境改为true
                    RedirectStandardOutput = false,
                    RedirectStandardError = false,
                    WorkingDirectory = Path.GetDirectoryName(_electronAppPath)
                };

                _electronProcess = Process.Start(startInfo);

                if (_electronProcess == null)
                {
                    Debug.WriteLine("无法启动Electron应用");
                    return false;
                }

                Debug.WriteLine($"Electron应用已启动 (PID: {_electronProcess.Id})");
                return true;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"启动Electron应用失败: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// 等待服务启动
        /// </summary>
        /// <param name="timeout">超时时间（秒）</param>
        /// <returns>服务是否成功启动</returns>
        private async Task<bool> WaitForServiceStartAsync(int timeout = 30)
        {
            var cts = new CancellationTokenSource(TimeSpan.FromSeconds(timeout));
            int attempt = 0;

            while (!cts.Token.IsCancellationRequested)
            {
                attempt++;
                
                try
                {
                    if (await IsServiceRunningAsync())
                    {
                        Debug.WriteLine($"服务启动成功 (尝试次数: {attempt})");
                        return true;
                    }
                }
                catch
                {
                    // 忽略错误，继续等待
                }

                // 每500ms检查一次
                await Task.Delay(500, cts.Token);
            }

            Debug.WriteLine($"等待服务启动超时 (尝试次数: {attempt})");
            return false;
        }

        /// <summary>
        /// 停止AI服务
        /// </summary>
        public void StopService()
        {
            try
            {
                if (_electronProcess != null && !_electronProcess.HasExited)
                {
                    _electronProcess.Kill();
                    _electronProcess.WaitForExit(5000);
                    _electronProcess.Dispose();
                    _electronProcess = null;
                    
                    Debug.WriteLine("Electron应用已停止");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"停止Electron应用失败: {ex.Message}");
            }
        }

        /// <summary>
        /// 重启AI服务
        /// </summary>
        public async Task<bool> RestartServiceAsync()
        {
            StopService();
            await Task.Delay(2000); // 等待完全停止
            return await EnsureServiceRunningAsync();
        }

        /// <summary>
        /// 获取服务状态信息
        /// </summary>
        public async Task<ServiceStatus> GetServiceStatusAsync()
        {
            var status = new ServiceStatus
            {
                IsRunning = await IsServiceRunningAsync(),
                ProcessId = _electronProcess?.Id ?? 0,
                AppPath = _electronAppPath
            };

            if (status.IsRunning)
            {
                try
                {
                    var config = await _healthCheckClient.GetConfigAsync();
                    if (config.Success)
                    {
                        status.Version = "1.0.0";
                        status.Features = config.Config?.Features;
                    }
                }
                catch
                {
                    // 忽略错误
                }
            }

            return status;
        }

        /// <summary>
        /// 清理资源
        /// </summary>
        public void Dispose()
        {
            _healthCheckClient?.Dispose();
            
            // 可选：是否在退出时关闭Electron应用
            // StopService();
        }
    }

    /// <summary>
    /// 服务状态信息
    /// </summary>
    public class ServiceStatus
    {
        /// <summary>
        /// 服务是否正在运行
        /// </summary>
        public bool IsRunning { get; set; }

        /// <summary>
        /// 进程ID
        /// </summary>
        public int ProcessId { get; set; }

        /// <summary>
        /// 应用程序路径
        /// </summary>
        public string AppPath { get; set; }

        /// <summary>
        /// 版本号
        /// </summary>
        public string Version { get; set; }

        /// <summary>
        /// 支持的功能列表
        /// </summary>
        public System.Collections.Generic.List<string> Features { get; set; }

        public override string ToString()
        {
            return IsRunning
                ? $"运行中 (PID: {ProcessId}, Version: {Version})"
                : "未运行";
        }
    }
}
