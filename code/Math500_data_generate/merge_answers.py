import json
import os


def process_merge():
    # 1. 自动获取当前脚本所在的目录 (即 C:\Users\HP\Desktop\...\Math500)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. 配置文件路径 (根据你的截图文件名)
    source_file = os.path.join(current_dir,
                               'math500_with_id.jsonl')  # 来源文件(提供answer)
    target_file = os.path.join(current_dir,
                               'filtered.jsonl')  # 目标文件(需要填入answer)
    output_file = os.path.join(current_dir,
                               'filtered_with_answers.jsonl')  # 输出文件

    print(f"正在工作目录: {current_dir} 下运行")
    print("-" * 30)

    # 3. 第一步：读取 math500_with_id.jsonl 建立 {id: answer} 索引
    id_answer_map = {}
    print(f"1. 正在读取 {os.path.basename(source_file)} ...")

    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line: continue
                try:
                    data = json.loads(line)
                    # 提取 id 和 answer
                    item_id = data.get('id')
                    answer = data.get('answer')

                    if item_id is not None:
                        id_answer_map[item_id] = answer
                except json.JSONDecodeError:
                    print(f"   [警告] 第 {line_num} 行 JSON 格式错误，已跳过")
        print(f"   已加载 {len(id_answer_map)} 个答案索引。")

    except FileNotFoundError:
        print(f"[错误] 找不到文件: {source_file}")
        return

    # 4. 第二步：读取 filtered.jsonl 并填入答案
    print(f"2. 正在处理 {os.path.basename(target_file)} ...")

    matched_count = 0
    total_processed = 0

    try:
        with open(target_file, 'r', encoding='utf-8') as f_in, \
                open(output_file, 'w', encoding='utf-8') as f_out:

            for line in f_in:
                line = line.strip()
                if not line: continue

                total_processed += 1
                data = json.loads(line)
                current_id = data.get('id')

                # 核心逻辑：根据 ID 匹配答案
                if current_id in id_answer_map:
                    data['answer'] = id_answer_map[current_id]
                    matched_count += 1
                else:
                    # 如果没找到答案，标记为空或打印警告
                    print(f"   [提示] ID {current_id} 在源文件中未找到答案")
                    data['answer'] = ""

                    # 写入新文件 (ensure_ascii=False 保证中文和公式不乱码)
                f_out.write(json.dumps(data, ensure_ascii=False) + '\n')

    except FileNotFoundError:
        print(f"[错误] 找不到文件: {target_file}")
        return

    # 5. 总结
    print("-" * 30)
    print("处理完成！")
    print(f"共扫描目标行数: {total_processed}")
    print(f"成功匹配答案数: {matched_count}")
    print(f"结果已保存至: {output_file}")


if __name__ == "__main__":
    process_merge()