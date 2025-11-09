from pathlib import Path

def root_dir(start_path: Path=None):
    if start_path is None:
        start_path = Path.cwd()
    current = start_path.resolve()
    while current != current.parent:
        if (current / 'pyproject.toml').exists():
            return current
        current = current.parent
    raise FileNotFoundError("No pyproject.toml found")