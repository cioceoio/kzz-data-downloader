"""
GitHub Actions版本 - 可转债历史数据下载器
适配GitHub Actions环境，支持自动触发和数据保存
"""

import requests
import csv
import json
import os
import time
import random
from datetime import datetime, timedelta
from wechat_notifier import notifier

def get_random_headers():
    """获取随机请求头，防止被封IP"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ]
    
    return {
        "User-Agent": random.choice(user_agents),
        "Referer": "https://www.jisilu.cn/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }

def get_stock_data(stock_code="113646", stock_name="永吉转债"):
    """获取可转债历史数据"""
    url = f"https://www.jisilu.cn/data/cbnew/detail_hist/{stock_code}"
    params = {}

    for retry in range(3):
        try:
            headers = get_random_headers()
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    rows = data.get("rows", [])
                    if rows:
                        # 获取当前日期作为文件名后缀
                        beijing_time = datetime.utcnow() + timedelta(hours=8)
                        file_date = beijing_time.strftime("%Y%m%d")
                        
                        # 确保数据目录存在
                        data_dir = "data/csv"
                        os.makedirs(data_dir, exist_ok=True)
                        
                        filename = f"{data_dir}/{stock_code}{stock_name}__{file_date}.csv"
                        
                        # 写入CSV文件
                        csv_content = []
                        for i, row in enumerate(rows, 1):
                            try:
                                cell = row.get("cell", {})
                                date = cell.get("last_chg_dt", "")
                                price = cell.get("price", "")
                                volume = cell.get("volume", "")  # 成交额(万元)
                                convert_value = cell.get("convert_value", "")
                                ytm_rt = cell.get("ytm_rt", "")  # 到期税前收益率
                                premium_rt = cell.get("premium_rt", "")  # 转股溢价率
                                curr_iss_amt = cell.get("curr_iss_amt", "")  # 剩余规模(亿元)
                                turnover_rt = cell.get("turnover_rt", "")  # 换手率
                                if turnover_rt and not turnover_rt.endswith("%"):
                                    turnover_rt += "%"
                                sprice = cell.get("sprice", "")  # 正股价
                                
                                if date and price:
                                    # 按照参考表头顺序添加数据
                                    csv_content.append([
                                        str(i),  # 序号
                                        date,
                                        price,
                                        volume,
                                        convert_value,
                                        ytm_rt,
                                        premium_rt,
                                        curr_iss_amt,
                                        turnover_rt,
                                        sprice
                                    ])
                            except Exception as ve:
                                print(f"⚠ 跳过异常数据: {row} - {ve}")
                                continue
                        
                        if csv_content:
                            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                                writer = csv.writer(csvfile)
                                writer.writerow(["序号", "日期", "收盘价", "成交额(万元)", "转股价值", "到期税前收益率", "转股溢价率", "剩余规模(亿元)", "换手率", "正股价"])
                                writer.writerows(csv_content)
                            
                            print(f"✓ {filename} - {len(csv_content)}条记录")
                            return {
                                "success": True,
                                "filename": filename,
                                "records": len(csv_content),
                                "stock": f"{stock_code} {stock_name}"
                            }
                        else:
                            print(f"⚠ {filename} - 无有效数据")
                            return {"success": False, "error": "无有效数据"}
                    else:
                        print(f"⚠ {stock_code} {stock_name} - API返回空数据")
                        # 发送微信通知 - 数据为空
                        # notifier.notify_data_empty(stock_code)
                        return {"success": False, "error": "API返回空数据"}
                except json.JSONDecodeError as e:
                    print(f"⚠ 数据解析异常: {e}")
                    continue
            else:
                print(f"❌ 请求失败，状态码：{response.status_code}")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"网络异常: {e}"
            print(f"❌ {error_msg} (第{retry+1}次)")
            # 发送微信通知 - API异常
            if retry == 2:  # 只在最后一次重试失败时发送通知
                notifier.notify_api_failure(stock_code, error_msg)
        except Exception as e:
            error_msg = f"未知异常: {e}"
            print(f"❌ {error_msg} (第{retry+1}次)")
            # 检查是否是IP被封的迹象，只在最后一次重试时发送通知
            if retry == 2:
                if "timeout" in str(e).lower() or "connection" in str(e).lower():
                    notifier.notify_ip_blocked(stock_code)
                else:
                    notifier.notify_api_failure(stock_code, error_msg)
        
        if retry < 2:
            wait_time = (retry + 1) * 2
            print(f"⏳ 等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    return {"success": False, "error": "所有重试均失败"}

def main():
    """主执行函数"""
    print(f"🚀 可转债历史数据下载开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 从配置文件读取可转债列表（优先使用CSV格式）
    stock_list = []
    
    # 尝试从TXT配置文件读取
    try:
        with open('config.txt', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过表头
            for row in reader:
                if len(row) >= 2:
                    code = row[0].strip()
                    name = row[1].strip()
                    if code and name:
                        stock_list.append((code, name))
        if stock_list:
            print(f"从TXT配置文件成功读取 {len(stock_list)} 条可转债数据")
    except Exception as e:
        print(f"读取TXT配置文件失败: {e}")
    
    # 如果CSV读取失败或为空，尝试从JSON配置文件读取
    if not stock_list:
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            bonds_data = config.get('convertible_bonds', [])
            stock_list = [(bond['code'], bond['name']) for bond in bonds_data]
            print(f"从JSON配置文件成功读取 {len(stock_list)} 条可转债数据")
        except Exception as e:
            print(f"读取JSON配置文件失败: {e}")
    
    # 如果所有配置文件读取失败，使用默认列表作为备份
    if not stock_list:
        stock_list = [
            ("113646", "永吉转债"),
            ("128125", "华阳转债"),
            ("111016", "神通转债"),
        ]
        print(f"使用默认配置: {len(stock_list)} 条可转债数据")
    
    results = []
    success_count = 0
    total_count = len(stock_list)
    
    for i, (code, name) in enumerate(stock_list, 1):
        print(f"\n[{i}/{total_count}] 📈 正在下载: {code} {name}")
        
        result = get_stock_data(code, name)
        results.append(result)
        
        if result["success"]:
            success_count += 1
        
        # 延时防止请求过频
        if i < total_count:
            time.sleep(random.uniform(3, 9)) # 随机延时3-9秒，避免对服务器造成过大压力
    
    # 生成执行报告
    print(f"\n📊 执行完成！")
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失败: {total_count - success_count}/{total_count}")
    
    # 收集失败的可转债信息
    failed_stocks = []
    for result in results:
        if not result["success"]:
            failed_stocks.append(result.get("stock", "未知可转债"))
    
    # 发送微信通知 - 执行总结
    #notifier.notify_batch_summary(total_count, success_count, failed_stocks)
    
    # 显示执行结果（不生成报告文件）
    print(f"\n📊 执行完成！")
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失败: {total_count - success_count}/{total_count}")
    
    # 列出生成的CSV文件
    print(f"\n📁 生成的CSV文件:")
    for file in os.listdir("."):
        if file.endswith(".csv"):
            file_size = os.path.getsize(file)
            print(f"  📄 {file} ({file_size:,} bytes)")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    # 只要程序执行完成，就返回成功状态码
    # 即使部分股票下载失败，也不影响整体执行
    exit(0)