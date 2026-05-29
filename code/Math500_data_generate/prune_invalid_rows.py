import json
import os
import ast


def prune_data():
    # --- 配置区域 ---
    # 1. 包含要删除 ID 的文件列表
    id_files = [
        "empty_variants_ids.txt",
        "imaginary_ids.txt"
    ]

    # 2. 待处理的数据文件 (根据你的描述应该是这个名字，如果不对请修改)
    # 注意：你之前生成的最终文件叫 final_clean_data.jsonl
    # 如果你要处理的是 filter_clean_data.jsonl，请保持不变；否则请改为对应文件名
    input_file = "final_clean_data.jsonl"

    # 3. 输出的新文件名
    output_file = "final_dataset_perfect.jsonl"

    # ----------------

    print(f"开始执行数据剔除任务...")

    # 第一步：读取并合并所有要删除的 ID
    ids_to_remove = set()

    for file_path in id_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # 使用 ast.literal_eval 安全地将字符串列表 "[1, 2, 3]" 转为 Python 列表
                        id_list = ast.literal_eval(content)
                        ids_to_remove.update(id_list)
                        print(
                            f"  -> 已加载 {file_path}: 包含 {len(id_list)} 个 ID")
            except Exception as e:
                print(f"  -> 读取 {file_path} 失败: {e}")
        else:
            print(f"  -> 警告: 找不到文件 {file_path}，跳过。")

    print(f"总计需要删除的 ID 数量 (去重后): {len(ids_to_remove)}")
    print("-" * 30)

    # 第二步：逐行读取数据并过滤
    if not os.path.exists(input_file):
        print(f"错误: 找不到输入文件 {input_file}，请检查文件名。")
        return

    kept_count = 0
    removed_count = 0

    print(f"正在处理 {input_file} ...")

    try:
        with open(input_file, 'r', encoding='utf-8') as f_in, \
                open(output_file, 'w', encoding='utf-8') as f_out:

            for line in f_in:
                if not line.strip(): continue

                try:
                    data = json.loads(line)
                    curr_id = data.get('id')

                    # 检查当前 ID 是否在删除列表中
                    if curr_id in ids_to_remove:
                        removed_count += 1
                        # 跳过写入，相当于删除
                    else:
                        f_out.write(line)
                        kept_count += 1

                except json.JSONDecodeError:
                    continue

        print("-" * 30)
        print("处理完成！")
        print(f"原文件保留行数: {kept_count}")
        print(f"本次删除行数:   {removed_count}")
        print(f"最终结果已保存至: {output_file}")

    except Exception as e:
        print(f"处理过程中发生错误: {e}")


if __name__ == "__main__":
    prune_data()