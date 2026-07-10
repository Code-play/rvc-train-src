# TMP: 用 kagglehub 上传音频数据集到 Kaggle | 依赖: kagglehub, 音频文件 | 保留: 否
"""
用法:
  python scripts/upload_audio_to_kaggle.py --dir opt/ --handle codenya/taffie

说明:
  将本地音频目录上传/更新为 Kaggle Dataset。
  支持首次创建和后续版本更新。
  音频文件建议用 FLAC/WAV 格式，不推荐 mp3。
"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import os, argparse, glob, tempfile, shutil
import kagglehub


def upload_dataset(local_audio_dir: str, handle: str, title: str = None, notes: str = ""):
    """用 kagglehub 上传音频数据集"""
    notes = notes or f"RVC training data from {local_audio_dir}"

    # 验证音频文件
    exts = ('.wav', '.flac', '.mp3', '.m4a', '.ogg')
    audio_files = [f for f in os.listdir(local_audio_dir)
                   if f.lower().endswith(exts)]
    if not audio_files:
        print(f"错误: {local_audio_dir} 中没有音频文件 ({', '.join(exts)})")
        sys.exit(1)

    print(f"找到 {len(audio_files)} 个音频文件")
    total_sz = sum(os.path.getsize(os.path.join(local_audio_dir, f)) for f in audio_files)
    print(f"总大小: {total_sz / 1024 / 1024:.1f} MB")

    # 上传
    print(f"\n上传到 {handle}...")
    try:
        result = kagglehub.dataset_upload(handle, local_audio_dir)
        print(f"✓ {'更新' if 'version' in str(result) else '创建'}成功: {handle}")
        print(f"  上传了 {len(audio_files)} 个音频文件")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("数据集已存在，尝试创建新版本...")
            result = kagglehub.dataset_upload(
                handle, local_audio_dir,
                version_notes=notes
            )
            print(f"✓ 新版本上传成功: {handle}")
        else:
            print(f"✗ 上传失败: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="上传音频到 Kaggle Dataset")
    parser.add_argument("--dir", required=True, help="音频文件目录")
    parser.add_argument("--handle", default="codenya/taffie", help="Kaggle Dataset handle")
    parser.add_argument("--title", help="Dataset 标题（仅首次创建时使用）")
    parser.add_argument("--notes", default="", help="版本更新说明")
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"错误: 目录不存在: {args.dir}")
        sys.exit(1)

    upload_dataset(args.dir, args.handle, args.title, args.notes)


if __name__ == "__main__":
    main()
