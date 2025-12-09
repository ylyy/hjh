# 大众点评"免费试"自动点击脚本

自动点击大众点评App中"免费试"页面的所有申请按钮。

---

## 📁 脚本文件

| 文件 | 适用工具 | 说明 |
|------|----------|------|
| `dianping_hamibot.js` | Hamibot / Auto.js Pro | 手机端运行 |
| `dianping_adb.py` | Python + uiautomator2 | 电脑控制手机 |

---

## 方案一：Hamibot（推荐）⭐

Hamibot 是目前最活跃的 Auto.js 替代品，免费使用。

### 安装步骤

1. **下载 Hamibot**
   - 官网：https://hamibot.com/
   - 或应用商店搜索 "Hamibot"

2. **注册账号并登录**

3. **开启无障碍服务**
   - 设置 → 无障碍 → Hamibot → 开启

4. **导入脚本**
   - 打开 Hamibot → 开发 → 新建脚本
   - 粘贴 `dianping_hamibot.js` 内容

5. **运行**
   - 打开大众点评 → 进入"免费试"页面
   - 回到 Hamibot 运行脚本

---

## 方案二：Python + uiautomator2（电脑控制）

通过电脑 USB 连接手机运行，更稳定可靠。

### 安装步骤

1. **安装 Python 3**
   ```bash
   # Windows: 下载 https://python.org
   # Mac: brew install python3
   # Linux: sudo apt install python3
   ```

2. **安装依赖**
   ```bash
   pip install uiautomator2
   ```

3. **手机开启 USB 调试**
   - 设置 → 关于手机 → 连点7次版本号 → 开启开发者模式
   - 设置 → 开发者选项 → USB调试 → 开启

4. **连接手机到电脑**
   - 用数据线连接
   - 手机上点击"允许调试"

5. **运行脚本**
   ```bash
   python dianping_adb.py
   ```

---

## 方案三：Auto.js Pro（付费）

如果愿意付费，Auto.js Pro 仍然可用。

- 官网：https://pro.autojs.org/
- 价格：约 45 元永久

---

## 方案四：按键精灵手机版

老牌自动化工具，功能强大。

- 下载：https://www.anjian.com/
- 需要 ROOT 或开启无障碍服务

---

## ⚙️ 配置说明

```javascript
const CONFIG = {
    clickDelay: 1500,      // 点击间隔(毫秒)
    scrollDelay: 1000,     // 滑动等待时间
    maxScrollCount: 50,    // 最大滑动次数
};
```

**建议**：如果担心风控，把 `clickDelay` 改成 2000-3000

---

## ⏹️ 停止脚本

- **Hamibot**：按音量+键 或 点击停止按钮
- **Python**：按 Ctrl+C

---

## ⚠️ 注意事项

1. 仅支持 **Android** 手机
2. 操作间隔不要太快，避免被风控
3. 如果大众点评更新界面，需要修改关键词
4. 请遵守平台规则

---

## 🔧 常见问题

**Q: 找不到按钮？**
- 大众点评可能更新了界面，修改脚本中的 `applyKeywords`

**Q: 无障碍服务被关闭？**
- 部分手机会自动关闭，需要在设置中重新开启

**Q: Python 连接不上手机？**
- 检查 USB 调试是否开启
- 运行 `adb devices` 看是否识别到设备

---

**免责声明**：仅供学习交流，请遵守平台规则。
