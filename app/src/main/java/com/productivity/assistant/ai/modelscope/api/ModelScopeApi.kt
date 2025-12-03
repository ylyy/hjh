package com.productivity.assistant.ai.modelscope.api

import com.productivity.assistant.ai.modelscope.ModelScopeConfig
import retrofit2.Response
import retrofit2.http.*

/**
 * ModelScope API接口定义
 */
interface ModelScopeApi {
    
    /**
     * 文本生成
     * ModelScope API格式：POST /api-inference/v1/models/{model}/inference
     */
    @POST("models/{model}/inference")
    @Headers("Content-Type: application/json")
    suspend fun generateText(
        @Path("model") model: String,
        @Header("Authorization") authorization: String = "Bearer ${ModelScopeConfig.API_TOKEN}",
        @Body request: TextGenerationRequest
    ): Response<TextGenerationResponse>
    
    /**
     * 图片生成
     */
    @POST("models/{model}/inference")
    @Headers("Content-Type: application/json")
    suspend fun generateImage(
        @Path("model") model: String,
        @Header("Authorization") authorization: String = "Bearer ${ModelScopeConfig.API_TOKEN}",
        @Body request: ImageGenerationRequest
    ): Response<ImageGenerationResponse>
}

/**
 * 文本生成请求
 */
data class TextGenerationRequest(
    val input: String,
    val parameters: TextGenerationParameters = TextGenerationParameters()
)

data class TextGenerationParameters(
    val max_new_tokens: Int = 512,
    val temperature: Double = 0.7,
    val top_p: Double = 0.9,
    val top_k: Int = 50,
    val repetition_penalty: Double = 1.1
)

/**
 * 文本生成响应
 */
data class TextGenerationResponse(
    val output: String?,
    val request_id: String?,
    val usage: TokenUsage?
)

data class TokenUsage(
    val input_tokens: Int,
    val output_tokens: Int,
    val total_tokens: Int
)

/**
 * 图片生成请求
 */
data class ImageGenerationRequest(
    val input: String,  // 提示词
    val parameters: ImageGenerationParameters = ImageGenerationParameters()
)

data class ImageGenerationParameters(
    val width: Int = 512,
    val height: Int = 512,
    val num_inference_steps: Int = 20,
    val guidance_scale: Double = 7.5
)

/**
 * 图片生成响应
 */
data class ImageGenerationResponse(
    val output: ImageOutput?,
    val request_id: String?
)

data class ImageOutput(
    val images: List<String>?  // Base64编码的图片数据或URL
)
