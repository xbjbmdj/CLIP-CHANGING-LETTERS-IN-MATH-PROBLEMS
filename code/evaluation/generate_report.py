import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import glob

def load_results():
    """加载结果文件"""
    result_files = glob.glob("results/*summary*.json")
    
    summaries = {}
    for file in result_files:
        with open(file, 'r') as f:
            data = json.load(f)
            dataset_type = data['dataset_type']
            summaries[dataset_type] = data
    
    return summaries

def create_comparison_plot(summaries):
    """创建对比图表"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 准备数据
    comparison_data = []
    for dtype, summary in summaries.items():
        comparison_data.append({
            'Dataset': dtype,
            'Accuracy': summary['average_accuracy'],
            'Std': summary['std_accuracy'],
            'Min': summary['min_accuracy'],
            'Max': summary['max_accuracy']
        })
    
    df = pd.DataFrame(comparison_data)
    
    # 1. 准确率对比柱状图
    ax = axes[0, 0]
    bars = ax.bar(df['Dataset'], df['Accuracy'], 
                  yerr=df['Std'], capsize=5, alpha=0.7)
    ax.set_ylabel('准确率')
    ax.set_title('Original vs Variant 准确率对比')
    ax.set_ylim([0, 1])
    
    # 在柱子上添加数值
    for bar, acc in zip(bars, df['Accuracy']):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{acc:.3f}', ha='center', va='bottom')
    
    # 2. 箱型图
    ax = axes[0, 1]
    # 这里需要加载详细数据来画箱型图
    # 简化版：只画范围
    for i, (dtype, summary) in enumerate(summaries.items()):
        ax.bar(i, summary['average_accuracy'], 
               yerr=[[summary['average_accuracy'] - summary['min_accuracy']], 
                     [summary['max_accuracy'] - summary['average_accuracy']]],
               capsize=10)
    ax.set_xticks(range(len(summaries)))
    ax.set_xticklabels(summaries.keys())
    ax.set_title('准确率分布范围')
    
    # 3. 准确率差异
    ax = axes[1, 0]
    if 'original' in summaries and 'variant' in summaries:
        orig_acc = summaries['original']['average_accuracy']
        var_acc = summaries['variant']['average_accuracy']
        diff = var_acc - orig_acc
        
        colors = ['red' if diff < 0 else 'green']
        ax.bar(['准确率差异'], [diff], color=colors)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.set_ylabel('Variant - Original')
        ax.set_title(f'准确率差异: {diff:.4f}')
    
    # 4. 统计表
    ax = axes[1, 1]
    ax.axis('tight')
    ax.axis('off')
    
    table_data = []
    for dtype, summary in summaries.items():
        table_data.append([
            dtype,
            f"{summary['average_accuracy']:.4f}",
            f"{summary['std_accuracy']:.4f}",
            f"{summary['min_accuracy']:.4f}",
            f"{summary['max_accuracy']:.4f}"
        ])
    
    table = ax.table(cellText=table_data,
                     colLabels=['数据集', '平均准确率', '标准差', '最小值', '最大值'],
                     cellLoc='center',
                     loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    plt.suptitle('Original vs Variant 对比分析报告', fontsize=16)
    plt.tight_layout()
    plt.savefig('comparison_plot.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_markdown_report(summaries):
    """生成 Markdown 格式的报告"""
    report = """# Original vs Variant 数学问题评测报告

## 评测设置
- 模型: Qwen/Qwen2.5-0.5B-Instruct
- 每道题采样次数: 100次
- 温度: 0.6
- Top-p: 0.95

## 结果对比

| 数据集 | 平均准确率 | 标准差 | 最低准确率 | 最高准确率 |
|--------|------------|--------|------------|------------|
"""
    
    for dtype, summary in summaries.items():
        report += f"| {dtype} | {summary['average_accuracy']:.4f} | {summary['std_accuracy']:.4f} | {summary['min_accuracy']:.4f} | {summary['max_accuracy']:.4f} |\n"
    
    # 计算差异
    if 'original' in summaries and 'variant' in summaries:
        orig = summaries['original']['average_accuracy']
        var = summaries['variant']['average_accuracy']
        diff = var - orig
        diff_percent = (diff / orig * 100) if orig > 0 else 0
        
        report += f"\n## 关键发现\n"
        report += f"- Variant 比 Original 的准确率 **{'高' if diff > 0 else '低'} {abs(diff):.4f}** ({abs(diff_percent):.2f}%)\n"
        
        if diff > 0:
            report += f"- 变量替换对模型性能有积极影响\n"
        elif diff < 0:
            report += f"- 变量替换对模型性能有负面影响\n"
        else:
            report += f"- 变量替换对模型性能无显著影响\n"
    
    report += f"\n![对比图表](comparison_plot.png)\n"
    
    with open('comparison_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✓ 报告已生成: comparison_report.md")

if __name__ == "__main__":
    # 加载结果
    summaries = load_results()
    
    if not summaries:
        print("未找到结果文件，请先运行评测")
    else:
        print(f"加载了 {len(summaries)} 个数据集的结果")
        
        # 创建可视化
        create_comparison_plot(summaries)
        
        # 生成报告
        generate_markdown_report(summaries)