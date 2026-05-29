import json
import os
import re


def is_valid_numerical_answer(answer_str):
    """
    判断逻辑：
    1. 允许数字、标点、运算符号。
    2. 允许特定的 LaTeX 命令 (如 \frac, \sqrt, \pi)。
    3. 允许特定的字母常量 (e, i)。
    4. 禁止其他任何字母 (x, y, sin, cos, cm, degrees 等)。
    """
    if not answer_str or not isinstance(answer_str, str):
        return False

    # --- 第一步：剔除合法的 LaTeX 命令和符号 ---
    # 我们把这些命令替换为空字符串，因为它们虽然包含字母，但属于"格式"或"允许的符号"
    # 注意：\pi 是用户指定允许的，\circ (度数) 也是数字常带的符号
    allowed_commands = [
        r'\\dfrac', r'\\frac', r'\\cfrac',  # 分数
        r'\\sqrt',  # 根号
        r'\\left', r'\\right',  # 括号修饰
        r'\\pi',  # 圆周率 (包含 pi，允许)
        r'\\circ',  # 度数符号 (包含 circ，允许)
        r'\\text', r'\\mathrm', r'\\mathbf',  # 字体命令 (去掉命令本身，检查里面的内容)
        r'\\pm', r'\\mp', r'\\cdot',  # 运算符
        r'\\,'  # 空格
    ]

    clean_str = answer_str

    # 按顺序移除这些命令
    for cmd in allowed_commands:
        clean_str = re.sub(cmd, '', clean_str)

    # --- 第二步：核心检查 ---
    # 遍历剩余字符串中的每一个字符
    for char in clean_str:
        # 如果字符是字母 (a-z 或 A-Z)
        if char.isalpha():
            # 只有 e 和 i 是允许的
            # 注意：这里我们只允许小写的 e 和 i (数学常数通常小写)
            # 如果你的数据中有大写 E (科学计数法) 也可以加上 'E'
            if char not in ['e', 'i', 'E', 'I']:
                return False

    # 如果循环结束没有发现非法字母，则是纯数字/合法常量
    return True


def process_filtering():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, 'filtered_with_answers.jsonl')
    output_file = os.path.join(current_dir, 'filtered_numbers.jsonl')

    print(f"正在处理文件: {input_file}")

    kept_count = 0
    deleted_count = 0

    try:
        with open(input_file, 'r', encoding='utf-8') as f_in, \
                open(output_file, 'w', encoding='utf-8') as f_out:

            for line in f_in:
                line = line.strip()
                if not line: continue

                try:
                    data = json.loads(line)
                    answer = data.get('answer', '')

                    if is_valid_numerical_answer(answer):
                        f_out.write(json.dumps(data, ensure_ascii=False) + '\n')
                        kept_count += 1
                    else:
                        deleted_count += 1
                        # 如果想看删除了什么，取消下面这行的注释
                        # print(f"删除: {answer}")

                except json.JSONDecodeError:
                    continue

        print("-" * 30)
        print("筛选完成！")
        print(f"保留行数 (数字/pi/e/i): {kept_count}")
        print(f"删除行数 (含其他字母):   {deleted_count}")
        print(f"结果已保存至: {output_file}")

    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")


if __name__ == "__main__":
    process_filtering()