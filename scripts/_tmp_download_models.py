import sys
sys.stdout.reconfigure(encoding="utf-8")
import subprocess, os

BASE = r"D:\sundries\tools\RVC\Retrieval-based-Voice-Conversion-WebUI-2.2.231006\Retrieval-based-Voice-Conversion-WebUI-2.2.231006"
URL = "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main"

files = [
    ("assets/hubert",       "hubert_base.pt"),
    ("assets/rmvpe",        "rmvpe.pt"),
    ("assets/pretrained_v2","f0G40k.pth"),
    ("assets/pretrained_v2","f0D40k.pth"),
]

for subdir, name in files:
    dst = os.path.join(BASE, subdir, name)
    if os.path.exists(dst) and os.path.getsize(dst) > 1_000_000:
        print(f"SKIP {name}")
        continue
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    src = f"{URL}/{subdir}/{name}"
    print(f"DL {name} ...")
    # 先试直连，不行再用代理
    r = subprocess.run(
        ["curl", "-L", "-o", dst, src],
        capture_output=True, text=True
    )
    sz = os.path.getsize(dst)
    print(f"  直连结果: exit={r.returncode}, size={sz}")
    if sz < 100_000:
        # 用代理重试
        r2 = subprocess.run(
            ["curl", "-x", "http://127.0.0.1:7890", "-L", "-o", dst, src],
            capture_output=True, text=True
        )
        sz2 = os.path.getsize(dst)
        print(f"  代理结果: exit={r2.returncode}, size={sz2}")

print("完成")
