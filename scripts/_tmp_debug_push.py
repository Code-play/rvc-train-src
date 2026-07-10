import sys; sys.stdout.reconfigure(encoding='utf-8')
import requests, json

token = 'KGAT_160596653880070c2a50a60069a8808d'
nb_path = 'D:/sundries/tools/RVC/Retrieval-based-Voice-Conversion-WebUI-2.2.231006/Retrieval-based-Voice-Conversion-WebUI-2.2.231006/kaggle_kernel/rvc-train.ipynb'

with open(nb_path, encoding='utf-8') as f:
    notebook_json = f.read()

# Try WITHOUT proxy first
for label, proxies in [('WITHOUT proxy', None), ('WITH proxy', {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'})]:
    print(f'\n=== {label} ===')
    payload = {
        'id': 'codenya/rvc-train',
        'title': 'rvc-train',
        'code_file': 'rvc-train.ipynb',
        'language': 'python',
        'kernel_type': 'notebook',
        'is_private': False,
        'enable_gpu': True,
        'enable_internet': True,
        'dataset_sources': ['codenya/taffie'],
        'competition_sources': [],
        'kernel_sources': [],
        'model_sources': []
    }
    try:
        r = requests.post(
            'https://api.kaggle.com/api/v1/kernels/push',
            headers={'X-Kaggle-Token': token},
            files={'blob': ('rvc-train.ipynb', notebook_json, 'application/json')},
            data={'json': json.dumps(payload)},
            proxies=proxies,
            timeout=30
        )
        print(f'Status: {r.status_code}')
        print(f'Body: "{r.text}"[:200]')
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')
