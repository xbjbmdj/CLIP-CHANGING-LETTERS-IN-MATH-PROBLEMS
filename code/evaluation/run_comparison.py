#!/usr/bin/env python3
"""
对比评测脚本：分别测试 original 和 variant，每道题100次
"""
import json
import sys
import os
from pathlib import Path
import subprocess
import time
import pandas as pd
import matplotlib.pyplot as plt

class MathComparisonEvaluator:
    def __init__(self, model_name="Qwen/Qwen2.5-0.5B-Instruct"):
        self.model_name = model_name
        self.results_dir = Path(f"comparison_results_{int(time.time())}")
        self.results_dir.mkdir(exist_ok=True)
        
    def evaluate_dataset(self, dataset_name, dataset_file, num_samples=100):
        """
        评测单个数据集
        """
        print(f"\n{'='*60}")
        print(f"开始评测: {dataset_name}")
        print(f"{'='*60}")
        
        # 创建临时配置文件
        config = {
            "tasks": [
                {
                    "name": dataset_name,
                    "fewshot_num": 0,
                    "metric": ["exact_match", "contains"],
                    "num_samples": num_samples  # 采样次数
                }
            ],
            "custom_tasks": {
                dataset_name: {
                    "path": str(dataset_file.absolute())
                }
            },
            "model_args": {
                "pretrained": self.model_name,
                "dtype": "bfloat16",
                "max_model_len": 4096,
                "gpu_memory_utilization": 0.9
            },
            "generation_args": {
                "max_new_tokens": 4096,
                "temperature": 0.6,
                "top_p": 0.95,
                "do_sample": True,
                "num_return_sequences": num_samples  # 每个问题生成多个答案
            },
            "eval_args": {
                "num_fewshots": 0,
                "job_id": f"{dataset_name}_{int(time.time())}"
            }
        }
        
        config_file = self.results_dir / f"config_{dataset_name}.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(config, f, default_flow_style=False)
        
        # 运行 lighteval
        cmd = [
            "lighteval",
            "--config", str(config_file),
            "--output_dir", str(self.results_dir / dataset_name),
            "--save-details",
            "--verbosity", "INFO"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("评测完成!")
            print(result.stdout[-1000:])  # 打印最后1000字符输出
            
            # 解析结果
            results_file = self.results_dir / dataset_name / "detailed_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    results = json.load(f)
                return results
            else:
                print(f"警告: 结果文件未找到: {results_file}")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"评测失败: {e}")
            print(f"标准错误: {e.stderr}")
            return None
    
    def calculate_accuracy_per_question(self, results, dataset_type):
        """
        计算每道题的准确率（基于100次采样）
        """
        if not results or "task" not in results:
            return {}
        
        question_accuracies = {}
        
        # 假设结果格式中有每个问题的多次生成
        for task_name, task_data in results["task"].items():
            if "samples" in task_data:
                for sample in task_data["samples"]:
                    question_id = sample.get("metadata", {}).get("id", "unknown")
                    
                    # 这里需要根据实际结果格式调整
                    # lighteval 可能不会直接存储多次采样的结果
                    # 可能需要修改 lighteval 或使用其他方法
        
        return question_accuracies
    
    def run_comparison(self, original_file, variant_file, num_samples=100):
        """
        运行对比评测
        """
        print("开始对比评测...")
        
        # 评测 original 数据集
        original_results = self.evaluate_dataset(
            "math_original", 
            Path(original_file),
            num_samples
        )
        
        # 评测 variant 数据集  
        variant_results = self.evaluate_dataset(
            "math_variant",
            Path(variant_file),
            num_samples
        )
        
        # 生成对比报告
        self.generate_comparison_report(original_results, variant_results)
    
    def generate_comparison_report(self, original_results, variant_results):
        """
        生成对比报告
        """
        report_file = self.results_dir / "comparison_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Original vs Variant 对比评测报告\n\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 评测设置\n")
            f.write("- 模型: Qwen/Qwen2.5-0.5B-Instruct\n")
            f.write("- 每道题采样次数: 100次\n")
            f.write("- Temperature: 0.6\n")
            f.write("- Top-p: 0.95\n\n")
            
            f.write("## 数据集统计\n")
            
            # 这里添加具体的统计结果
            # 需要从结果文件中提取
            
            f.write("\n## 准确率对比\n")
            f.write("| 问题类型 | 平均准确率 | 标准差 | 最低准确率 | 最高准确率 |\n")
            f.write("|----------|------------|--------|------------|------------|\n")
            f.write("| Original | 待计算 | 待计算 | 待计算 | 待计算 |\n")
            f.write("| Variant  | 待计算 | 待计算 | 待计算 | 待计算 |\n")
            
            f.write("\n## 详细结果\n")
            f.write("每道题的准确率对比将保存在详细结果文件中。\n")
        
        print(f"✓ 报告已生成: {report_file}")

if __name__ == "__main__":
    # 初始化评测器
    evaluator = MathComparisonEvaluator()
    
    # 运行对比评测
    evaluator.run_comparison(
        original_file="math_original_lighteval.json",
        variant_file="math_variant_lighteval.json",
        num_samples=100  # 每道题测试100遍
    )