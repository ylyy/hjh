#!/usr/bin/env python3
"""
启动脚本

使用方法:
    python run.py
    python run.py --port 8080
    python run.py --no-reload
"""
import argparse
import uvicorn
import sys
import os

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description="抖音直播AIGC后台")
    parser.add_argument("--host", default="0.0.0.0", help="绑定地址")
    parser.add_argument("--port", type=int, default=8000, help="端口号")
    parser.add_argument("--no-reload", action="store_true", help="禁用自动重载")
    parser.add_argument("--workers", type=int, default=1, help="工作进程数")
    
    args = parser.parse_args()
    
    print(f"""
╔═══════════════════════════════════════════════════════╗
║       🎮 抖音直播AIGC后台系统                          ║
╠═══════════════════════════════════════════════════════╣
║  首页:    http://{args.host}:{args.port}              
║  API文档: http://{args.host}:{args.port}/docs         
║  ReDoc:   http://{args.host}:{args.port}/redoc        
╚═══════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        workers=args.workers if args.no_reload else 1,
        log_level="info"
    )


if __name__ == "__main__":
    main()
