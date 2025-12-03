package com.productivity.assistant.ai.modelscope

import android.util.Log
import com.productivity.assistant.ai.modelscope.api.*
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import java.util.concurrent.TimeUnit

/**
 * ModelScope API客户端
 */
class ModelScopeClient {
    
    private val api: ModelScopeApi
    
    init {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        
        val client = OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(ModelScopeConfig.REQUEST_TIMEOUT, TimeUnit.SECONDS)
            .readTimeout(ModelScopeConfig.REQUEST_TIMEOUT, TimeUnit.SECONDS)
            .writeTimeout(ModelScopeConfig.REQUEST_TIMEOUT, TimeUnit.SECONDS)
            .build()
        
        val retrofit = Retrofit.Builder()
            .baseUrl(ModelScopeConfig.BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        
        api = retrofit.create(ModelScopeApi::class.java)
    }
    
    /**
     * 生成文本
     */
    suspend fun generateText(
        prompt: String,
        maxTokens: Int = 512,
        temperature: Double = 0.7
    ): Result<String> {
        return try {
            val request = TextGenerationRequest(
                input = prompt,
                parameters = TextGenerationParameters(
                    max_new_tokens = maxTokens,
                    temperature = temperature
                )
            )
            
            val response = api.generateText(
                ModelScopeConfig.TEXT_GENERATION_MODEL,
                request
            )
            
            if (response.isSuccessful) {
                val body = response.body()
                val output = body?.output
                if (output != null) {
                    Result.success(output)
                } else {
                    Result.failure(Exception("响应体为空"))
                }
            } else {
                Result.failure(Exception("请求失败: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Log.e("ModelScopeClient", "文本生成失败", e)
            Result.failure(e)
        }
    }
    
    /**
     * 生成图片
     */
    suspend fun generateImage(
        prompt: String,
        width: Int = 512,
        height: Int = 512
    ): Result<List<String>> {
        return try {
            val request = ImageGenerationRequest(
                input = prompt,
                parameters = ImageGenerationParameters(
                    width = width,
                    height = height
                )
            )
            
            val response = api.generateImage(
                ModelScopeConfig.IMAGE_GENERATION_MODEL,
                request
            )
            
            if (response.isSuccessful) {
                val body = response.body()
                val images = body?.output?.images
                if (images != null && images.isNotEmpty()) {
                    Result.success(images)
                } else {
                    Result.failure(Exception("未生成图片"))
                }
            } else {
                Result.failure(Exception("请求失败: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Log.e("ModelScopeClient", "图片生成失败", e)
            Result.failure(e)
        }
    }
}
