# download_qwen_tsinghua.py
import os

# 设置清华镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from modelscope import snapshot_download

# 下载Qwen2.5-0.5B-Instruct
model_dir = snapshot_download(
    'qwen/Qwen2.5-0.5B-Instruct',  # 注意：ModelScope使用小写qwen
    cache_dir='/root/shared-nvme/models',
    revision='master'
)

print(f"✅ 模型已下载到: {model_dir}")