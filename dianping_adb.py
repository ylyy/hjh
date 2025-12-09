#!/usr/bin/env python3
"""
大众点评"免费试"自动点击脚本
使用 uiautomator2 通过电脑控制手机

安装依赖:
    pip install uiautomator2

使用方法:
    1. 手机开启USB调试，连接电脑
    2. 打开大众点评"免费试"页面
    3. 运行: python dianping_adb.py
"""

import uiautomator2 as u2
import time
import sys

# 配置
CONFIG = {
    'click_delay': 1.5,      # 点击间隔(秒)
    'scroll_delay': 1.0,     # 滑动后等待(秒)
    'max_scroll': 50,        # 最大滑动次数
    'apply_keywords': ['免费申请', '立即申请', '马上申请', '我要申请', '申请试用', '免费试用', '立即领取'],
    'skip_keywords': ['已申请', '已结束', '已抢光', '已领取', '名额已满', '已参与'],
    'confirm_keywords': ['确定', '确认', '知道了', '好的', '提交'],
}


def connect_device():
    """连接设备"""
    print("正在连接设备...")
    try:
        d = u2.connect()  # 自动连接USB设备
        print(f"已连接: {d.info['productName']}")
        return d
    except Exception as e:
        print(f"连接失败: {e}")
        print("请确保:")
        print("  1. 手机已开启USB调试")
        print("  2. 已授权电脑调试")
        print("  3. ADB已正确安装")
        sys.exit(1)


def click_apply_buttons(d):
    """点击所有申请按钮"""
    clicked = 0
    
    for keyword in CONFIG['apply_keywords']:
        # 查找所有匹配的元素
        elements = d(textContains=keyword)
        count = elements.count
        
        for i in range(count):
            try:
                el = elements[i]
                if not el.exists:
                    continue
                
                # 获取元素信息
                info = el.info
                text = info.get('text', '')
                
                # 检查是否应该跳过
                skip = False
                for skip_kw in CONFIG['skip_keywords']:
                    if skip_kw in text:
                        skip = True
                        break
                
                if skip:
                    continue
                
                # 检查是否可见
                bounds = info.get('bounds', {})
                if bounds:
                    # 点击
                    print(f"点击: {text or keyword}")
                    el.click()
                    clicked += 1
                    time.sleep(CONFIG['click_delay'])
                    
                    # 处理弹窗
                    handle_popup(d)
                    
            except Exception as e:
                print(f"点击出错: {e}")
                continue
    
    return clicked


def handle_popup(d):
    """处理弹窗"""
    time.sleep(0.5)
    
    for keyword in CONFIG['confirm_keywords']:
        try:
            btn = d(text=keyword)
            if btn.exists(timeout=0.3):
                print(f"关闭弹窗: {keyword}")
                btn.click()
                time.sleep(0.3)
        except:
            pass


def scroll_down(d):
    """向下滑动"""
    d.swipe_ext("up", scale=0.5)


def main():
    print("=" * 40)
    print("大众点评 免费试 自动申请脚本")
    print("=" * 40)
    
    # 连接设备
    d = connect_device()
    
    print("\n请确保已打开大众点评'免费试'页面")
    print("3秒后开始...")
    time.sleep(3)
    
    total_clicked = 0
    scroll_count = 0
    no_new_count = 0
    
    while scroll_count < CONFIG['max_scroll']:
        # 点击当前页面的按钮
        clicked = click_apply_buttons(d)
        total_clicked += clicked
        
        if clicked == 0:
            no_new_count += 1
        else:
            no_new_count = 0
            print(f"本轮点击: {clicked}, 累计: {total_clicked}")
        
        # 连续3次没有新按钮，可能到底了
        if no_new_count >= 3:
            print("未发现新按钮，可能已完成")
            break
        
        # 滑动加载更多
        scroll_down(d)
        time.sleep(CONFIG['scroll_delay'])
        scroll_count += 1
    
    print("\n" + "=" * 40)
    print(f"完成！共申请: {total_clicked} 个")
    print(f"滑动次数: {scroll_count}")
    print("=" * 40)


if __name__ == '__main__':
    main()
