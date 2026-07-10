# TMP: 重新打包 RVC bundle，修复 EXCLUDE_DIRS 排除路径问题 | 保留: 否
import sys; sys.stdout.reconfigure(encoding='utf-8')
import os, shutil, zipfile

BASE = r"D:\sundries\tools\RVC\Retrieval-based-Voice-Conversion-WebUI-2.2.231006\Retrieval-based-Voice-Conversion-WebUI-2.2.231006"
ZIP_PATH = os.path.join(BASE, "kaggle_kernel", "rvc-kaggle-base.zip")

# 只排除顶层目录（修复：以前 'train' 会误排除 infer/modules/train/）
EXCLUDE_TOP_DIRS = {'.git', '__pycache__', '.venv', 'logs', 'TEMP', 'opt', 'kaggle_kernel',
                    'venv.sh', '.pytest_cache', 'node_modules'}
EXCLUDE_FILES = {'ffmpeg.exe', 'ffprobe.exe', '.gitignore', 'poetry.lock'}
ASSETS_KEEP = {
    'assets/hubert/hubert_base.pt',
    'assets/pretrained_v2/G40k.pth',
    'assets/pretrained_v2/D40k.pth',
}

if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)

tmp_dir = os.path.join(BASE, "kaggle_kernel", "_tmp_bundle")
if os.path.exists(tmp_dir):
    shutil.rmtree(tmp_dir)

os.makedirs(tmp_dir)

# 1. 复制源码（排除正确）
copied = 0
for root, dirs, files in os.walk(BASE):
    for f in files:
        src = os.path.join(root, f)
        rel = os.path.relpath(src, BASE)
        parts = rel.replace('\\', '/').split('/')
        if parts[0] in EXCLUDE_TOP_DIRS:
            continue
        if os.path.basename(rel) in EXCLUDE_FILES:
            continue
        if parts[0] == 'assets':
            continue  # 单独处理
        dst = os.path.join(tmp_dir, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1

# 2. 预训练模型
for src_rel in ASSETS_KEEP:
    src = os.path.join(BASE, src_rel)
    dst = os.path.join(tmp_dir, src_rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)

# 3. requirements_static.txt
with open(os.path.join(tmp_dir, 'requirements_static.txt'), 'w') as f:
    f.write('fairseq==0.12.2\nav==12.3.0\nlibrosa==0.10.2\nsoundfile==0.12.1\nscipy==1.13.1\nscikit-learn==1.6.1\nffmpeg-python==0.2.0\npraat-parselmouth==0.5.0\npyworld==0.3.4\nfaiss-cpu==1.9.0\ntensorboardX==2.6.2.2\nmatplotlib==3.9.3\ngradio==5.12.0\nrequests==2.32.3\nnumba==0.60.0\n')

# 4. 打包
print("Verifying train module files...")
train_files = [p for p in os.listdir(os.path.join(tmp_dir, 'infer', 'modules', 'train')) if p.endswith('.py')]
print(f"  infer/modules/train/ files: {train_files}")

with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, _, files in os.walk(tmp_dir):
        for f in files:
            fp = os.path.join(root, f)
            arcname = os.path.relpath(fp, tmp_dir)
            zf.write(fp, arcname)

total_mb = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(tmp_dir) for f in fs) / 1024 / 1024
zip_mb = os.path.getsize(ZIP_PATH) / 1024 / 1024
print(f"Total files: {copied + len(ASSETS_KEEP)} + 1 (requirements)")
print(f"Total size: {total_mb:.1f} MB, Zip: {zip_mb:.1f} MB")
print(f"Zip: {ZIP_PATH}")

# 清理 temp
shutil.rmtree(tmp_dir)
