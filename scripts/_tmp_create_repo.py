# TMP: 创建 GitHub 仓库 | 保留: 否
import sys; sys.stdout.reconfigure(encoding='utf-8')
import requests
r = requests.post("https://api.github.com/user/repos",
    json={"name": "rvc-train-src", "private": False, "auto_init": False},
    headers={"Authorization": "token PLACEHOLDER"},
    proxies={"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"},
    timeout=30)
print(r.status_code, r.text[:300])
