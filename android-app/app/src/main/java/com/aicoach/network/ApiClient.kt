package com.aicoach.network

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import java.util.concurrent.TimeUnit

/**
 * 网络API客户端
 */

// 数据模型
data class AppOpenEvent(
    val appName: String,
    val appCategory: String,
    val timestamp: Long
)

data class ApiResponse<T>(
    val success: Boolean,
    val intervention: Map<String, Any>?,
    val data: T? = null,
    val message: String? = null
)

data class Goal(
    val id: Int,
    val type: String,
    val target: Float,
    val current: Float,
    val progress: Float,
    val startDate: String,
    val endDate: String,
    val description: String
)

data class Achievement(
    val id: Int,
    val name: String,
    val unlockDate: String,
    val description: String,
    val icon: String
)

data class DashboardData(
    val productivityScore: Float,
    val activeGoals: Int,
    val totalAchievements: Int,
    val weeklyEntertainmentHours: Float,
    val todayStrategy: Map<String, Any>,
    val behaviorSummary: Map<String, Any>
)

// API接口定义
interface ApiService {
    
    @POST("api/events/app-opened")
    suspend fun reportAppOpened(@Body event: AppOpenEvent): ApiResponse<Nothing>
    
    @GET("api/goals/active")
    suspend fun getActiveGoals(): ApiResponse<List<Goal>>
    
    @GET("api/achievements")
    suspend fun getAchievements(): ApiResponse<List<Achievement>>
    
    @GET("api/dashboard")
    suspend fun getDashboardData(): ApiResponse<DashboardData>
    
    @GET("api/reports/weekly")
    suspend fun getWeeklyReport(): ApiResponse<Map<String, Any>>
    
    @POST("api/goals")
    suspend fun createGoal(@Body goal: Map<String, Any>): ApiResponse<Map<String, Any>>
    
    @GET("api/analysis/behavior")
    suspend fun getBehaviorAnalysis(@Query("days") days: Int = 7): ApiResponse<Map<String, Any>>
}

// API客户端单例
object ApiClient {
    
    // 修改为您的服务器地址
    private const val BASE_URL = "http://10.0.2.2:8000/"  // Android模拟器访问本机
    // 真机测试时改为: "http://YOUR_COMPUTER_IP:8000/"
    
    private val gson: Gson by lazy {
        GsonBuilder()
            .setLenient()
            .create()
    }
    
    private val loggingInterceptor by lazy {
        HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
    }
    
    private val okHttpClient by lazy {
        OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
    }
    
    private val retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
    }
    
    val apiService: ApiService by lazy {
        retrofit.create(ApiService::class.java)
    }
}
