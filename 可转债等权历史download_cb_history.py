#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可转债历史数据下载工具
功能：从集思录获取可转债指数历史数据并保存为 CSV 文件
作者：Administrator
创建日期：2025-01-06
"""

import requests
import csv
import os
from datetime import datetime


# CSV 表头定义
CSV_HEADERS = [
    '日期', '指数', '涨跌', '涨幅(%)', '温度',
    '平均价格(元)', '价格中位数(元)', '转股价值中位数',
    '双低平均', '平均溢价率', '溢价率中位数', '平均收益率',
    '成交额(亿元)', '剩余规模(亿元)', '换手率(%)',
    '数量', '<90', '90~100', '100~110', '110~120', '120~130', '>=130',
    # 以下是未分配的字段
    '指数涨幅(%)', '涨幅_90', '涨幅_90~100', '涨幅_100~110', '涨幅_110~120', '涨幅_120~130', '涨幅_>=130'
]


def fetch_cb_index_history():
    """
    从集思录 API 获取可转债指数历史数据
    
    Returns:
        dict: JSON 响应数据，失败返回 None
    """
    url = "https://www.jisilu.cn/webapi/cb/index_history/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.jisilu.cn/",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


def parse_data(json_data):
    """
    解析 JSON 数据，提取所有可用字段
    
    Args:
        json_data (dict): JSON 响应数据
    
    Returns:
        list: 包含所有字段数据的字典列表，解析失败返回空列表
    """
    if not json_data:
        return []
    
    # 检查响应状态
    if json_data.get("code") != 200:
        print(f"API 返回错误: {json_data.get('msg')}")
        return []
    
    # 提取数据
    data = json_data.get("data", {})
    
    # 解析各字段（使用集思录 API 实际返回的字段名）
    price_dt = data.get("price_dt", [])
    idx_price = data.get("price", [])
    increase_val = data.get("increase_val", [])
    increase_rt = data.get("increase_rt", [])
    temperature = data.get("temperature", [])
    avg_price = data.get("avg_price", [])
    mid_price = data.get("mid_price", [])
    mid_convert_value = data.get("mid_convert_value", [])
    avg_dblow = data.get("avg_dblow", [])
    avg_premium_rt = data.get("avg_premium_rt", [])
    mid_premium_rt = data.get("mid_premium_rt", [])
    avg_ytm_rt = data.get("avg_ytm_rt", [])
    volume = data.get("volume", [])
    count = data.get("count", [])
    amount = data.get("amount", [])
    turnover_rt = data.get("turnover_rt", [])
    price_90 = data.get("price_90", [])
    price_90_100 = data.get("price_90_100", [])
    price_100_110 = data.get("price_100_110", [])
    price_110_120 = data.get("price_110_120", [])
    price_120_130 = data.get("price_120_130", [])
    price_130 = data.get("price_130", [])
    # 未分配的字段
    increase_rt_90 = data.get("increase_rt_90", [])
    increase_rt_90_100 = data.get("increase_rt_90_100", [])
    increase_rt_100_110 = data.get("increase_rt_100_110", [])
    increase_rt_110_120 = data.get("increase_rt_110_120", [])
    increase_rt_120_130 = data.get("increase_rt_120_130", [])
    increase_rt_130 = data.get("increase_rt_130", [])
    idx_increase_rt = data.get("idx_increase_rt", [])
    
    # 获取最大长度
    max_len = len(price_dt)
    
    # 构建结果列表
    result = []
    for i in range(max_len):
        row = {
            '日期': price_dt[i] if i < len(price_dt) else '',
            '指数': idx_price[i] if i < len(idx_price) else '',
            '涨跌': increase_val[i] if i < len(increase_val) else '',
            '涨幅(%)': f"{increase_rt[i]}%" if i < len(increase_rt) else '',
            '温度': temperature[i] if i < len(temperature) else '',
            '平均价格(元)': avg_price[i] if i < len(avg_price) else '',
            '价格中位数(元)': mid_price[i] if i < len(mid_price) else '',
            '转股价值中位数': mid_convert_value[i] if i < len(mid_convert_value) else '',
            '双低平均': avg_dblow[i] if i < len(avg_dblow) else '',
            '平均溢价率': f"{avg_premium_rt[i]}%" if i < len(avg_premium_rt) else '',
            '溢价率中位数': f"{mid_premium_rt[i]}%" if i < len(mid_premium_rt) else '',
            '平均收益率': f"{avg_ytm_rt[i]}%" if i < len(avg_ytm_rt) else '',
            '成交额(亿元)': volume[i] if i < len(volume) else '',
            '剩余规模(亿元)': amount[i] if i < len(amount) else '',
            '换手率(%)': f"{turnover_rt[i]}%" if i < len(turnover_rt) else '',
            '数量': count[i] if i < len(count) else '',
            '<90': price_90[i] if i < len(price_90) else '',
            '90~100': price_90_100[i] if i < len(price_90_100) else '',
            '100~110': price_100_110[i] if i < len(price_100_110) else '',
            '110~120': price_110_120[i] if i < len(price_110_120) else '',
            '120~130': price_120_130[i] if i < len(price_120_130) else '',
            '>=130': price_130[i] if i < len(price_130) else '',
            # 未分配的字段
            '指数涨幅(%)': f"{idx_increase_rt[i]}%" if i < len(idx_increase_rt) else '',
            '涨幅_90': f"{increase_rt_90[i]}%" if i < len(increase_rt_90) else '',
            '涨幅_90~100': f"{increase_rt_90_100[i]}%" if i < len(increase_rt_90_100) else '',
            '涨幅_100~110': f"{increase_rt_100_110[i]}%" if i < len(increase_rt_100_110) else '',
            '涨幅_110~120': f"{increase_rt_110_120[i]}%" if i < len(increase_rt_110_120) else '',
            '涨幅_120~130': f"{increase_rt_120_130[i]}%" if i < len(increase_rt_120_130) else '',
            '涨幅_>=130': f"{increase_rt_130[i]}%" if i < len(increase_rt_130) else '',
        }
        result.append(row)
    
    return result


def save_to_csv(data_list, output_path):
    """
    将数据列表保存为 CSV 文件
    
    Args:
        data_list (list): 包含字典的数据列表
        output_path (str): 输出文件路径
    
    Returns:
        bool: 保存成功返回 True，失败返回 False
    """
    if not data_list:
        print("没有数据可保存")
        return False
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(data_list)
        return True
    except IOError as e:
        print(f"保存文件失败: {e}")
        return False


def main():
    """
    主函数：执行完整的数据下载和保存流程
    """
    print("=" * 60)
    print("可转债指数历史数据下载工具")
    print("=" * 60)
    
    # 获取当前程序所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置输出文件名（包含时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H")
    default_filename = f"可转债等权cb_index_history_{timestamp}.csv"
    
    # 使用默认文件名
    filename = default_filename
    
    # 确保文件名为 CSV 格式
    if not filename.lower().endswith('.csv'):
        filename += '.csv'
    
    # 组合完整路径（保存到程序所在目录）
    output_path = os.path.join(script_dir, filename)
    
    print("\n正在从集思录获取数据...")
    
    # 获取数据
    json_data = fetch_cb_index_history()
    if not json_data:
        print("数据获取失败，请检查网络连接或 API 地址")
        return
    
    # 解析数据
    data_list = parse_data(json_data)
    if not data_list:
        print("数据解析失败或无有效数据")
        return
    
    print(f"成功获取 {len(data_list)} 条记录")
    print(f"可用字段: {len(CSV_HEADERS)} 个")
    
    # 保存为 CSV
    print(f"\n正在保存到文件: {output_path}")
    
    if save_to_csv(data_list, output_path):
        print("✓ 保存成功！")
        print(f"文件路径: {os.path.abspath(output_path)}")
        print(f"数据范围: {data_list[0]['日期']} 至 {data_list[-1]['日期']}")
    else:
        print("✗ 保存失败")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
