# TMP: 创建 GitHub 仓库并 push RVC 源码 | 保留: 否
import sys; sys.stdout.reconfigure(encoding='utf-8')
import requests, os, subprocess

TOKEN = os.environ["GITHUB_TOKEN"]
USER = "Code-play"
REPO = "rvc-train-src"
BASE = r"D:\sundries\tools\RVC\Retrieval-based-Voice-Conversion-WebUI-2.2.231006\Retrieval-based-Voice-Conversion-WebUI-2.2.231006"
PROXY = "http://127.0.0.1:7890"
proxies = {"http": PROXY, "https": PROXY}

# 1. 创建 GitHub 仓库（允许已存在）
print("=== 创建 GitHub 仓库 ===")
r = requests.post("https://api.github.com/user/repos",
    json={"name": REPO, "private": False, "auto_init": False},
    headers={"Authorization": f"token {TOKEN}"},
    proxies=proxies, timeout=30)
print(f"POST /user/repos -> {r.status_code}")
if r.status_code == 422:
    print("仓库已存在，继续 push")
elif r.status_code == 201:
    print("仓库创建成功")
else:
    print(f"失败: {r.text[:300]}")
    exit(1)

clone_url = f"https://github.com/{USER}/{REPO}.git"

# 2. git init
os.chdir(BASE)
print(f"\n=== git init in {BASE} ===")

# 如果已有 .git，先清理
if os.path.exists(".git"):
    import shutil
    shutil.rmtree(".git")

subprocess.run(["git", "init"], check=True, capture_output=True)

# 写 .gitignore
with open(os.path.join(BASE, ".gitignore"), "w") as f:
    f.write("""# RVC source-only repo
assets/
train/
logs/
TEMP/
opt/
kaggle_kernel/
__pycache__/
.pytest_cache/
node_modules/
venv.sh/
*.exe
.env
""")

# 设置 remote
remote_url = f"https://{TOKEN}@github.com/{USER}/{REPO}.git"
subprocess.run(["git", "remote", "add", "origin", remote_url], check=True, capture_output=True)
subprocess.run(["git", "config", "user.email", "bot@example.com"], capture_output=True)
subprocess.run(["git", "config", "user.name", "bot"], capture_output=True)

# 3. git add + commit
subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
result = subprocess.run(["git", "commit", "-m", "Initial commit: RVC v2.2.231006 source code"], capture_output=True, text=True)
print(f"Commit: {result.stdout.strip()}{result.stderr.strip()}")

# 4. git push（走代理）
print("\n=== git push ===")
env = os.environ.copy()
env["HTTP_PROXY"] = PROXY
env["HTTPS_PROXY"] = PROXY
result = subprocess.run(["git", "push", "-u", "origin", "master"], capture_output=True, text=True, timeout=120, env=env)
print(f"STDOUT: {result.stdout[:500]}")
print(f"STDERR: {result.stderr[:500]}")
print(f"RC: {result.returncode}")
if result.returncode != 0:
    # 重试一次无代理
    print("代理失败，重试无代理...")
    result = subprocess.run(["git", "push", "-u", "origin", "master"], capture_output=True, text=True, timeout=120)
    print(f"STDOUT: {result.stdout[:500]}")
    print(f"STDERR: {result.stderr[:500]}")
    print(f"RC: {result.returncode}")
else:
    print("Push 成功!")
