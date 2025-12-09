"""
演示客户端

展示如何使用API和WebSocket连接
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"
ROOM_ID = "demo_room_123"


async def demo_api():
    """演示API调用"""
    async with aiohttp.ClientSession() as session:
        # 1. 创建直播间
        print("1. 创建直播间...")
        async with session.post(
            f"{BASE_URL}/api/rooms",
            json={
                "room_id": ROOM_ID,
                "name": "演示直播间"
            }
        ) as resp:
            result = await resp.json()
            print(f"   结果: {result}")
        
        # 2. 创建AI小说游戏
        print("\n2. 创建AI小说游戏...")
        async with session.post(
            f"{BASE_URL}/api/games/create",
            json={
                "room_id": ROOM_ID,
                "game_type": "story",
                "config": {
                    "style": "悬疑",
                    "title": "神秘事件",
                    "vote_duration": 10,
                    "min_votes": 1
                }
            }
        ) as resp:
            result = await resp.json()
            print(f"   结果: {result}")
        
        # 3. 启动游戏
        print("\n3. 启动游戏...")
        async with session.post(
            f"{BASE_URL}/api/games/{ROOM_ID}/start"
        ) as resp:
            result = await resp.json()
            print(f"   结果: {result}")
        
        # 4. 等待AI生成第一章
        print("\n4. 等待AI生成内容...")
        await asyncio.sleep(5)
        
        # 5. 获取游戏状态
        print("\n5. 获取游戏状态...")
        async with session.get(
            f"{BASE_URL}/api/games/{ROOM_ID}/state"
        ) as resp:
            result = await resp.json()
            print(f"   状态: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 6. 模拟投票
        print("\n6. 模拟投票...")
        for i, name in enumerate(["小明", "小红", "小刚"]):
            async with session.post(
                f"{BASE_URL}/api/danmu/inject",
                json={
                    "room_id": ROOM_ID,
                    "user_id": f"user_{i}",
                    "username": name,
                    "content": str((i % 3) + 1)  # 投票1, 2, 3
                }
            ) as resp:
                result = await resp.json()
                print(f"   {name} 投票: {result}")
        
        # 7. 获取投票状态
        print("\n7. 获取投票状态...")
        async with session.get(
            f"{BASE_URL}/api/games/{ROOM_ID}/vote"
        ) as resp:
            result = await resp.json()
            print(f"   投票: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 8. 停止游戏
        print("\n8. 停止游戏...")
        async with session.post(
            f"{BASE_URL}/api/games/{ROOM_ID}/stop"
        ) as resp:
            result = await resp.json()
            print(f"   结果: {json.dumps(result, indent=2, ensure_ascii=False)}")


async def demo_websocket():
    """演示WebSocket连接"""
    print("\n" + "="*50)
    print("WebSocket演示")
    print("="*50)
    
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(f"ws://localhost:8000/api/ws/room/{ROOM_ID}") as ws:
            print(f"已连接到房间: {ROOM_ID}")
            
            # 接收连接确认
            msg = await ws.receive()
            print(f"收到: {msg.data}")
            
            # 发送ping
            await ws.send_json({"type": "ping"})
            msg = await ws.receive()
            print(f"Ping响应: {msg.data}")
            
            # 获取游戏状态
            await ws.send_json({"type": "get_state"})
            msg = await ws.receive()
            print(f"游戏状态: {msg.data}")
            
            # 注入弹幕
            await ws.send_json({
                "type": "inject_danmu",
                "data": {
                    "username": "WebSocket用户",
                    "content": "选1"
                }
            })
            msg = await ws.receive()
            print(f"注入结果: {msg.data}")
            
            # 持续接收消息 (演示5秒)
            print("\n监听实时消息 (5秒)...")
            try:
                async with asyncio.timeout(5):
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            print(f"实时消息: {data['type']}")
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break
            except asyncio.TimeoutError:
                pass
            
            print("WebSocket演示结束")


async def demo_puzzle_game():
    """演示解谜游戏"""
    print("\n" + "="*50)
    print("AI解谜游戏演示")
    print("="*50)
    
    async with aiohttp.ClientSession() as session:
        # 创建解谜游戏
        print("\n1. 创建解谜游戏...")
        async with session.post(
            f"{BASE_URL}/api/games/create",
            json={
                "room_id": ROOM_ID,
                "game_type": "puzzle",
                "config": {
                    "theme": "趣味问答",
                    "difficulty": "easy",
                    "vote_duration": 10,
                    "puzzle_count": 3
                }
            }
        ) as resp:
            result = await resp.json()
            print(f"   结果: {result}")
        
        # 启动游戏
        print("\n2. 启动游戏...")
        async with session.post(
            f"{BASE_URL}/api/games/{ROOM_ID}/start"
        ) as resp:
            result = await resp.json()
            print(f"   结果: {result}")
        
        # 等待生成第一题
        await asyncio.sleep(3)
        
        # 获取当前谜题
        print("\n3. 获取当前谜题...")
        async with session.get(
            f"{BASE_URL}/api/games/{ROOM_ID}/puzzle/current"
        ) as resp:
            result = await resp.json()
            print(f"   谜题: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 模拟多人投票
        print("\n4. 模拟投票...")
        voters = [
            ("user_1", "玩家A", "1"),
            ("user_2", "玩家B", "2"),
            ("user_3", "玩家C", "1"),
            ("user_4", "玩家D", "1"),
        ]
        for user_id, username, vote in voters:
            async with session.post(
                f"{BASE_URL}/api/danmu/inject",
                json={
                    "room_id": ROOM_ID,
                    "user_id": user_id,
                    "username": username,
                    "content": vote
                }
            ) as resp:
                print(f"   {username} 选择了 {vote}")
        
        # 等待投票结束
        await asyncio.sleep(12)
        
        # 获取排行榜
        print("\n5. 获取排行榜...")
        async with session.get(
            f"{BASE_URL}/api/games/{ROOM_ID}/puzzle/leaderboard"
        ) as resp:
            result = await resp.json()
            print(f"   排行榜: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 停止游戏
        print("\n6. 停止游戏...")
        async with session.post(
            f"{BASE_URL}/api/games/{ROOM_ID}/stop"
        ) as resp:
            result = await resp.json()
            print(f"   最终结果: {json.dumps(result, indent=2, ensure_ascii=False)}")


async def main():
    """主函数"""
    print("="*50)
    print("抖音直播AIGC后台 - 演示客户端")
    print("="*50)
    print(f"服务地址: {BASE_URL}")
    print(f"演示房间: {ROOM_ID}")
    
    try:
        # API演示
        await demo_api()
        
        # WebSocket演示
        # await demo_websocket()
        
        # 解谜游戏演示
        # await demo_puzzle_game()
        
    except aiohttp.ClientError as e:
        print(f"\n连接错误: {e}")
        print("请确保服务已启动: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
