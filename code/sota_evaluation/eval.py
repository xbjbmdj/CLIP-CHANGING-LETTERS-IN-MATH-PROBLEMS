import json
import time
import os
import re
import sys
from openai import OpenAI

# Configure client (keeps existing settings)
client = OpenAI(api_key="...", base_url="https://llmapi.paratera.com")

ROOT_DIR = os.path.dirname(__file__)
INPUT_PATH = os.path.join(ROOT_DIR, "o1517.json")
# Default output path; can be overridden by providing a filename as first arg
DEFAULT_OUTPUT = os.path.join(ROOT_DIR, "ori1.jsonl")
if len(sys.argv) > 1:
    arg = sys.argv[1]
    OUTPUT_PATH = arg if os.path.isabs(arg) else os.path.join(ROOT_DIR, arg)
else:
    OUTPUT_PATH = DEFAULT_OUTPUT

def eval_instance(inst, idx):
    prompt = (
        "您是一名数学家。接下来，你需要解答一个简单的填空题。如果您不会做，也请尽可能尝试，并猜测一个答案。让我们一步一步仔细思考。在解答末尾，请将答案放在\\boxed中。题目是：\n"
        + inst.get("input", "")
    )
    print(prompt)
    messages = [{"role": "user", "content": prompt}]

    try:
        start = time.perf_counter()
        response = client.chat.completions.create(
            model="DeepSeek-V3.2-Thinking",
            messages=messages
        )
        end = time.perf_counter()
        elapsed = end - start

        # Try to extract usage tokens robustly
        usage = None
        try:
            usage = getattr(response, "usage", None)
        except Exception:
            usage = None
        if usage is None:
            try:
                usage = response["usage"]
            except Exception:
                usage = None

        prompt_tokens = None
        completion_tokens = None
        total_tokens = None
        if usage is not None:
            # usage may be an object or dict
            prompt_tokens = getattr(usage, "prompt_tokens", None) if not isinstance(usage, dict) else usage.get("prompt_tokens")
            completion_tokens = getattr(usage, "completion_tokens", None) if not isinstance(usage, dict) else usage.get("completion_tokens")
            total_tokens = getattr(usage, "total_tokens", None) if not isinstance(usage, dict) else usage.get("total_tokens")

        # Extract fields if available
        choice = response.choices[0].message
        reasoning = getattr(choice, "reasoning_content", "")
        content = getattr(choice, "content", "")

        # Extract the last contiguous digit substring from answer
        # Returns the last sequence of 0-9 digits if present, else None
        last_digits = None
        try:
            digit_seqs = re.findall(r"\d+", content or "")
            if digit_seqs:
                last_digits = digit_seqs[-1]
        except Exception:
            last_digits = None

        meta = {"id": getattr(response, 'id', None), "model": getattr(response, 'model', None)}

        # Compare extracted digits to instance target for exact match (store as 0/1)
        last_matches_target = 0
        try:
            target = inst.get("target")
            if last_digits is not None and target is not None:
                last_matches_target = 1 if str(last_digits) == str(target) else 0
        except Exception:
            last_matches_target = 0

        return {
            "id": inst.get("id"),
            "input": inst.get("input"),
            "reasoning": reasoning,
            "answer": content,
            "last_digits": last_digits,
            "last_matches_target": last_matches_target,
            "ok": True,
            "elapsed_seconds": elapsed,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "meta": meta,
        }
    except Exception as e:
        return {"id": inst.get("id"), "input": inst.get("input"), "error": str(e), "ok": False}


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    instances = data.get("instances", [])
    # Ensure output file exists
    cnt=0
    with open(OUTPUT_PATH, "a", encoding="utf-8") as out_f:
        for i, inst in enumerate(instances, start=1):
            cnt+=1
            print(f"Evaluating instance {i}/{len(instances)} id={inst.get('id')}")
            result = eval_instance(inst, i)
            out_f.write(json.dumps(result, ensure_ascii=False) + "\n")
            out_f.flush()
            # Small delay to avoid rate limits
            time.sleep(0.5)


if __name__ == "__main__":
    main()