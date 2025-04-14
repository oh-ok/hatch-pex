from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from subprocess import run, PIPE

import httpx
import pytest


def test_pex_build(new_project: Path, proc_stdout: str) -> None:
    """
    builds and tests a pex executable
    """

    dist = new_project / "dist" / "pex"
    proc = run([sys.executable, "-m", "hatch", "build", "-t", "pex"])
    proc.check_returncode()

    assert dist.is_dir()
    binaries = list(dist.iterdir())
    assert len(binaries) == 1
    prog = binaries[0]
    assert prog.suffix == ".pex"
    assert zipfile.is_zipfile(prog)

    proc = run([sys.executable, prog], stdout=PIPE, universal_newlines=True)
    assert proc.returncode == 0
    assert proc.stdout == proc_stdout


@pytest.mark.xfail(raises=httpx.HTTPStatusError)
def test_scie_build(new_project: Path, proc_stdout: str) -> None:
    """
    builds and tests a scie of a pex executable
    """

    dist = new_project / "dist" / "pex"

    # modify the pyproject.toml to produce both a scie and a .pex file
    pyproject = new_project / "pyproject.toml"
    assert pyproject.is_file()

    with pyproject.open("a") as f:
        f.write("scie = 'eager'\n")

    proc = run([sys.executable, "-m", "hatch", "build", "-t", "pex"])
    proc.check_returncode()

    assert dist.is_dir()
    artifacts = list(dist.iterdir())
    artifacts.sort()

    expected_suffix = ".exe" if sys.platform in {"win32", "cygwin"} else ""
 
    assert len(artifacts) == 2
    assert artifacts[0].suffix == expected_suffix
    assert artifacts[1].suffix == ".pex"
    assert zipfile.is_zipfile(artifacts[1])

    proc = run([artifacts[0]], stdout=PIPE, universal_newlines=True)
    assert proc.returncode == 0
    assert proc.stdout == proc_stdout

    proc = run([sys.executable, artifacts[1]], stdout=PIPE, universal_newlines=True)
    assert proc.returncode == 0
    assert proc.stdout == proc_stdout


def test_interactive_pex(new_project: Path) -> None:
    """
    builds and tests an interactive pex
    """

    dist = new_project / "dist" / "pex"

    pyproject = new_project / "pyproject.toml"
    assert pyproject.is_file()

    # remove the scripts
    with pyproject.open("r+") as f:
        content = f.read()
        content = re.sub(r"\[project.scripts\][^\[]*", "", content)
        f.seek(0, 0)
        f.truncate(0)
        f.write(content)

    proc = run([sys.executable, "-m", "hatch", "build", "-t", "pex"])
    proc.check_returncode()

    assert dist.is_dir()
    artifacts = list(dist.iterdir())
    artifacts.sort()
    assert len(artifacts) == 1
    prog = artifacts[0]
    assert prog.suffix == ".pex"
    assert zipfile.is_zipfile(prog)

    proc = run([sys.executable, prog, "-V"], stdout=PIPE, universal_newlines=True)
    proc.check_returncode()
    assert "Python" in proc.stdout
