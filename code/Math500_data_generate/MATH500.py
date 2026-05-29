from datasets import load_dataset
import json

# 加载数据集
ds = load_dataset("HuggingFaceH4/MATH-500")
math500 = ds["test"][:500]
# for item in ds["test"]:
#     print(item)
#     print('---------')

# 保存到本地JSONL文件
with open("math500_with_id.jsonl", "w", encoding="utf-8") as f:
    for idx in range(500):
        formatted_data = {
            "id": idx,
            "problem": math500['problem'][idx],
            "answer": math500['answer'][idx],
            "subject": math500['subject'][idx],
            "level": math500['level'][idx]
        }
        json.dump(formatted_data, f, ensure_ascii=False)
        f.write("\n")

print("数据已按指定格式保存到 math500_with_id.jsonl")