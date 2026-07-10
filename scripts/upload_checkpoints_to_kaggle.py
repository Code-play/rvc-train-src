# TMP: 在训练过程中自动上传 checkpoint 到 Kaggle Models | 依赖: kagglehub | 保留: 否
"""
用法（在 Notebook 中）:
  import threading
  t = threading.Thread(target=upload_checkpoint_loop, args=("/kaggle/working/Retrieval-based-Voice-Conversion-WebUI/logs/taffie", "codenya/rvc-model/pyTorch/taffie", 300), daemon=True)
  t.start()

监控指定目录，每 interval 秒检查一次，有新 checkpoint 则上传到 Kaggle Models。
"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import os, time, glob, shutil, tempfile, hashlib
import kagglehub


def upload_checkpoint_loop(exp_dir: str, model_handle: str, interval: int = 300):
    """
    监控 exp_dir，每 interval 秒上传最新 checkpoint。

    Args:
        exp_dir: RVC 训练日志目录 (logs/exp_name)
        model_handle: Kaggle Models handle (username/model/framework/variation)
        interval: 检查间隔（秒）
    """
    uploaded = set()  # 已上传的文件名集合

    print(f"[checkpoint upload] 开始监控 {exp_dir}")
    print(f"[checkpoint upload] 目标: {model_handle}")
    print(f"[checkpoint upload] 间隔: {interval}s")

    if not os.path.isdir(exp_dir):
        print(f"[checkpoint upload] 目录不存在，等待创建: {exp_dir}")
        while not os.path.isdir(exp_dir):
            time.sleep(30)

    while True:
        try:
            # 查找最新的 G 和 D checkpoint
            g_files = sorted(glob.glob(os.path.join(exp_dir, "G_*.pth")))
            d_files = sorted(glob.glob(os.path.join(exp_dir, "D_*.pth")))
            idx_files = sorted(glob.glob(os.path.join(exp_dir, "*.index")))

            # 取最新的 G+D
            latest = set()
            if g_files:
                latest.add(g_files[-1])
            if d_files:
                latest.add(d_files[-1])

            # 新的还未上传的
            new_files = latest - uploaded
            if new_files:
                with tempfile.TemporaryDirectory() as tmpdir:
                    for f in new_files:
                        shutil.copy2(f, tmpdir)
                    for f in idx_files:
                        shutil.copy2(f, tmpdir)

                    note = f"Checkpoint: {', '.join(os.path.basename(f) for f in new_files)}"
                    print(f"[checkpoint upload] 上传 {note}")

                    try:
                        kagglehub.model_upload(model_handle, tmpdir, version_notes=note)
                        uploaded.update(new_files)
                        print(f"[checkpoint upload] ✓ 上传成功")
                    except Exception as e:
                        print(f"[checkpoint upload] ✗ 上传失败: {e}")
            else:
                print(f"[checkpoint upload] 无新 checkpoint，休眠 {interval}s")

        except Exception as e:
            print(f"[checkpoint upload] 错误: {e}")

        time.sleep(interval)


if __name__ == "__main__":
    # CLI 模式
    import argparse
    parser = argparse.ArgumentParser(description="上传 checkpoint 到 Kaggle")
    parser.add_argument("--exp-dir", required=True, help="训练日志目录")
    parser.add_argument("--handle", default="codenya/rvc-model/pyTorch/taffie", help="Kaggle Model handle")
    parser.add_argument("--interval", type=int, default=300, help="检查间隔(秒)")
    args = parser.parse_args()
    upload_checkpoint_loop(args.exp_dir, args.handle, args.interval)
