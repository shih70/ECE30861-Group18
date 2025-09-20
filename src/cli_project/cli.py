from pathlib import Path
import sys
import subprocess

def install() -> None:
    """Implements ./run install"""
    py = sys.executable
    cmds = [
        [py, "-m", "pip", "install", "--user", "--upgrade", "pip", "wheel"],
        [py, "-m", "pip", "install", "--user", "-r", "requirements.txt"],
    ]
    for cmd in cmds:
        rc = subprocess.call(cmd)
        if rc != 0:
            sys.stderr.write(f"Command failed: {' '.join(cmd)} (exit {rc})\n")
            sys.exit(rc)
    sys.exit(0)

def test() -> None:
    """Implements ./run test (stub for now)"""
    print("0/0 test cases passed. 0% line coverage achieved.")
    sys.exit(1)

def score(url_file: str) -> None:
    """Implements ./run URL_FILE"""
    path = Path(url_file)
    if not path.exists():
        sys.stderr.write(f"File not found: {path}\n")
        sys.exit(1)

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            print(line)
    sys.exit(0)

if __name__ == "__main__":
    pass
    
