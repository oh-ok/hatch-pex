from __future__ import annotations

import sys
import zipfile
from pathlib import Path
from subprocess import run, PIPE


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
    assert binaries[0].suffix == ".pex"
    assert zipfile.is_zipfile(binaries[0])

    proc = run(binaries, stdout=PIPE, universal_newlines=True)
    assert proc.returncode == 0
    assert proc.stdout == proc_stdout


def test_scie_build(new_project: Path, proc_stdout: str) -> None:
    """
    builds and tests a scie of a pex executable
    """

    dist = new_project / "dist" / "pex"

    # modify the pyproject.toml to produce both a scie and a .pex file
    pyproject = new_project / "pyproject.toml"
    assert pyproject.is_file()

    with pyproject.open("a") as f:
        f.write("""
scie = 'eager'
""")

    proc = run([sys.executable, "-m", "hatch", "build", "-t", "pex"])
    proc.check_returncode()

    assert dist.is_dir()
    artifacts = list(dist.iterdir())
    artifacts.sort()
    assert len(artifacts) == 2
    assert not artifacts[0].suffix
    assert artifacts[1].suffix == ".pex"
    assert zipfile.is_zipfile(artifacts[1])

    for binary in artifacts:
        proc = run([binary], stdout=PIPE, universal_newlines=True)
        assert proc.returncode == 0
        assert proc.stdout == proc_stdout
