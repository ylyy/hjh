/**
 * C# 测试工具 - AI助手客户端
 * 用于与Electron AI助手API服务器通信
 */

using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace TestTool.AIIntegration
{
    /// <summary>
    /// AI助手客户端
    /// </summary>
    public class AIAssistantClient : IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;
        private readonly string _apiToken;

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="baseUrl">API服务器地址，默认 http://localhost:8765</param>
        /// <param name="apiToken">API认证令牌</param>
        /// <param name="timeout">请求超时时间（秒），默认30秒</param>
        public AIAssistantClient(
            string baseUrl = "http://localhost:8765",
            string apiToken = "your-secret-token",
            int timeout = 30)
        {
            _baseUrl = baseUrl.TrimEnd('/');
            _apiToken = apiToken;

            _httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromSeconds(timeout)
            };

            // 添加认证头
            _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_apiToken}");
        }

        /// <summary>
        /// 检查AI服务是否可用
        /// </summary>
        public async Task<bool> IsServiceAvailableAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync($"{_baseUrl}/api/health");
                if (!response.IsSuccessStatusCode)
                {
                    return false;
                }

                var json = await response.Content.ReadAsStringAsync();
                var health = JsonConvert.DeserializeObject<HealthResponse>(json);
                return health?.Status == "ok";
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Health check failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// 分析错误日志
        /// </summary>
        /// <param name="errorLog">错误日志内容</param>
        /// <param name="context">上下文信息（可选）</param>
        /// <param name="options">分析选项（可选）</param>
        /// <returns>AI分析结果</returns>
        public async Task<AISolutionResponse> AnalyzeErrorAsync(
            string errorLog,
            Dictionary<string, object> context = null,
            AnalysisOptions options = null)
        {
            if (string.IsNullOrWhiteSpace(errorLog))
            {
                return new AISolutionResponse
                {
                    Success = false,
                    Error = "错误日志不能为空"
                };
            }

            var requestData = new
            {
                errorLog = errorLog,
                context = context ?? new Dictionary<string, object>(),
                options = options ?? new AnalysisOptions()
            };

            try
            {
                var json = JsonConvert.SerializeObject(requestData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync($"{_baseUrl}/api/analyze-error", content);
                
                var responseJson = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    var errorResponse = JsonConvert.DeserializeObject<ErrorResponse>(responseJson);
                    return new AISolutionResponse
                    {
                        Success = false,
                        Error = errorResponse?.Error ?? $"HTTP {response.StatusCode}"
                    };
                }

                return JsonConvert.DeserializeObject<AISolutionResponse>(responseJson);
            }
            catch (TaskCanceledException)
            {
                return new AISolutionResponse
                {
                    Success = false,
                    Error = "请求超时，请检查AI服务是否正常运行"
                };
            }
            catch (HttpRequestException ex)
            {
                return new AISolutionResponse
                {
                    Success = false,
                    Error = $"网络错误: {ex.Message}"
                };
            }
            catch (Exception ex)
            {
                return new AISolutionResponse
                {
                    Success = false,
                    Error = $"未知错误: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// 批量分析多个错误日志
        /// </summary>
        /// <param name="errors">错误日志列表</param>
        /// <returns>批量分析结果</returns>
        public async Task<BatchAnalysisResponse> AnalyzeBatchAsync(List<ErrorItem> errors)
        {
            if (errors == null || errors.Count == 0)
            {
                return new BatchAnalysisResponse
                {
                    Success = false,
                    Error = "错误列表不能为空"
                };
            }

            var requestData = new { errors = errors };

            try
            {
                var json = JsonConvert.SerializeObject(requestData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync($"{_baseUrl}/api/analyze-batch", content);
                var responseJson = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    var errorResponse = JsonConvert.DeserializeObject<ErrorResponse>(responseJson);
                    return new BatchAnalysisResponse
                    {
                        Success = false,
                        Error = errorResponse?.Error ?? $"HTTP {response.StatusCode}"
                    };
                }

                return JsonConvert.DeserializeObject<BatchAnalysisResponse>(responseJson);
            }
            catch (Exception ex)
            {
                return new BatchAnalysisResponse
                {
                    Success = false,
                    Error = $"批量分析失败: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// 获取AI服务配置信息
        /// </summary>
        public async Task<ConfigResponse> GetConfigAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync($"{_baseUrl}/api/config");
                var json = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<ConfigResponse>(json);
            }
            catch (Exception ex)
            {
                return new ConfigResponse
                {
                    Success = false,
                    Error = ex.Message
                };
            }
        }

        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }

    #region 数据模型

    /// <summary>
    /// 健康检查响应
    /// </summary>
    public class HealthResponse
    {
        [JsonProperty("status")]
        public string Status { get; set; }

        [JsonProperty("service")]
        public string Service { get; set; }

        [JsonProperty("version")]
        public string Version { get; set; }

        [JsonProperty("timestamp")]
        public long Timestamp { get; set; }
    }

    /// <summary>
    /// AI分析响应
    /// </summary>
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

    /// <summary>
    /// 错误响应
    /// </summary>
    public class ErrorResponse
    {
        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("error")]
        public string Error { get; set; }
    }

    /// <summary>
    /// 分析选项
    /// </summary>
    public class AnalysisOptions
    {
        [JsonProperty("language")]
        public string Language { get; set; } = "zh-CN";

        [JsonProperty("model")]
        public string Model { get; set; } = "gpt-4";

        [JsonProperty("detailLevel")]
        public string DetailLevel { get; set; } = "normal"; // normal, detailed, brief
    }

    /// <summary>
    /// 错误项（用于批量分析）
    /// </summary>
    public class ErrorItem
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("errorLog")]
        public string ErrorLog { get; set; }

        [JsonProperty("context")]
        public Dictionary<string, object> Context { get; set; }
    }

    /// <summary>
    /// 批量分析响应
    /// </summary>
    public class BatchAnalysisResponse
    {
        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("results")]
        public List<BatchResultItem> Results { get; set; }

        [JsonProperty("error")]
        public string Error { get; set; }

        [JsonProperty("timestamp")]
        public long Timestamp { get; set; }
    }

    /// <summary>
    /// 批量分析结果项
    /// </summary>
    public class BatchResultItem
    {
        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("solution")]
        public string Solution { get; set; }

        [JsonProperty("error")]
        public string Error { get; set; }
    }

    /// <summary>
    /// 配置响应
    /// </summary>
    public class ConfigResponse
    {
        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("config")]
        public AIConfig Config { get; set; }

        [JsonProperty("error")]
        public string Error { get; set; }
    }

    /// <summary>
    /// AI配置
    /// </summary>
    public class AIConfig
    {
        [JsonProperty("maxLogLength")]
        public int MaxLogLength { get; set; }

        [JsonProperty("supportedLanguages")]
        public List<string> SupportedLanguages { get; set; }

        [JsonProperty("features")]
        public List<string> Features { get; set; }
    }

    #endregion
}
