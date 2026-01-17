# 可转债历史数据自动采集系统

## 🚀 功能概览

自动化可转债历史数据采集系统，支持GitHub仓库存储和微信异常通知。

### 核心功能
- ⏰ **定时采集**：每月1日自动执行
- 📊 **数据下载**：从集思录API获取历史数据
- 💾 **自动存储**：CSV文件保存到GitHub仓库
- 🔔 **异常通知**：微信推送API失败、IP异常等告警
- 📈 **执行报告**：每次运行后的详细统计

## 📋 快速部署

### 1. 配置微信通知（可选）
1. 企业微信群添加机器人，获取Webhook地址
2. GitHub仓库设置 → Secrets → 添加 `WECHAT_WEBHOOK`

### 2. 上传文件到GitHub
```bash
# 工作流文件
mkdir -p .github/workflows
cp kzz-schedule-with-wechat.yml .github/workflows/

# 程序文件
cp github_actions_etf.py .
cp wechat_notifier.py .

# 提交到仓库
git add .
git commit -m "部署可转债历史数据采集系统"
git push
```

### 3. 启用工作流
- GitHub仓库 → Actions → 启用工作流
- 支持手动触发测试

## 📁 文件结构
```
repository/
├── .github/workflows/
│   └── kzz-schedule-with-wechat.yml   # 工作流配置
├── data/csv/                          # 数据存储目录
├── github_actions_etf.py              # 主程序
└── wechat_notifier.py                 # 微信通知模块
```

## 📊 监控面板

### GitHub Actions
- 执行状态和日志
- 文件生成统计
- 失败原因分析

### 微信通知
- 🚨 API请求失败
- ⛔ IP访问限制  
- ⚠️ 数据为空
- 📊 执行总结

## 🔧 故障处理

### 常见问题
- **文件未生成**：检查API状态和执行日志
- **通知未收到**：确认Webhook配置正确
- **提交失败**：检查仓库权限设置

### 手动操作
```bash
# 手动触发
GitHub Actions → Run workflow

# 查看历史数据
git log --oneline -- data/csv/
```

## 💡 技术特点

- **零侵入**：不影响原有业务逻辑
- **高可靠**：多重异常处理机制
- **易维护**：模块化设计，便于扩展
- **安全**：敏感信息通过环境变量管理

---

**部署完成后，系统将自动运行，无需人工干预！** 🎉