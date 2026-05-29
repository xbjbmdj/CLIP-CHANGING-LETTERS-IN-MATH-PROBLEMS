# batch_sampling_eval_fixed.py
import json
import torch
from vllm import SamplingParams, LLM
from tqdm import tqdm
import time
import pandas as pd
import os
import sys
config_max_tokens=16384

class MultiSampleEvaluator:
    def __init__(self, model_name="Qwen/Qwen3-4B-Thinking-2507", local_model_path=None):
        """初始化评测器
        
        Args:
            model_name: 模型名称
            local_model_path: 本地模型路径（如果提供则使用本地路径）
        """
        print(f"加载模型: {model_name}")
        
        # 决定使用哪个路径
        if local_model_path and os.path.exists(local_model_path):
            print(f"✓ 使用本地模型路径: {local_model_path}")
            model_to_load = local_model_path
        else:
            print(f"✓ 使用在线模型名称: {model_name}")
            model_to_load = model_name
        
        # 尝试多种方式加载模型
        self.llm = self._load_model_with_retry(model_to_load)
    
    def _load_model_with_retry(self, model_path, max_retries=3):
        """带重试的模型加载"""
        for attempt in range(max_retries):
            try:
                print(f"尝试加载模型 (尝试 {attempt+1}/{max_retries})...")
                
                # 尝试不同的参数组合
                if attempt == 0:
                    # 第一次尝试：标准方式
                    llm = LLM(
                        model=model_path,
                        dtype="bfloat16",
                        max_model_len=config_max_tokens,
                        gpu_memory_utilization=0.9,
                        trust_remote_code=True
                    )
                elif attempt == 1:
                    # 第二次尝试：禁用下载
                    llm = LLM(
                        model=model_path,
                        dtype="bfloat16",
                        max_model_len=config_max_tokens,
                        gpu_memory_utilization=0.9,
                        trust_remote_code=True,
                        download_dir=None
                    )
                else:
                    # 第三次尝试：使用auto dtype
                    llm = LLM(
                        model=model_path,
                        dtype="auto",
                        max_model_len=config_max_tokens,
                        gpu_memory_utilization=0.9,
                        trust_remote_code=True
                    )
                
                print("✅ 模型加载成功！")
                return llm
                
            except Exception as e:
                print(f"❌ 尝试 {attempt+1} 失败: {str(e)[:200]}")
                if attempt == max_retries - 1:
                    print("所有尝试都失败，请检查：")
                    print("1. 模型路径是否正确")
                    print("2. 模型文件是否完整")
                    print("3. 是否有足够GPU内存")
                    raise
                time.sleep(2)  # 等待后重试
    
    def load_dataset(self, json_file):
        """加载数据集"""
        print(f"加载数据集: {json_file}")
        with open(json_file, 'r') as f:
            data = json.load(f)
        print(f"加载了 {len(data['instances'])} 个问题")
        return data['instances']
    
    def create_prompt(self, question):
        """创建提示模板"""
        return f"""You are a mathematician. Solve the following math problem. Please think step by step. 
问题：{question}
"""
    
    def evaluate_with_multiple_samples(self, instances, num_samples=100, temperature=0.6):
        """
        对每个问题生成多个样本并评估
        """
        results = []
        
        # 准备所有提示
        prompts = []
        metadata = []
        
        print(f"\n准备 {len(instances)} 个问题的提示...")
        for instance in instances:
            prompt = self.create_prompt(instance['input'])
            prompts.append(prompt)
            metadata.append({
                'id': instance.get('id', len(prompts)-1),
                'question': instance['input'],
                'target': instance['target']
            })
        
        # 采样参数 - 对每个提示生成多个样本
        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=0.95,
            max_tokens=config_max_tokens,
            n=num_samples  # 关键：每个提示生成多个样本
        )
        
        print(f"开始生成 {len(prompts)} 个问题的 {num_samples} 个样本...")
        print(f"总共需要生成 {len(prompts) * num_samples} 个回答")
        
        # 批量生成
        outputs = self.llm.generate(prompts, sampling_params)
        
        print("处理生成结果...")
        # 处理结果
        for idx, (output, meta) in enumerate(zip(outputs, metadata)):
            question_id = meta['id']
            target_answer = meta['target']
            
            # 收集所有生成的答案
            generated_answers = []
            correct_count = 0
            
            for i in range(num_samples):
                if i < len(output.outputs):
                    generated = output.outputs[i].text.strip()
                    generated_answers.append(generated)
                    
                    # 检查是否正确
                    if self.is_correct(generated, target_answer):
                        correct_count += 1
            
            accuracy = correct_count / num_samples if num_samples > 0 else 0
            
            results.append({
                "question_id": question_id,
                "question": meta['question'][:100] + "..." if len(meta['question']) > 100 else meta['question'],
                "target_answer": target_answer,
                "accuracy": accuracy,
                "correct_samples": correct_count,
                "total_samples": num_samples,
                "all_generated": generated_answers[:5]  # 只保存前5个示例
            })
            
            if (idx + 1) % 10 == 0 or idx == 0 or idx == len(outputs)-1:
                print(f"  进度: {idx+1}/{len(outputs)} - 准确率: {accuracy:.3f}")
        
        return results
    
    def is_correct(self, generated, target):
        """判断答案是否正确"""
        # 简化匹配：去除空格和特殊符号
        import re
        
        # # 清理生成的答案
        # clean_generated = re.sub(r'\s+', '', generated)
        # clean_generated = re.sub(r'[\\$()]', '', clean_generated)
        
        # # 清理目标答案
        # clean_target = re.sub(r'\s+', '', target)
        # clean_target = re.sub(r'[\\$()]', '', clean_target)
        
        # # 尝试多种匹配方式
        # if clean_generated == clean_target:
        #     return True
        
        # # 检查是否包含关键数字
        # numbers_gen = re.findall(r'\d+\.?\d*', clean_generated)
        # numbers_target = re.findall(r'\d+\.?\d*', clean_target)
        
        # if numbers_target and all(num in clean_generated for num in numbers_target):
        #     return True
        
        # return False
        """
    判断生成答案与目标答案是否正确。
    提取两个字符串中最后一个连续的数字字符串进行比较。
    
    参数:
        generated: 模型生成的答案字符串
        target: 目标答案字符串
    
    返回:
        bool: 如果提取到的最后一个数字字符串相同则返回True，否则返回False
    """
        def extract_last_number(text):
            """
            提取字符串中最后一个连续的数字字符串
            例如："fjhjh8012jkbdkj123jajl-5" -> "5"
            """
            # 找到所有连续的数字序列
            numbers = re.findall(r'\d+', text)
            # 返回最后一个，如果没有则返回空字符串
            return numbers[-1] if numbers else ""
        
        # 提取最后一个数字字符串
        gen_last_num = extract_last_number(generated)
        target_last_num = extract_last_number(target)
        
        # 比较提取到的数字字符串
        return gen_last_num == target_last_num
    
    def save_results(self, results, dataset_type, output_dir="shinsh_results_qwen4b"):
        """保存结果"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = int(time.time())
        filename = f"{output_dir}/{dataset_type}_multisample_{timestamp}.json"
        
        # 保存详细结果
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 创建统计摘要
        df = pd.DataFrame(results)
        summary = {
            "dataset_type": dataset_type,
            "total_questions": len(results),
            "num_samples_per_question": results[0]['total_samples'] if results else 0,
            "average_accuracy": float(df['accuracy'].mean()),
            "std_accuracy": float(df['accuracy'].std()),
            "min_accuracy": float(df['accuracy'].min()),
            "max_accuracy": float(df['accuracy'].max()),
            "timestamp": timestamp,
            "results_file": filename
        }
        
        summary_file = f"{output_dir}/{dataset_type}_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✓ 结果已保存: {filename}")
        print(f"✓ 摘要已保存: {summary_file}")
        print(f"  平均准确率: {summary['average_accuracy']:.4f}")
        print(f"  标准差: {summary['std_accuracy']:.4f}")
        
        return summary
    
    def run_comparison(self, original_file, variant_file, num_samples=100):
        """运行完整的对比评测"""
        print("=" * 60)
        print("Original vs Variant 对比评测")
        print("=" * 60)
        
        # 检查文件是否存在
        for file in [original_file, variant_file]:
            if not os.path.exists(file):
                print(f"❌ 文件不存在: {file}")
                return
        
        print(f"\n加载 Original 数据集...")
        original_data = self.load_dataset(original_file)
        
        print(f"加载 Variant 数据集...")
        variant_data = self.load_dataset(variant_file)
        
        print(f"\n{'='*60}")
        print(f"开始评测 Original 数据集 ({len(original_data)} 个问题)")
        print(f"每个问题采样 {num_samples} 次")
        print(f"{'='*60}")
        
        original_results = self.evaluate_with_multiple_samples(
            original_data, num_samples=num_samples
        )
        original_summary = self.save_results(original_results, "original")
        
        print(f"\n{'='*60}")
        print(f"开始评测 Variant 数据集 ({len(variant_data)} 个问题)")
        print(f"每个问题采样 {num_samples} 次")
        print(f"{'='*60}")
        
        variant_results = self.evaluate_with_multiple_samples(
            variant_data, num_samples=num_samples
        )
        variant_summary = self.save_results(variant_results, "variant")
        
        # 生成对比报告
        self.generate_comparison_report(original_summary, variant_summary)
    
    def generate_comparison_report(self, original_summary, variant_summary):
        """生成对比报告"""
        report_dir = "comparison_reports"
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = int(time.time())
        report_file = f"{report_dir}/comparison_report_{timestamp}.md"
        
        # 计算差异
        orig_acc = original_summary['average_accuracy']
        var_acc = variant_summary['average_accuracy']
        diff = var_acc - orig_acc
        diff_percent = (diff / orig_acc * 100) if orig_acc > 0 else 0
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Original vs Variant 对比评测报告\n\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 评测设置\n")
            f.write(f"- 模型: Ministral-3-3B-Instruct-2512\n")
            f.write(f"- 每道题采样次数: 100次\n")
            f.write(f"- Temperature: 0.6\n")
            f.write(f"- Top-p: 0.95\n\n")
            
            f.write("## 结果对比\n\n")
            f.write("| 数据集 | 问题数量 | 平均准确率 | 标准差 | 最低准确率 | 最高准确率 |\n")
            f.write("|--------|----------|------------|--------|------------|------------|\n")
            f.write(f"| Original | {original_summary['total_questions']} | {orig_acc:.4f} | {original_summary['std_accuracy']:.4f} | {original_summary['min_accuracy']:.4f} | {original_summary['max_accuracy']:.4f} |\n")
            f.write(f"| Variant | {variant_summary['total_questions']} | {var_acc:.4f} | {variant_summary['std_accuracy']:.4f} | {variant_summary['min_accuracy']:.4f} | {variant_summary['max_accuracy']:.4f} |\n\n")
            
            f.write("## 关键发现\n")
            f.write(f"- **准确率差异**: Variant 比 Original ")
            if diff > 0:
                f.write(f"高 {abs(diff):.4f} ({abs(diff_percent):.2f}%)\n")
                f.write(f"- **结论**: 变量替换对模型性能有 **积极影响**\n")
            elif diff < 0:
                f.write(f"低 {abs(diff):.4f} ({abs(diff_percent):.2f}%)\n")
                f.write(f"- **结论**: 变量替换对模型性能有 **负面影响**\n")
            else:
                f.write("无差异\n")
                f.write(f"- **结论**: 变量替换对模型性能 **无显著影响**\n")
            
            f.write(f"\n## 详细结果文件\n")
            f.write(f"- Original 结果: `{original_summary['results_file']}`\n")
            f.write(f"- Variant 结果: `{variant_summary['results_file']}`\n")
        
        print(f"\n{'='*60}")
        print("✅ 对比评测完成！")
        print(f"{'='*60}")
        print(f"报告文件: {report_file}")
        print(f"Original 平均准确率: {orig_acc:.4f}")
        print(f"Variant 平均准确率: {var_acc:.4f}")
        print(f"差异: {diff:.4f} ({'+' if diff > 0 else ''}{diff_percent:.2f}%)")
        print(f"{'='*60}")

def main():
    """主函数"""
    print("欢迎使用 Original vs Variant 对比评测工具")
    print(f"当前目录: {os.getcwd()}")
    
    # 模型路径配置
    LOCAL_MODEL_PATH = "/root/shared-nvme/models/xxx"
    
    # 检查模型是否存在
    if os.path.exists(LOCAL_MODEL_PATH):
        print(f"✓ 找到本地模型: {LOCAL_MODEL_PATH}")
        model_path = LOCAL_MODEL_PATH
    else:
        print(f"⚠️  本地模型不存在: {LOCAL_MODEL_PATH}")
        print("将尝试使用在线模型（需要网络连接）")
        model_path = None
    
    # 检查数据文件
    data_files = ["ori_hard.json", "var_hard.json"]
    for file in data_files:
        if os.path.exists(file):
            print(f"✓ 找到数据文件: {file}")
        else:
            print(f"❌ 数据文件不存在: {file}")
            print("请先运行 prepare_datasets.py 生成数据文件")
            return
    
    # 初始化评测器
    if model_path:
        evaluator = MultiSampleEvaluator(
            model_name="Qwen/Qwen3-4B-Thinking-2507",
            local_model_path=model_path
        )
    else:
        evaluator = MultiSampleEvaluator(
            model_name="Qwen/Qwen3-4B-Thinking-2507"
        )
    
    # 运行对比评测
    evaluator.run_comparison(
        original_file="ori_hard.json",
        variant_file="var_hard.json",
        num_samples=40
    )

if __name__ == "__main__":
    main()