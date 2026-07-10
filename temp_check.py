# @title 5. 打 PyTorch 兼容补丁（hubert + matplotlib 修复）
import fairseq, torch
# fix: fairseq + PyTorch 2.6+ weights_only 兼容
torch.serialization.add_safe_globals([fairseq.data.dictionary.Dictionary])

# fix: matplotlib tostring_rgb -> tostring_argb
with open('infer/lib/train/utils.py', 'r') as f:
    code = f.read()
code = code.replace('tostring_rgb()', 'tostring_argb()')
code = code.replace('.reshape(fig.canvas.get_width_height()[::-1] + (3,))',
                    '.reshape(fig.canvas.get_width_height()[::-1] + (4,))[:,:,1:]')
with open('infer/lib/train/utils.py', 'w') as f:
    f.write(code)
print('Patches applied successfully')
