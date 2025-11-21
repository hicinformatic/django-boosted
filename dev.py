#!/usr/bin/env python3
"""Development helper for django-admin-boost."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"

BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
NC = "\033[0m"

if platform.system() == "Windows" and not os.environ.get("ANSICON"):
    BLUE = GREEN = RED = YELLOW = NC = ""


def _resolve_venv_dir() -> Path:
    for name in (".venv", "venv"):
        candidate = PROJECT_ROOT / name
        if candidate.exists():
            return candidate
    return PROJECT_ROOT / ".venv"


VENV_DIR = _resolve_venv_dir()
VENV_BIN = VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin")
PYTHON = VENV_BIN / ("python.exe" if platform.system() == "Windows" else "python")
PIP = VENV_BIN / ("pip.exe" if platform.system() == "Windows" else "pip")


def print_info(message: str) -> None:
    print(f"{BLUE}{message}{NC}")


def print_success(message: str) -> None:
    print(f"{GREEN}{message}{NC}")


def print_error(message: str) -> None:
    print(f"{RED}{message}{NC}", file=sys.stderr)


def print_warning(message: str) -> None:
    print(f"{YELLOW}{message}{NC}")


def run_command(cmd: Sequence[str], check: bool = True, **kwargs) -> bool:
    printable = " ".join(cmd)
    print_info(f"Running: {printable}")
    try:
        subprocess.run(cmd, check=check, cwd=PROJECT_ROOT, **kwargs)
        return True
    except subprocess.CalledProcessError as exc:
        print_error(f"Command exited with code {exc.returncode}")
    except FileNotFoundError:
        print_error(f"Command not found: {cmd[0]}")
    return False


def venv_exists() -> bool:
    return VENV_DIR.exists() and PYTHON.exists()


def ensure_venv_activation(command: str) -> None:
    if command in {"venv", "venv-clean"}:
        return
    if not venv_exists():
        return
    current_python = Path(sys.executable).resolve()
    desired_python = PYTHON.resolve()
    if current_python == desired_python:
        return

    print_info(
        f"Activating virtual environment at {VENV_DIR} before running '{command}'..."
    )
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(VENV_DIR)
    env["PATH"] = f"{VENV_BIN}{os.pathsep}{env.get('PATH', '')}"
    args = [str(desired_python), str(Path(__file__).resolve()), *sys.argv[1:]]
    os.execve(str(desired_python), args, env)


def get_code_directories() -> list[str]:
    targets: list[str] = []
    if SRC_DIR.exists():
        targets.append(str(SRC_DIR.relative_to(PROJECT_ROOT)))
    if TESTS_DIR.exists():
        targets.append(str(TESTS_DIR.relative_to(PROJECT_ROOT)))
    return targets or ["."]


def task_help() -> bool:
    print(f"{BLUE}django-admin-boost — available commands{NC}\n")
    print(f"{GREEN}Environment:{NC}")
    print("  venv            Create the local virtualenv (.venv)")
    print("  install         Install the package (production mode)")
    print("  install-dev     Install editable with dev extras")
    print("  venv-clean      Recreate the virtualenv from scratch\n")

    print(f"{GREEN}Quality:{NC}")
    print("  lint            Ruff + Black (check mode)")
    print("  format          Ruff --fix followed by Black")
    print("  test            Pytest (Django)")
    print("  coverage        Pytest with coverage report\n")

    print(f"{GREEN}Packaging:{NC}")
    print("  build           Clean then build wheel + sdist")
    print("  dist            Alias for build\n")

    print(f"{GREEN}Cleaning & Security:{NC}")
    print("  clean           Remove build/pyc/test artifacts")
    print("  clean-build     Remove only build/dist outputs")
    print("  clean-pyc       Delete __pycache__ and *.pyc")
    print("  clean-test      Remove .pytest_cache, coverage, etc.")
    print("  security        Run Bandit + Safety + pip-audit\n")

    print(f"Usage: {GREEN}python dev.py <command>{NC}")
    return True


def task_venv() -> bool:
    if venv_exists():
        print_warning("Virtual environment already exists.")
        return True

    python_cmd = "python3" if platform.system() != "Windows" else "python"
    print_info("Creating virtual environment...")
    if not run_command([python_cmd, "-m", "venv", str(VENV_DIR)]):
        return False
    print_success(f"Virtual environment created at {VENV_DIR}")
    activation = (
        f"{VENV_DIR}\\Scripts\\activate"
        if platform.system() == "Windows"
        else f"source {VENV_DIR}/bin/activate"
    )
    print_info(f"Activate it with: {activation}")
    return True


def task_install() -> bool:
    if not venv_exists() and not task_venv():
        return False
    if not run_command([str(PIP), "install", "--upgrade", "pip", "setuptools", "wheel"]):
        return False
    if not run_command([str(PIP), "install", "."]):
        return False
    print_success("Installation complete.")
    return True


def task_install_dev() -> bool:
    if not venv_exists() and not task_venv():
        return False
    if not run_command([str(PIP), "install", "--upgrade", "pip", "setuptools", "wheel"]):
        return False
    if not run_command([str(PIP), "install", "-e", ".[dev]"]):
        return False
    print_success("Development installation complete.")
    return True


def _ensure_venv_for_task(task: str) -> bool:
    if not venv_exists():
        print_error(
            f"Virtual environment not found. Run `python dev.py install-dev` before `{task}`."
        )
        return False
    return True


def task_lint() -> bool:
    if not _ensure_venv_for_task("lint"):
        return False
    targets = get_code_directories()
    ruff = VENV_BIN / ("ruff.exe" if platform.system() == "Windows" else "ruff")
    black = VENV_BIN / ("black.exe" if platform.system() == "Windows" else "black")

    success = True
    if not run_command([str(ruff), "check", *targets]):
        success = False
    if not run_command([str(black), "--check", *targets]):
        success = False
    if success:
        print_success("Lint checks passed.")
    return success


def task_format() -> bool:
    if not _ensure_venv_for_task("format"):
        return False
    targets = get_code_directories()
    ruff = VENV_BIN / ("ruff.exe" if platform.system() == "Windows" else "ruff")
    black = VENV_BIN / ("black.exe" if platform.system() == "Windows" else "black")

    success = True
    if not run_command([str(ruff), "check", "--fix", *targets]):
        success = False
    if not run_command([str(black), *targets]):
        success = False
    if success:
        print_success("Formatting complete.")
    return success


def task_test() -> bool:
    if not _ensure_venv_for_task("test"):
        return False
    pytest = VENV_BIN / ("pytest.exe" if platform.system() == "Windows" else "pytest")
    return run_command([str(pytest)])


def task_coverage() -> bool:
    if not _ensure_venv_for_task("coverage"):
        return False
    pytest = VENV_BIN / ("pytest.exe" if platform.system() == "Windows" else "pytest")
    cmd = [str(pytest), "--cov=django_admin_boost", "--cov-report=term-missing"]
    return run_command(cmd)


def task_clean_build() -> bool:
    print_info("Removing build artifacts...")
    for directory in ("build", "dist"):
        path = PROJECT_ROOT / directory
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
            print_info(f"  removed {directory}/")
    for egg_info in PROJECT_ROOT.glob("*.egg-info"):
        shutil.rmtree(egg_info, ignore_errors=True)
        print_info(f"  removed {egg_info}")
    return True


def task_clean_pyc() -> bool:
    print_info("Removing .pyc files and __pycache__ folders...")
    for pycache in PROJECT_ROOT.glob("**/__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)
    for pattern in ("**/*.pyc", "**/*.pyo", "**/*~"):
        for file in PROJECT_ROOT.glob(pattern):
            file.unlink(missing_ok=True)
    return True


def task_clean_test() -> bool:
    print_info("Removing test artifacts...")
    for artifact in (".pytest_cache", ".coverage", "htmlcov"):
        path = PROJECT_ROOT / artifact
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink(missing_ok=True)
    return True


def task_clean() -> bool:
    task_clean_build()
    task_clean_pyc()
    task_clean_test()
    print_success("Workspace clean.")
    return True


def task_security() -> bool:
    if not _ensure_venv_for_task("security"):
        return False

    bandit = VENV_BIN / ("bandit.exe" if platform.system() == "Windows" else "bandit")
    safety = VENV_BIN / ("safety.exe" if platform.system() == "Windows" else "safety")
    pip_audit = VENV_BIN / (
        "pip-audit.exe" if platform.system() == "Windows" else "pip-audit"
    )
    targets = get_code_directories()

    print_info("=" * 70)
    print_info("SECURITY AUDIT")
    print_info("=" * 70)

    results = {"bandit": False, "safety": False, "pip_audit": False}

    print("\n" + "=" * 70)
    print_info("1/3 - Bandit (static analysis)")
    print("=" * 70)
    if run_command(
        [str(bandit), "-r", *targets, "-ll", "-f", "screen", "--skip", "B101"],
        check=False,
    ):
        print_success("✓ Bandit: no critical issues detected.")
        results["bandit"] = True
    else:
        print_warning("⚠ Bandit: review the warnings above.")

    print("\n" + "=" * 70)
    print_info("2/3 - Safety (dependencies)")
    print("=" * 70)
    if run_command([str(safety), "check", "--full-report"], check=False):
        print_success("✓ Safety: no known vulnerabilities.")
        results["safety"] = True
    else:
        print_warning("⚠ Safety: check the report above.")

    print("\n" + "=" * 70)
    print_info("3/3 - pip-audit (PyPI)")
    print("=" * 70)
    if run_command([str(pip_audit)], check=False):
        print_success("✓ pip-audit: no vulnerabilities reported.")
        results["pip_audit"] = True
    else:
        print_warning("⚠ pip-audit: review the findings above.")

    passed = sum(results.values())
    total = len(results)
    print("\n" + "=" * 70)
    print_info("SUMMARY")
    print("=" * 70)
    for tool, ok in results.items():
        status = f"{GREEN}✓ PASS{NC}" if ok else f"{RED}✗ FAIL{NC}"
        print(f"  {tool.upper():15} {status}")

    score = int((passed / total) * 100)
    if score == 100:
        print_success(f"Security score: {score}/100 — excellent.")
    elif score >= 66:
        print_warning(f"Security score: {score}/100 — acceptable.")
    else:
        print_error(f"Security score: {score}/100 — needs attention.")

    return passed == total


def task_build() -> bool:
    if not task_clean():
        return False
    if not task_install_dev():
        return False
    python_exec = PYTHON if venv_exists() else sys.executable
    if not run_command([str(python_exec), "-m", "build"]):
        return False
    print_success("Artifacts available in dist/.")
    return True


def task_dist() -> bool:
    return task_build()


def task_venv_clean() -> bool:
    if venv_exists():
        print_info("Removing existing virtualenv...")
        shutil.rmtree(VENV_DIR, ignore_errors=True)
    return task_venv()


COMMANDS = {
    "help": task_help,
    "venv": task_venv,
    "install": task_install,
    "install-dev": task_install_dev,
    "venv-clean": task_venv_clean,
    "lint": task_lint,
    "format": task_format,
    "test": task_test,
    "coverage": task_coverage,
    "clean": task_clean,
    "clean-build": task_clean_build,
    "clean-pyc": task_clean_pyc,
    "clean-test": task_clean_test,
    "security": task_security,
    "build": task_build,
    "dist": task_dist,
}


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        task_help()
        return 0
    command = args[0]
    if command not in COMMANDS:
        print_error(f"Unknown command: {command}")
        print_info("Use `python dev.py help` to list available commands.")
        return 1

    ensure_venv_activation(command)
    try:
        success = COMMANDS[command]()
        return 0 if success else 1
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user.")
        return 130
    except Exception as exc:
        print_error(f"Unexpected error: {exc}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())


