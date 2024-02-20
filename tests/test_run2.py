"""
Unit test file.
"""

import unittest
from pathlib import Path

from docker_run_cmd.run2 import run

HERE = Path(__file__).parent
PROJECT_DIR = HERE.parent
DOCKER_FILE = PROJECT_DIR / "src" / "docker_run_cmd" / "Dockerfile"

assert DOCKER_FILE.exists(), f"Dockerfile not found: {DOCKER_FILE}"


class MainTester(unittest.TestCase):
    """Main tester class."""

    def test_imports(self) -> None:
        """Test command line interface (CLI)."""
        run(dockerfile=DOCKER_FILE, cwd=PROJECT_DIR / "tmp", cmd_list=["--help"])
        print()


if __name__ == "__main__":
    unittest.main()