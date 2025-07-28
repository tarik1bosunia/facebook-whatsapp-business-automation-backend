import os

for root, dirs, files in os.walk('.'):
    if os.path.basename(root) == 'migrations':
        if '__init__.py' not in files:
            open(os.path.join(root, '__init__.py'), 'w').close()
            print(f"Created __init__.py in {root}")
