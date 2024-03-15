"""
Main entry point.
"""

import argparse
from pathlib import Path

from docker_run_cmd.api import docker_run


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run a command in a Docker container.")
    parser.add_argument("name", help="Name of the Docker container")
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()
    cwd = Path.cwd()
    rtn = docker_run(
        name=args.name,
        #dockerfile_or_url=args.dockerfile_or_url,
        cwd=cwd,
        #cmd_list=args.cmd_list,
    )
    return rtn
