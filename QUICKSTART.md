# 🚀 AI生产力教练 - 快速启动指南

## 5分钟快速体验

### 步骤1: 启动后端服务器

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 启动服务器
cd api
python server.py
```

看到以下输出表示成功：
```
🚀 启动AI生产力教练服务器...
📊 API文档: http://localhost:8000/docs
🤖 双Agent系统已就绪
```

### 步骤2: 启动Web控制台

```bash
# 新开一个终端
cd web-console
npm install
npm run dev
```

访问: http://localhost:3000

### 步骤3: 运行Android应用

1. 用Android Studio打开 `android-app/` 目录
2. 修改服务器地址（模拟器用 `10.0.2.2:8000`，真机用电脑IP）
3. 点击Run按钮

### 步骤4: 授予权限

首次运行需要：
1. 允许通知权限
2. 设置 -> 应用 -> 特殊权限 -> 使用统计权限

### 步骤5: 开始使用

1. 点击"启动智能监控"
2. 在Web控制台创建第一个目标
3. 打开任何娱乐应用体验AI提醒

---

## 🎯 核心特性

### 双Agent AI系统
- **策划Agent**: 分析习惯，制定长期策略
- **导演Agent**: 实时监控，智能干预

### 主要功能
- 📱 Android监控娱乐应用
- 🎯 目标设定和追踪
- 🏆 成就解锁系统
- 📊 数据可视化分析
- 💡 智能提醒和鼓励

---

## 📚 更多文档

- [完整README](README.md) - 项目概述
- [架构设计](docs/架构设计.md) - 技术架构
- [部署指南](docs/部署指南.md) - 详细部署步骤
- [使用手册](docs/使用手册.md) - 功能详解
- [方案对比](docs/方案对比分析.md) - 为什么选择这个方案

---

## 🔧 故障排除

### 后端无法启动
```bash
# 检查Python版本（需要3.8+）
python --version

# 重新安装依赖
pip install -r requirements.txt --upgrade
```

### Web控制台无法访问
```bash
# 检查端口占用
lsof -i:3000

# 清除缓存重新安装
rm -rf node_modules package-lock.json
npm install
```

### Android应用无法连接
1. 确保后端服务器运行中
2. 模拟器使用 `10.0.2.2`，真机使用电脑IP地址
3. 检查防火墙是否阻止8000端口

---

## 💬 获取帮助

- 📧 Email: support@example.com
- 💡 Issues: https://github.com/your-repo/issues

---

**开始您的生产力提升之旅！** 🎉
