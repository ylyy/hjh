package com.productivity.assistant.ai

import android.content.Context
import android.graphics.Bitmap
import android.os.Environment
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

/**
 * 成就图片生成器 - 使用AI生成成就徽章
 */
class AchievementImageGenerator(private val context: Context) {
    
    private val aiService = AIService(context)
    
    /**
     * 为成就生成并保存图片
     */
    suspend fun generateAndSaveAchievementImage(
        achievementName: String,
        achievementDescription: String
    ): String? = withContext(Dispatchers.IO) {
        try {
            val bitmap = aiService.generateAchievementBadge(
                achievementName = achievementName,
                achievementDescription = achievementDescription
            )
            
            bitmap?.let { saveBitmapToFile(it, achievementName) }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
    
    /**
     * 保存Bitmap到文件
     */
    private fun saveBitmapToFile(bitmap: Bitmap, fileName: String): String? {
        return try {
            val imagesDir = File(context.getExternalFilesDir(Environment.DIRECTORY_PICTURES), "achievements")
            if (!imagesDir.exists()) {
                imagesDir.mkdirs()
            }
            
            val file = File(imagesDir, "${fileName}_${System.currentTimeMillis()}.png")
            FileOutputStream(file).use { out ->
                bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
            }
            
            file.absolutePath
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}
