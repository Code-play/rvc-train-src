# TMP: 安装kaggle CLI并上传音频数据 | 依赖: kaggle | 保留: 否
import sys; sys.stdout.reconfigure(encoding='utf-8')
import os, subprocess, json

# 1. 安装 kaggle CLI
print("Installing kaggle CLI...")
subprocess.run([sys.executable, '-m', 'pip', 'install', 'kaggle', '-q'], check=True)
print("Done")

# 2. 检查是否已有认证
kaggle_dir = os.path.expanduser('~/.kaggle')
has_auth = False
if os.path.exists(os.path.join(kaggle_dir, 'kaggle.json')):
    has_auth = True
    print("Found kaggle.json credentials")
elif os.path.exists(os.path.join(kaggle_dir, 'access_token')):
    has_auth = True
    print("Found access_token")
elif 'KAGGLE_API_TOKEN' in os.environ:
    has_auth = True
    print("Found KAGGLE_API_TOKEN env var")

if not has_auth:
    print("\n" + "="*60)
    print("需要 Kaggle API 认证")
    print("="*60)
    print("请在浏览器打开以下页面，创建 API Token：")
    print("  https://www.kaggle.com/settings/api")
    print("\n点击「Create New Token」按钮，下载 kaggle.json 文件")
    print("然后把 kaggle.json 放到这里：")
    print(f"  {kaggle_dir}\\kaggle.json")
    print("="*60)
