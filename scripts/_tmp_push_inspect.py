import sys; sys.stdout.reconfigure(encoding='utf-8')
import inspect
from kaggle.api.kaggle_api import KernelsApiMixin

# Find the push method
for name, method in inspect.getmembers(KernelsApiMixin):
    if 'push' in name.lower() or 'kernel' in name.lower():
        print(f"\n=== {name} ===")
        print(inspect.getsource(method))
