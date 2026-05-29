import json
import os
from collections import defaultdict

def split_datasets(jsonl_path):
    """
    将 JSONL 数据分成两个数据集：original 和 variant
    """
    original_data = []
    variant_data = []
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
                
            item = json.loads(line)
            item_id = item.get('id', len(original_data))
            
            # Original 数据集
            original_data.append({
                "id": item_id,
                "input": item["original"],
                "target": item["answer"],
                "metadata": {
                    "type": "original",
                    "replace_list": item.get("replace_list", []),
                    "variant": item.get("variants", "")
                }
            })
            
            # Variant 数据集（使用变量替换后的问题）
            variant_data.append({
                "id": item_id,
                "input": item["variants"],
                "target": item["answer"],
                "metadata": {
                    "type": "variant",
                    "replace_list": item.get("replace_list", []),
                    "original": item.get("original", "")
                }
            })
    
    # 保存两个数据集
    datasets = {
        "math_original": {
            "name": "math_original",
            "description": "原始数学问题（未替换变量）",
            "instances": original_data
        },
        "math_variant": {
            "name": "math_variant", 
            "description": "变量替换后的数学问题",
            "instances": variant_data
        }
    }
    
    # 保存文件
    for name, data in datasets.items():
        filename = f"{name}_lighteval.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ 已保存 {name}: {len(data['instances'])} 条数据到 {filename}")
    
    return datasets

def create_comparison_config():
    """创建对比评测的配置文件"""
    config = {
        "comparison_eval": {
            "description": "Original vs Variant 对比评测",
            "datasets": ["math_original", "math_variant"],
            "num_samples": 100,  # 每道题采样100次
            "metrics": ["exact_match", "partial_match"]
        },
        
        "model_config": {
            "pretrained": "Qwen/Qwen2.5-0.5B-Instruct",
            "dtype": "bfloat16",
            "max_model_len": 4096,
            "gpu_memory_utilization": 0.9
        },
        
        "generation_config": {
            "max_new_tokens": 4096,
            "temperature": 0.6,
            "top_p": 0.95,
            "do_sample": True,
            "num_return_sequences": 100  # 关键：每个问题生成100个答案
        }
    }
    
    with open("comparison_config.yaml", 'w', encoding='utf-8') as f:
        import yaml
        yaml.dump(config, f, default_flow_style=False)
    
    print("✓ 已创建对比配置文件: comparison_config.yaml")

if __name__ == "__main__":
    # 你的数据文件路径
    jsonl_file = "dataset.jsonl"
    
    print("正在处理数据集...")
    datasets = split_datasets(jsonl_file)
    
    print("\n正在创建配置文件...")
    create_comparison_config()
    
    print("\n数据集统计:")
    for name, data in datasets.items():
        print(f"  {name}: {len(data['instances'])} 个问题")
        if data['instances']:
            print(f"    示例: {data['instances'][0]['input'][:80]}...")