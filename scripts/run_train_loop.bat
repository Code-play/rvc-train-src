@echo off
setlocal enabledelayedexpansion
set COUNT=1
cd /d "D:\sundries\tools\RVC\Retrieval-based-Voice-Conversion-WebUI-2.2.231006\Retrieval-based-Voice-Conversion-WebUI-2.2.231006"

:LOOP
echo [%DATE% %TIME%] ===== 训练尝试 #%COUNT% ===== >> logs\taffie\train_loop.log
"C:\Users\18777\anaconda3\envs\rvc\python.exe" infer/modules/train/train.py -e "taffie" -sr 40k -f0 1 -bs 4 -g 0 -te 100 -se 5 -pg "assets/pretrained_v2/f0G40k.pth" -pd "assets/pretrained_v2/f0D40k.pth" -l 1 -c 0 -sw 0 -v v2 >> logs\taffie\train_loop.log 2>&1
echo [%DATE% %TIME%] ===== 退出码: %ERRORLEVEL% ===== >> logs\taffie\train_loop.log

if %COUNT% lss 100 goto LOOP
