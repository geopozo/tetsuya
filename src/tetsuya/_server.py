from pathlib import Path

import platformdirs

runtime = platformdirs.user_runtime_dir("tetsuya", "pikulgroup")


def uds_path() -> Path:
    base = Path(runtime)
    p = base / "tetsuya.sock"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p
