import json
import os


def filter_visual_problems():
    # 定义输入和输出文件名
    input_file = "filtered_numbers.jsonl"  # 上一步的输出
    output_file = "final_clean_data.jsonl"  # 最终清洗完成的文件

    print(f"正在处理文件: {input_file} ...")

    total_count = 0
    visual_count = 0
    kept_count = 0

    try:
        with open(input_file, 'r', encoding='utf-8') as f_in, \
                open(output_file, 'w', encoding='utf-8') as f_out:

            for line in f_in:
                line = line.strip()
                if not line: continue

                total_count += 1
                try:
                    data = json.loads(line)

                    # 获取原始题目内容
                    original_text = data.get('original', '')
                    variant_text = data.get('variants', '')

                    # 检查是否包含 [asy] 标签
                    # 通常图示代码被包裹在 [asy]...[/asy] 之间
                    if "[asy]" in original_text or "[asy]" in variant_text:
                        visual_count += 1
                        # 这是一个带图示的题目，跳过写入
                        continue

                    # 如果没有图示，保留该行
                    f_out.write(json.dumps(data, ensure_ascii=False) + '\n')
                    kept_count += 1

                except json.JSONDecodeError:
                    print(f"警告: 第 {total_count} 行 JSON 解析失败，已跳过。")
                    continue

        print("-" * 30)
        print("图示题目过滤完成！")
        print(f"原始总行数: {total_count}")
        print(f"已删除 (含图示): {visual_count}")
        print(f"最终保留行数: {kept_count}")
        print(f"结果已保存至: {output_file}")

    except FileNotFoundError:
        print(
            f"错误: 找不到输入文件 {input_file}，请确保上一步 (Step 3) 已完成。")


if __name__ == "__main__":
    filter_visual_problems()