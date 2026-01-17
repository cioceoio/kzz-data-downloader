"""
微信机器人通知模块
最小化改动，支持异常状态推送
"""

import requests
import json
import os
from datetime import datetime

class WeChatNotifier:
    def __init__(self, webhook_url=None):
        """
        初始化微信机器人
        webhook_url: 企业微信机器人webhook地址，从环境变量WECHAT_WEBHOOK获取
        """
        self.webhook_url = webhook_url or os.getenv('WECHAT_WEBHOOK')
        self.enabled = bool(self.webhook_url)
        
    def send_message(self, content, msg_type="text"):
        """发送消息到微信"""
        if not self.enabled:
            print("🔕 微信通知未配置，跳过发送")
            return False
            
        try:
            if msg_type == "text":
                data = {"msgtype": "text", "text": {"content": content}}
            elif msg_type == "markdown":
                data = {"msgtype": "markdown", "markdown": {"content": content}}
            
            response = requests.post(self.webhook_url, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print("✅ 微信通知发送成功")
                    return True
                else:
                    print(f"❌ 微信通知发送失败: {result.get('errmsg', '未知错误')}")
                    return False
            else:
                print(f"❌ 微信通知请求失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 微信通知异常: {str(e)}")
            return False
    
    def notify_api_failure(self, stock_code, error_msg):
        """通知API失效"""
        content = f"""
🚨 **可转债数据采集异常通知**

**股票代码**: {stock_code}
**异常类型**: API请求失败
**错误信息**: {error_msg}
**发生时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**建议操作**: 
1. 检查集思录API服务状态
2. 确认网络连接正常
3. 查看GitHub Actions执行日志

📊 可转债自动监控系统
        """.strip()
        
        return self.send_message(content, "markdown")
    
    def notify_ip_blocked(self, stock_code):
        """通知IP异常"""
        content = f"""
🚨 **可转债数据采集IP异常**

**股票代码**: {stock_code}
**异常类型**: IP访问被限制
**发生时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**可能原因**:
- 请求频率过高
- IP被临时封禁
- API策略变更

**建议操作**:
1. 等待一段时间后重试
2. 手动触发GitHub Actions
3. 检查请求频率设置

📊 可转债自动监控系统
        """.strip()
        
        return self.send_message(content, "markdown")
    
    def notify_data_empty(self, stock_code):
        """通知数据为空"""
        content = f"""
⚠️ **可转债数据采集异常**

**股票代码**: {stock_code}
**异常类型**: 返回数据为空
**发生时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**可能原因**:
- 非交易时间
- 停牌或休市
- 数据源异常

**建议操作**:
1. 确认当前是否为交易时间
2. 检查股票是否正常交易
3. 查看市场公告

📊 可转债自动监控系统
        """.strip()
        
        return self.send_message(content, "markdown")
    
    def notify_batch_summary(self, total_count, success_count, failed_stocks):
        """发送批量执行总结"""
        if failed_stocks:
            failed_list = "\n".join([f"- {stock}" for stock in failed_stocks])
            content = f"""
📊 **可转债数据采集完成报告**

📈 **执行统计**
- 总股票数: {total_count}
- 成功下载: {success_count}
- 下载失败: {total_count - success_count}

❌ **失败股票列表**
{failed_list}

⏰ **完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 **查看详情**: [GitHub Actions](https://github.com/${{ github.repository }}/actions)

📊 可转债自动监控系统
            """.strip()
        else:
            content = f"""
✅ **可转债数据采集全部成功**

📈 **执行统计**
- 总股票数: {total_count}
- 成功下载: {success_count}
- 下载失败: 0

⏰ **完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 **查看详情**: [GitHub Actions](https://github.com/${{ github.repository }}/actions)

📊 可转债自动监控系统
            """.strip()
        
        return self.send_message(content, "markdown")

# 全局通知器实例
notifier = WeChatNotifier()