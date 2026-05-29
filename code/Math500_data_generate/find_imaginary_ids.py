import json
import os


def find_imaginary_numbers():
    # 默认读取最终清洗后的文件，你也可以改成 "filtered_numbers.jsonl"
    input_file = "final_clean_data.jsonl"

    print(f"正在扫描文件: {input_file} 中的虚数答案...")

    imaginary_ids = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue

                try:
                    data = json.loads(line)
                    idx = data.get('id')
                    answer = data.get('answer', '')

                    # --- 核心检测逻辑 ---

                    # 1. 创建一个临时字符串用于检查
                    temp_ans = answer

                    # 2. 移除干扰项：移除 \pi, \sin, \phi 等包含 'i' 的 LaTeX 命令
                    # 否则 \pi 会被误判为包含 i
                    ignore_list = [
                        r'\pi', r'\Pi',  # 圆周率
                        r'\sin', r'\arcsin',  # 正弦
                        r'\phi', r'\Phi',  # 黄金分割等
                        r'\psi', r'\Psi',  # 普赛
                        r'\sigma', r'\Sigma',  # 西格玛
                        r'\lim', r'\min',  # 极限、极小
                        r'\right',  # 括号标记 \right)
                        r'\circ'  # 角度符号 (包含 i)
                    ]

                    for ignore_item in ignore_list:
                        temp_ans = temp_ans.replace(ignore_item, '')

                    # 3. 检查剩余字符串中是否还有 'i'
                    if 'i' in temp_ans:
                        imaginary_ids.append(idx)
                        # 如果你想看具体的答案，取消下面这行的注释
                        # print(f"ID: {idx} | Answer: {answer}")

                except json.JSONDecodeError:
                    continue

        # --- 输出结果 ---
        print("-" * 30)
        print(f"扫描完成。")
        print(f"共发现 {len(imaginary_ids)} 个包含虚数 i 的题目。")
        print("ID 列表如下：")
        print("-" * 30)

        # 打印 ID 列表
        print(imaginary_ids)

        # 也可以保存到一个txt文件中方便查看
        with open("imaginary_ids.txt", "w", encoding="utf-8") as f_out:
            f_out.write(str(imaginary_ids))
            print(f"\nID列表已保存至 imaginary_ids.txt")

    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")


if __name__ == "__main__":
    find_imaginary_numbers()