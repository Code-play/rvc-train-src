# TMP: 上传音频到Kaggle数据集 | 依赖: kaggle CLI | 保留: 否
import sys; sys.stdout.reconfigure(encoding='utf-8')
import os, subprocess, json, glob, shutil

# ==== 1. 配置 Kaggle API Token ====
token = input("请粘贴你的 Kaggle API Token: ").strip()
os.makedirs(os.path.expanduser('~/.kaggle'), exist_ok=True)
with open(os.path.expanduser('~/.kaggle/access_token'), 'w') as f:
    f.write(token)
os.environ['KAGGLE_API_TOKEN'] = token
print("Token saved")

# ==== 2. 安装 kaggle CLI ====
subprocess.run([sys.executable, '-m', 'pip', 'install', 'kaggle', '-q'], check=True)
print("kaggle CLI installed")

# ==== 3. 准备数据文件夹 ====
base_dir = 'D:\\sundries\\tools\\RVC\\Retrieval-based-Voice-Conversion-WebUI-2.2.231006\\Retrieval-based-Voice-Conversion-WebUI-2.2.231006'
dataset_dir = os.path.join(base_dir, 'kaggle_dataset')
if os.path.exists(dataset_dir):
    shutil.rmtree(dataset_dir)
os.makedirs(dataset_dir)

# 复制 opt/ 里的音频文件
opt_dir = os.path.join(base_dir, 'opt')
for f in glob.glob(os.path.join(opt_dir, '*')):
    shutil.copy2(f, dataset_dir)
print(f"Copied {len(os.listdir(dataset_dir))} files to {dataset_dir}")

# ==== 4. 创建 metadata ====
metadata = {
    "title": "taffie",
    "id": "codenya/taffie",
    "licenses": [{"name": "CC0-1.0"}]
}
with open(os.path.join(dataset_dir, 'dataset-metadata.json'), 'w') as f:
    json.dump(metadata, f, indent=2)
print("Metadata created")

# ==== 5. 上传 ====
print("Uploading dataset...")
os.chdir(dataset_dir)
result = subprocess.run(['kaggle', 'datasets', 'create', '-p', dataset_dir, '--public', '-q', '-r', 'skip'],
                       capture_output=True, text=True, env={**os.environ, 'KAGGLE_API_TOKEN': token})
if result.returncode == 0:
    print("Upload success!")
else:
    # 如果已存在则创建新版本
    print(f"Create failed (may already exist), trying version update: {result.stderr}")
    result2 = subprocess.run(['kaggle', 'datasets', 'version', '-p', dataset_dir, '-m', 'initial upload', '-q', '-r', 'skip'],
                            capture_output=True, text=True, env={**os.environ, 'KAGGLE_API_TOKEN': token})
    if result2.returncode == 0:
        print("Version update success!")
    else:
        print(f"Version update failed: {result2.stderr}")
