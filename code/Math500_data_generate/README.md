这里是修改后的 README。我已将 `filter_integers.py` 整合进项目结构、工作流（作为 Step 8）以及脚本详解中，并将最终产出文件更新为 `positive_integer_dataset.jsonl`。

***

# Math500 Data Augmentation & Filtering Pipeline

本项目构建了一个高精度的数学题目数据处理流水线。主要功能是对 Math500 数据集进行**变量替换增强**，并经过多重清洗（去除失败项、筛选纯数值答案、剔除图示题、ID黑名单剔除），最后进一步筛选出**非负整数**答案，生成最终完美的数据集。

## 📁 项目目录结构

```text
.
├── MATH500.py                  # [数据下载] 将MATH500下载到本地
├── api_key.py                  # [配置] 存放 OpenRouter API Key
├── api_openrouter.py           # [Step 1] 数据增强
├── unique.py                   # [Step 2] 失败清洗
├── merge_answers.py            # [Step 3] 数据合并
├── filter_pure_numbers.py      # [Step 4] 格式筛选
├── filter_visuals.py           # [Step 5] 图示清洗 -> 产出 final_clean_data.jsonl
├── find_imaginary_ids.py       # [Step 6a] 检测虚数 ID
├── check_empty_variants.py     # [Step 6b] 检测空变体 ID
├── prune_invalid_rows.py       # [Step 7] 最终剔除 -> 产出 final_dataset_perfect.jsonl
├── filter_integers.py          # [Step 8] 整数筛选 -> 产出 positive_integer_dataset.jsonl
├── math500_with_id.jsonl       # [源数据] 原始输入文件
├── math500_augmented.jsonl     # [中间产物] Step 1 输出
├── filtered.jsonl              # [中间产物] Step 2 输出
├── filtered_with_answers.jsonl # [中间产物] Step 3 输出
├── filtered_numbers.jsonl      # [中间产物] Step 4 输出
├── final_clean_data.jsonl      # [中间产物] Step 5 输出 (待检测)
├── imaginary_ids.txt           # [中间产物] 待删除的虚数 ID 列表
├── empty_variants_ids.txt      # [中间产物] 待删除的空变体 ID 列表
├── final_dataset_perfect.jsonl # [中间产物] Step 7 输出 (完美格式数据)
├── positive_integer_dataset.jsonl # [最终结果] Step 8 输出 (最终非负整数数据)
└── requirements.txt            # (可选) 项目依赖
```

## 数据下载（data download)
**命令: `python MATH500.py`**

将 MATH500 中数据下载到本地, 下载好的数据将存入`math500_with_id.jsonl`中


## 🚀 完整工作流 (Workflow)

请严格按照以下顺序运行脚本，确保数据流转正确。

### 0. 环境准备
```bash
pip install openai
```

---

### Phase 1: 生成与基础清洗

**Step 1: 数据增强 (Data Augmentation)**
调用大模型进行同构变量替换。
*   命令: `python api_openrouter.py`
*   输出: `math500_augmented.jsonl`

**Step 2: 清洗失败生成 (Filter Failed Generations)**
删除 LLM 返回 "无法更改题目" 的行。
*   命令: `python unique.py`
*   输出: `filtered.jsonl`

**Step 3: 答案合并 (Merge Answers)**
将原始答案关联到变体数据中。
*   命令: `python merge_answers.py`
*   输出: `filtered_with_answers.jsonl`

---

### Phase 2: 格式与内容过滤

**Step 4: 答案格式筛选 (Number Filtering)**
保留纯数值、标准 LaTeX 常数答案，剔除文字描述。
*   命令: `python filter_pure_numbers.py`
*   输出: `filtered_numbers.jsonl`

**Step 5: 图示题目剔除 (Visual Filtering)**
剔除包含 `[asy]` 绘图代码的题目。
*   命令: `python filter_visuals.py`
*   输出: `final_clean_data.jsonl`

---

### Phase 3: 深度检测与最终剔除 (Final Pruning)

**Step 6: 生成黑名单 ID (ID Extraction)**
分别运行以下两个脚本，扫描 `final_clean_data.jsonl` 中残留的问题数据：

1.  **检测虚数答案**:
    *   命令: `python find_imaginary_ids.py`
    *   输出: `imaginary_ids.txt` (包含带 $i$ 的题目ID)
2.  **检测空变体**:
    *   命令: `python check_empty_variants.py`
    *   输出: `empty_variants_ids.txt` (包含 variants 为空的题目ID)

**Step 7: 执行 ID 剔除 (Execute Pruning)**
读取上述生成的两个 txt 文件，从数据集中彻底删除这些行。
*   命令: `python prune_invalid_rows.py`
*   输出: `final_dataset_perfect.jsonl`

---

### Phase 4: 特定数值筛选 (Integer Constraint)

**Step 8: 非负整数筛选 (Non-Negative Integers)**
最后一步，严格筛选答案为**非负整数**（$\ge 0$）的题目，剔除负数、分数、小数及残留的非整数内容。
*   命令: `python filter_integers.py`
*   **最终输出**: `positive_integer_dataset.jsonl`

## 🛠️ 脚本逻辑详解

1.  **`api_openrouter.py`**: 核心生成脚本，使用 LLM 进行变量替换。
2.  **`unique.py` & `merge_answers.py`**: 数据预处理，确保数据结构完整且有效。
3.  **`filter_pure_numbers.py`**: 正则白名单机制，确保答案适合数学推理任务。
4.  **`filter_visuals.py`**: 移除依赖几何图像的题目。
5.  **`find_imaginary_ids.py`**: 特殊处理，识别答案中隐藏的虚数单位 $i$。
6.  **`prune_invalid_rows.py`**: 根据 ID 黑名单进行精确删除。
7.  **`filter_integers.py`**: **[新增]** 最终约束过滤器。只保留 `int(answer) >= 0` 的行，确保数据集仅包含正整数和零，适合基础数值推理训练。

## ⚠️ 注意事项

*   **流程依赖**: Step 6 和 Step 7 必须在 Step 5 完成后运行；Step 8 必须在 Step 7 完成后运行。
*   **文件检查**: 运行 Step 7 前确保存在 txt 黑名单文件；运行 Step 8 前确保存在 `final_dataset_perfect.jsonl`。
*   **最终交付**: 
    *   如果需要包含浮点数/分数的完美数据，请使用 `final_dataset_perfect.jsonl`。
    *   如果仅需要**非负整数**数据，请使用 **`positive_integer_dataset.jsonl`**。