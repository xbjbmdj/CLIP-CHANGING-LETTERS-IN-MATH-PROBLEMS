import json
import subprocess
import time
import random

INPUT_FILE = "math500_with_id.jsonl"
OUTPUT_FILE = "math500_ollama.jsonl"

# # 一题生成多少个扰动版本
# VARIANTS_PER_PROBLEM = 4

# 你本地 Ollama 模型名称（务必改成你实际拉取的模型）
OLLAMA_MODEL = "llama3.1:8b"


# OLLAMA_MODEL = "llama3:8b"

candidate_chars = list(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "αβγδϵζηθικλμνξοπρστυφχψω"
)

def call_ollama(prompt):
    """
    调用本地 Ollama 模型并返回生成内容。
    """
    cmd = ["ollama", "run", OLLAMA_MODEL]

    # 启动 subprocess
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    out, _ = process.communicate(prompt.encode("utf-8"))
    return out.decode("utf-8")


def build_prompt(problem):
    """
    构造扰动生成 prompt
    """
    replace_list = random.sample(candidate_chars, 20)
    print("替换列表:", replace_list)
    return f"""
你是一个严格的数学变量替换系统，你的任务是对题目执行【字符级别的强制替换】，不允许做任何推理或改写。

【极其重要：必须遵守以下约束】
1. 你只能替换“数学变量”，包括：
   - 26 个英文字母（a–z, A–Z）
   - 常见希腊字母（αβγδ…ω）
2. 数学变量必须严格按照它们【在题目中第一次出现的顺序】进行编号：
   第 1 个变量 → replace_list[0]
   第 2 个变量 → replace_list[1]
   …
3. 同一个原始变量出现多次时，必须替换成同一个新字符。
4. 不允许修改以下内容：
   - 中文、英文单词（如 Angela、height、area 等）
   - 数字、单位、运算符
   - 任何非变量字符
   - 整句结构、换行格式
5. 不允许改写题目，不允许添加额外解释。
6. 若题目中完全不存在数学变量，则必须输出：
   无法更改题目

【输出格式要求（必须严格遵守）】
你必须只输出：
1. 完整替换后的题目文本（不可省略原本换行）
或
2. “无法更改题目”

【替换列表】
replace_list = {replace_list}

【现在开始执行】
下面是题目：

{problem}
"""


def main():
    processed_ids = set()

    # 如果已存在输出文件，则跳过已处理过的 id
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                obj = json.loads(line)
                processed_ids.add(obj["id"])
    except FileNotFoundError:
        pass

    print(f"已处理 {len(processed_ids)} 条，将跳过这些。")

    with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
            open(OUTPUT_FILE, "a", encoding="utf-8") as outfile:

        num=0

        for line in infile:
            if num>=10:
                break
            num+=1

            obj = json.loads(line)
            idx = obj["id"]

            if idx in processed_ids:
                continue  # 断点续跑

            problem = obj["problem"]
            prompt = build_prompt(problem)
            print(f"正在生成：id={idx}...")

            response = call_ollama(prompt)

            # 写入文件
            outfile.write(json.dumps({
                "id": idx,
                "original": problem,
                "variants": response
            }, ensure_ascii=False) + "\n")
            outfile.flush()

            print(f"id={idx} 完成")
            time.sleep(0.2)  # 防止 CPU 占用过高

    print("全部生成完成！输出文件：", OUTPUT_FILE)


if __name__ == "__main__":
    main()
