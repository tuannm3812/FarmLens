"""Run the reproducible, network-free local showcase checks."""

from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Stop on the first failed check and preserve its exit status."""
    node = shutil.which("node")
    if node is None:
        print("Node.js is needed for frontend checks.", file=sys.stderr)
        return 1
    commands = [
        [sys.executable, "-m", "compileall", "-q", "farmlens", "app.py", "scripts"],
        [sys.executable, "-m", "pytest", "-q"],
        *[[node, "--check", str(path)] for path in sorted((ROOT / "web").glob("*.js"))],
        [node, "--test", *map(str, sorted((ROOT / "tests").glob("web_*.test.cjs")))],
    ]
    for command in commands:
        print("+", " ".join(command), flush=True)
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
