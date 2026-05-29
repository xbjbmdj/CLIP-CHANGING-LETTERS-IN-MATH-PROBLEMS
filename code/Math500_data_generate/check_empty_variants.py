import json
import os


def check_missing_variants():
    # 目标文件名
    input_file = "final_clean_data.jsonl"

    print(f"正在检查文件: {input_file} ...")

    empty_ids = []
    total_lines = 0

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue

                total_lines += 1
                try:
                    data = json.loads(line)
                    idx = data.get('id')
                    variants = data.get('variants')

                    # 检查 variants 是否为空
                    # 包含情况: 空字符串 "", None, 或者字段不存在
                    if not variants or str(variants).strip() == "":
                        empty_ids.append(idx)
                        # 如果你想看到具体的原始题目，可以取消下面这行的注释
                        # print(f"发现空 variants -> ID: {idx}")

                except json.JSONDecodeError:
                    print(f"警告: 第 {total_lines} 行 JSON 解析失败")
                    continue

        # --- 输出结果 ---
        print("-" * 30)
        print(f"检查完成。总扫描行数: {total_lines}")

        if len(empty_ids) > 0:
            print(f"发现 {len(empty_ids)} 条数据的 'variants' 字段为空。")
            print("ID 列表如下:")
            print(empty_ids)

            # 将结果保存到文件方便查看
            with open("empty_variants_ids.txt", "w", encoding="utf-8") as f_out:
                f_out.write(str(empty_ids))
            print(f"\nID 列表已保存至 empty_variants_ids.txt")
        else:
            print("完美！没有发现 variants 为空的数据。")

    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")


if __name__ == "__main__":
    check_missing_variants()