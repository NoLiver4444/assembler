#!/usr/bin/env python3
"""
Очистка временных файлов
"""

import os
import glob

files_to_clean = [
    '*.bin',
    '*.tmp',
    '__pycache__',
    'example_programs/*.bin'
]

for pattern in files_to_clean:
    for file in glob.glob(pattern):
        if os.path.isdir(file):
            os.system(f'rmdir /S /Q "{file}"' if os.name == 'nt' else f'rm -rf "{file}"')
        else:
            os.remove(file)
            print(f"Удалён: {file}")