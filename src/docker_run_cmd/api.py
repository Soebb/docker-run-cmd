# pylint: disable=too-many-locals,too-many-statements,too-many-arguments,too-many-branches

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from string import Template
from tempfile import TemporaryDirectory

from download import download

HERE = Path(__file__).parent
WIN_DOCKER_EXE = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
DOCKER_COMPOSE_TEMPLATE = HERE / "assets" / "docker-compose-template.yml"


def check_docker_running():
    """Check if Docker service is running."""
    # result = os.system("docker ps")
    # take all stdout and stderr from the current process pipe and silence them
    with TemporaryDirectory() as tempdir:
        dev_null = "DEV" if os.name == "nt" else "/dev/null"
        result = subprocess.run(
            ["docker", "ps", ">", dev_null, "2>&1"],
            check=False,
            shell=True,
            cwd=tempdir,
        ).returncode

    return result == 0


def start_docker_service():
    """Start Docker service depending on the OS."""
    if os.name == "nt":  # Windows
        os.system(f'start "" "{WIN_DOCKER_EXE}"')
    elif os.name == "posix":  # Unix-like
        os.system("open -a Docker")
    else:
        print("Unsupported operating system.")
        sys.exit(1)
    # Wait for Docker to start
    time.sleep(30)  # Adjust this as needed


def start_docker_if_needed() -> bool:
    """Start Docker service if it is not running."""
    if not check_docker_running():
        start_docker_service()
        return True
    return False


def remove_existing_container(container_name):
    """Remove existing Docker container with the given name."""
    result = os.system(f"docker inspect {container_name}")
    if result == 0:  # Container exists
        print(f"Removing existing container named {container_name}...")
        os.system(f"docker rm -f {container_name}")


def docker_run(
    name: str,
    #dockerfile_or_url: str,
    cwd: Path,
    #cmd_list: list[str],
    extra_files: dict[Path, Path] | None = None,
    platform: str | None = None,
    shutdown_after_run: bool = True,
) -> int:
    """Run the Docker container."""
    if not shutil.which("docker-compose"):
        print("docker-compose not found. Please install it.")
        return 1
    if not shutil.which("docker"):
        print("docker not found. Please install it.")
        return 1
    start_docker_if_needed()
    with TemporaryDirectory() as tempdir:
        td = Path(tempdir)
        print(f"Temporary directory: {td}")
        # copy extra files
        if extra_files:
            for src, dst in extra_files.items():
                if not src.exists():
                    print(f"File not found: {src}")
                    continue
                if src.is_dir():
                    shutil.copytree(str(src), str(td / dst))
                else:
                    shutil.copy(str(src), str(td / dst))

        prev_dir = Path.cwd()
        os.chdir(td)
        rtn = 0
        container_name = f"docker-run-cmd-{name}-container"
        try:
            os.system("docker-compose down --rmi all")
            # now docker compose run the app
            print("Building the Docker image...")
            os.system("docker-compose build")
            remove_existing_container(container_name)
            print("Running the Docker container...")
            # Add -d to run in detached mode, if interactive mode is not needed.
            os.system("docker network prune --force")
            rtn = os.system("docker-compose up --no-log-prefix --exit-code-from app")
            os.system("docker network prune --force")
            print("DONE")
        finally:
            os.chdir(prev_dir)
        return rtn
