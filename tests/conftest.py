from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import pytest

TEST_PYPROJECT = """
[project]
name = "test-app"
version = "0.1.0"

[project.scripts]
hello_world = "test_app:hello_world"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.pex]
dependencies = ["hatch-pex @ {}"]
"""

TEST_INIT_PY = """#!/usr/bin/env python3
import sys
def hello_world():
    sys.stdout.write({!r})

"""


@pytest.fixture(autouse=True)
def clear_env(monkeypatch: pytest.MonkeyPatch):
    # If we're running these tests in a hatch env,
    # hatch will try to load the env from within
    # the test project, which obviously doesn't exist.
    with monkeypatch.context() as m:
        m.delenv("HATCH_ENV_ACTIVE", raising=False)
        yield


@pytest.fixture(scope="session")
def tmp_dir():
    with tempfile.TemporaryDirectory() as dir:
        yield Path(dir).resolve()


@pytest.fixture(scope="session")
def plugin_dir():
    with tempfile.TemporaryDirectory() as dir:
        dir = Path(dir, "hatch-pex")
        shutil.copytree(Path.cwd(), dir, ignore=shutil.ignore_patterns(".*"))
        yield dir.resolve()


@pytest.fixture
def proc_stdout():
    return "hello_world!\n"


@pytest.fixture
def new_project(plugin_dir: Path, tmp_path: Path, proc_stdout: str) -> None:
    cwd = Path.cwd()
    project_dir = tmp_path / "test-app"
    project_dir.mkdir()

    pyproject = project_dir / "pyproject.toml"
    pyproject.write_text(TEST_PYPROJECT.format(plugin_dir.as_uri()))

    source_code = project_dir / "test_app"
    source_code.mkdir()

    init_py = source_code / "__init__.py"
    init_py.write_text(TEST_INIT_PY.format(proc_stdout))

    os.chdir(project_dir)
    try:
        yield project_dir
    finally:
        os.chdir(cwd)
