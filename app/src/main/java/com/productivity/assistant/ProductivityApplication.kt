package com.productivity.assistant

import android.app.Application
import androidx.room.Room
import com.productivity.assistant.data.database.ProductivityDatabase

class ProductivityApplication : Application() {
    
    val database: ProductivityDatabase by lazy {
        Room.databaseBuilder(
            applicationContext,
            ProductivityDatabase::class.java,
            "productivity_database"
        ).build()
    }
    
    override fun onCreate() {
        super.onCreate()
        instance = this
    }
    
    companion object {
        lateinit var instance: ProductivityApplication
            private set
    }
}
