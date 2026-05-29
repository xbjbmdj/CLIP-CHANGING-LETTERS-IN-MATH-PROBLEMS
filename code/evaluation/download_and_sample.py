# download_and_sample.py
from datasets import load_dataset
import pandas as pd

# 1. 下载完整数据集（选择其中一个难度级别，例如 'simplelr_abel_easy'）
print("正在下载数据集...")
dataset = load_dataset('hkust-nlp/SimpleRL-Zoo-Data', 'simplelr_abel_easy', split='train')

# 2. 随机采样 2000 条数据
print(f"原始数据量: {len(dataset)}")
sampled_dataset = dataset.shuffle(seed=42).select(range(2000))

# 3. 保存为 Parquet 格式（训练常用）
output_path = 'SimpleRL_Zoo_2k.parquet'
sampled_dataset.to_parquet(output_path)
print(f"✅ 已保存 2000 条数据至: {output_path}")

# 4. （可选）查看样例
print("\n数据样例:")
print(sampled_dataset[0])