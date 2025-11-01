import os

def ensure_dirs(*paths):
    """Ensure directories for given file paths exist"""
    for path in paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
