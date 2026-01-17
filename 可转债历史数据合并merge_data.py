#!/usr/bin/env python3
"""
可转债历史数据合并工具
将每月下载的可转债历史数据合并为按年保存的汇总文件，并移除重复行
"""

import os
import csv
import glob
from datetime import datetime

def merge_csv_files(input_dir="data/csv", output_dir="data/csv"):
    """
    合并CSV文件
    :param input_dir: 输入目录，默认data/csv
    :param output_dir: 输出目录，默认data/csv
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 按可转债分组的数据
    bonds_data = {}
    
    # 1. 遍历所有CSV文件
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    for file_path in csv_files:
        # 获取文件名
        filename = os.path.basename(file_path)
        
        # 解析文件名：代码名称__日期.csv
        if "__" in filename:
            try:
                # 提取可转债信息和日期
                bond_info, date_str = filename.split("__")
                date_str = date_str.replace(".csv", "")
                
                # 提取年份
                year = date_str[:4]
                
                # 获取可转债唯一标识（代码+名称）
                bond_key = bond_info
                
                # 如果是新的可转债，初始化数据结构
                if bond_key not in bonds_data:
                    bonds_data[bond_key] = {}
                
                # 如果是新的年份，初始化列表
                if year not in bonds_data[bond_key]:
                    bonds_data[bond_key][year] = []
                
                # 2. 读取CSV文件内容
                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    
                    # 获取表头（第一行）
                    headers = next(reader)
                    
                    # 保存表头
                    bonds_data[bond_key]["headers"] = headers
                    
                    # 3. 读取数据行
                    for row in reader:
                        if row:
                            # 转换序号为整数（用于排序）
                            try:
                                if row[0]:
                                    row[0] = int(row[0])
                                else:
                                    row[0] = 0
                            except ValueError:
                                row[0] = 0
                            
                            # 添加数据行
                            bonds_data[bond_key][year].append(row)
                
                print(f"✓ 处理文件: {filename}")
                
            except Exception as e:
                print(f"⚠ 处理文件失败 {filename}: {e}")
                continue
    
    # 4. 合并数据并保存
    merged_count = 0
    
    for bond_key, bond_data in bonds_data.items():
        if "headers" in bond_data:
            headers = bond_data["headers"]
            
            # 处理每个年份
            for year, rows in bond_data.items():
                if year != "headers" and rows:
                    # 去重：将数据行转换为元组，使用集合去重，再转换回列表
                    # 注意：需要将第一列序号转换为字符串，以便正确去重
                    unique_rows = []
                    seen = set()
                    
                    for row in rows:
                        # 转换序号为字符串
                        row_str = tuple(str(x) if isinstance(x, int) else x for x in row)
                        if row_str not in seen:
                            seen.add(row_str)
                            unique_rows.append(row)
                    
                    # 排序：按日期排序（第二列是日期）
                    unique_rows.sort(key=lambda x: (x[1] if len(x) > 1 else "", x[0]))
                    
                    # 重新生成序号
                    for idx, row in enumerate(unique_rows, 1):
                        row[0] = idx
                    
                    # 5. 保存合并后的数据
                    merged_filename = f"{bond_key}__{year}.csv"
                    merged_path = os.path.join(output_dir, merged_filename)
                    
                    # 检查文件是否已存在
                    if os.path.exists(merged_path):
                        print(f"ℹ️ 文件已存在，跳过合并: {merged_filename}")
                        continue
                    
                    # 保存合并后的数据
                    with open(merged_path, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                        writer.writerows(unique_rows)
                    
                    print(f"📁 合并完成: {merged_filename} (共 {len(unique_rows)} 条记录)")
                    merged_count += 1
    
    print(f"\n🎉 数据合并完成！")
    print(f"📊 处理了 {len(bonds_data)} 个可转债")
    print(f"📈 生成了 {merged_count} 个合并文件")
    print(f"📋 输出目录: {output_dir}")

if __name__ == "__main__":
    print("🚀 可转债历史数据合并工具")
    print(f"📅 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    merge_csv_files()
