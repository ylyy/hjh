package com.productivity.assistant.ai.modelscope

/**
 * ModelScope API配置
 */
object ModelScopeConfig {
    // API Token
    const val API_TOKEN = "ms-8d334afb-84a5-4f92-9e23-eb027737ca1f"
    
    // API基础URL
    const val BASE_URL = "https://api.modelscope.cn/api-inference/v1/"
    
    // 文本生成模型
    const val TEXT_GENERATION_MODEL = "deepseek-ai/DeepSeek-V3.2"
    
    // 图片生成模型
    const val IMAGE_GENERATION_MODEL = "Tongyi-MAI/Z-Image-Turbo"
    
    // 请求超时时间（秒）
    const val REQUEST_TIMEOUT = 30L
}
