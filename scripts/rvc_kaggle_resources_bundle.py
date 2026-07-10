# TMP: 打包 RVC 仓库+预训练模型为 Kaggle Dataset | 依赖: kagglehub, 网络 | 保留: 否
import sys; sys.stdout.reconfigure(encoding='utf-8')
import os, shutil, glob, tempfile
import kagglehub

BASE = r"D:\sundries\tools\RVC\Retrieval-based-Voice-Conversion-WebUI-2.2.231006\Retrieval-based-Voice-Conversion-WebUI-2.2.231006"

# Kaggle 配置（从 access_token 文件读取，不硬编码）
token_path = os.path.expanduser('~/.kaggle/access_token')
if os.path.exists(token_path):
    with open(token_path) as f:
        TOKEN = f.read().strip()
else:
    TOKEN = os.environ.get("KAGGLE_API_TOKEN", "")
    if not TOKEN:
        raise RuntimeError("未找到 Kaggle API Token！请先运行 kagglehub.login() 或配置 ~/.kaggle/access_token")

DATASET_HANDLE = "codenya/rvc-kaggle-base"

# 设置环境变量（kagglehub 会自动读取，无需 login()）
os.environ["KAGGLE_API_TOKEN"] = TOKEN
print("Token configured (env var)")

# 需要排除的目录/文件
EXCLUDE_DIRS = {'.git', '__pycache__', '.venv', 'logs', 'TEMP', 'opt', 'kaggle_kernel',
                'venv.sh', '.pytest_cache', 'node_modules', 'train'}
EXCLUDE_FILES = {'ffmpeg.exe', 'ffprobe.exe', '.gitignore', 'poetry.lock'}

# 目标目录结构:
# rvc-kaggle-base/
#   repo/              <- RVC 源码
#   assets/
#     hubert/hubert_base.pt
#     pretrained_v2/G40k.pth
#     pretrained_v2/D40k.pth
#   requirements_static.txt  <- 固定版本的依赖

ASSETS_KEEP_MAP = {
    'assets/hubert/hubert_base.pt': 'assets/hubert/hubert_base.pt',
    'assets/pretrained_v2/G40k.pth': 'assets/pretrained_v2/G40k.pth',
    'assets/pretrained_v2/D40k.pth': 'assets/pretrained_v2/D40k.pth',
}

def create_bundle():
    print("=== 创建资源包 ===")
    with tempfile.TemporaryDirectory() as tmp:
        bundle_dir = os.path.join(tmp, 'bundle')
        repo_dir = os.path.join(bundle_dir, 'repo')
        os.makedirs(repo_dir)

        # 1. 复制源码到 repo/
        copied = 0
        for root, dirs, files in os.walk(BASE):
            for f in files:
                src = os.path.join(root, f)
                rel = os.path.relpath(src, BASE)
                parts = rel.replace('\\', '/').split('/')
                # 跳过排除目录
                if any(p in EXCLUDE_DIRS for p in parts):
                    continue
                if os.path.basename(rel) in EXCLUDE_FILES:
                    continue
                # 跳过 assets（单独处理）
                if parts[0] == 'assets':
                    continue
                dst = os.path.join(repo_dir, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1

        # 2. 复制预训练模型到 assets/
        assets_dir = os.path.join(bundle_dir, 'assets')
        for src_rel, dst_rel in ASSETS_KEEP_MAP.items():
            src = os.path.join(BASE, src_rel)
            dst = os.path.join(bundle_dir, dst_rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            sz = os.path.getsize(dst)
            print(f"  模型 {dst_rel}: {sz/1024/1024:.1f} MB")

        # 3. 创建固定依赖文件
        req_path = os.path.join(bundle_dir, 'requirements_static.txt')
        with open(req_path, 'w') as f:
            f.write('''# RVC 训练依赖（固定版本，避免 pip 热装失败）
fairseq==0.12.2
av==12.3.0
librosa==0.10.2
soundfile==0.12.1
scipy==1.13.1
scikit-learn==1.6.1
ffmpeg-python==0.2.0
praat-parselmouth==0.5.0
pyworld==0.3.4
faiss-cpu==1.9.0
tensorboardX==2.6.2.2
matplotlib==3.9.3
gradio==5.12.0
requests==2.32.3
numba==0.60.0
''')

        print(f"\n源码文件数: {copied}")
        total_mb = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(bundle_dir) for f in fs) / 1024 / 1024
        print(f"总大小: {total_mb:.1f} MB")

        print("\n=== 目录结构 ===")
        for root, dirs, files in os.walk(bundle_dir):
            level = root.replace(bundle_dir, '').count(os.sep)
            indent = '  ' * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = '  ' * (level + 1)
            for f in sorted(files)[:15]:
                sz = os.path.getsize(os.path.join(root, f))
                print(f"{subindent}{f} ({sz/1024/1024:.1f} MB)" if sz > 1024*1024 else f"{subindent}{f}")
            if len(files) > 15:
                print(f"{subindent}... and {len(files)-15} more files")

        # 4. 上传
        print(f"\n=== 上传到 {DATASET_HANDLE} ===")
        try:
            result = kagglehub.dataset_upload(DATASET_HANDLE, bundle_dir)
            print(f"上传成功: {result}")
        except Exception as e:
            print(f"首次上传失败: {e}")
            print("尝试创建新版本...")
            try:
                result = kagglehub.dataset_upload(
                    DATASET_HANDLE, bundle_dir,
                    version_notes="Initial bundle: RVC repo + hubert_base + G40k + D40k"
                )
                print(f"新版本上传成功: {result}")
            except Exception as e2:
                print(f"新版本上传也失败: {e2}")

if __name__ == "__main__":
    create_bundle()
