import json

input_file = "math500_augmented.jsonl"
output_file = "filtered.jsonl"

with open(input_file, "r", encoding="utf-8") as fin, \
        open(output_file, "w", encoding="utf-8") as fout:
    for line in fin:
        if not line.strip():
            continue

        data = json.loads(line)

        # 跳过 variants 为 "无法更改题目" 的行
        if data.get("variants") == "无法更改题目":
            continue

        fout.write(json.dumps(data, ensure_ascii=False) + "\n")

print("过滤完成，已写入 filtered.jsonl")
