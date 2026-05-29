import json
import time
import random
from openai import OpenAI
import os
import api_key

INPUT_FILE = "math500_with_id.jsonl"
OUTPUT_FILE = "math500_augmented.jsonl"

# 通义千问API配置（兼容OpenAI格式）
QWEN_API_KEY = api_key.api_key  # 替换为你的API密钥
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-max"  # 模型名称：qwen-max/qwen-plus/qwen-turbo等

# 初始化OpenAI客户端（兼容模式）
client = OpenAI(
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
)

candidate_chars = list(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    #"αβγδϵζηθικλμνξορστυφχψω"
)


def call_qwen(prompt):
    """
    调用通义千问API（兼容OpenAI格式）并返回生成内容。
    """
    try:
        completion = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,  # 确保输出稳定
            max_tokens=1000
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"API调用错误: {e}")
        return "无法更改题目"


def build_prompt(problem):
    """
    构造扰动生成prompt
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

    # 如果已存在输出文件，则跳过已处理过的id
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

        num = 0

        for line in infile:
            # if num >= 100:
            #     break
            # num += 1

            obj = json.loads(line)
            idx = obj["id"]

            if idx in processed_ids:
                continue  # 断点续跑

            problem = obj["problem"]
            prompt = build_prompt(problem)
            print(f"正在生成：id={idx}...")

            response = call_qwen(prompt)

            # 写入文件
            outfile.write(json.dumps({
                "id": idx,
                "original": problem,
                "variants": response
            }, ensure_ascii=False) + "\n")
            outfile.flush()

            print(f"id={idx} 完成")
            time.sleep(1)  # 千问API有速率限制，适当增加延迟

    print("全部生成完成！输出文件：", OUTPUT_FILE)


if __name__ == "__main__":
    main()