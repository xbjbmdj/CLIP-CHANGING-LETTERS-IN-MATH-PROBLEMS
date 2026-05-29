#!/bin/bash

echo "=== Original vs Variant 对比评测 ==="
echo "每道题测试100遍"
echo "====================================="

# 步骤1: 准备数据
echo -e "\n[1/4] 准备数据集..."
python prepare_datasets.py

# 步骤2: 安装依赖
echo -e "\n[2/4] 检查依赖...（大约需要10秒）"
pip install vllm pandas tqdm matplotlib seaborn

# 步骤3: 运行批量采样评测
echo -e "\n[3/4] 运行批量采样评测 (每道题200次)..."
python batch_sampling_eval.py

# 步骤4: 生成可视化报告
echo -e "\n[4/4] 生成对比报告..."
python generate_report.py

echo -e "\n✅ 评测完成!"
echo "结果保存在: comparison_results_*/ 目录下"