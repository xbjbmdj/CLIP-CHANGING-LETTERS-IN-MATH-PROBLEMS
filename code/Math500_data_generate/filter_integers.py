import json


def is_valid_non_negative_integer(value):
    """
    判断一个值是否为非负整数 (>= 0)。
    条件：
    1. 能被解析为整数。
    2. 数值必须大于等于 0。
    """
    try:
        # 确保是字符串并去除首尾空格
        s = str(value).strip()

        # 尝试转换为整数
        val = int(s)

        # 检查是否为非负数 (排除负数)
        if val >= 0:
            return True
        else:
            return False

    except ValueError:
        # 无法转换为整数（比如分数、逗号分隔、非数字字符）
        return False


def filter_dataset(input_file, output_file):
    count_total = 0
    count_kept = 0

    print(f"正在处理文件: {input_file} ...")

    with open(input_file, 'r', encoding='utf-8') as f_in, \
            open(output_file, 'w', encoding='utf-8') as f_out:

        for line in f_in:
            if not line.strip():
                continue

            count_total += 1
            try:
                data = json.loads(line)
                answer = data.get('answer', '')

                # 使用新的判断逻辑：是非负整数才保留
                if is_valid_non_negative_integer(answer):
                    f_out.write(json.dumps(data, ensure_ascii=False) + '\n')
                    count_kept += 1

            except json.JSONDecodeError:
                print(f"警告: 第 {count_total} 行 JSON 格式错误，已跳过。")
                continue

    print("-" * 30)
    print(f"处理完成！")
    print(f"原始数据总行数: {count_total}")
    print(f"保留的非负整数行数: {count_kept}")
    print(f"被过滤掉的行数: {count_total - count_kept}")
    print(f"结果已保存至: {output_file}")


# --- 配置部分 ---
input_filename = 'final_dataset_perfect.jsonl'  # 输入文件名
output_filename = 'positive_integer_dataset.jsonl'  # 输出文件名

if __name__ == '__main__':
    try:
        filter_dataset(input_filename, output_filename)
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{input_filename}'，请确保文件在当前目录下。")