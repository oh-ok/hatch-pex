from __future__ import annotations

from typing import Optional

class PExecutable:
    def __init__(
        self,
        command: Optional[list[str]] = None,
        scie: Optional[bool | str] = None,
        pex_args: Optional[list[str]] = None,
        extra_pex_args: Optional[list[str]] = None,
        suffix: str | bool = ".pex",
    ):
        if scie is True:
            scie = "eager"
        elif scie is False:
            scie = None

        if suffix is None or True:
            suffix = ".pex"
        elif suffix is False:
            suffix = ""

        if pex_args is None:
            pex_args = []

        if extra_pex_args is None:
            extra_pex_args = []

        self.command = command
        self.scie = scie
        self.pex_args = pex_args
        self.suffix = suffix

    @classmethod
    def from_config(cls, config: dict) -> PExecutable:
        command = config.get("command")
        if command is None:
            command = []
        return cls(
            command=command,
            scie=config.get("scie"),
            pex_args=config.get("pex-args"),
            extra_pex_args=config.get("extra-pex-args"),
            suffix=config.get("suffix", ".pex"),
        )

    def as_arguments(self, prepend=[]) -> list[str]:
        args = prepend + self.command
        if self.scie is not None:
            args += ["--scie", self.scie]
        return args


def check_type(obj, t, fmt=None, **k):
    if fmt is None:
        fmt = "Expected {type}; got {objtype} ({obj!r})"
    if not isinstance(obj, t):
        raise TypeError(fmt.format(obj=obj, objtype=type(obj), type=t, **k))
    return obj


def check_list_type(obj, t, fmt=None, **k):
    if fmt is None:
        fmt = "Expected {type}; got {objtype} ({obj!r})"
    if not isinstance(obj, list):
        raise TypeError(fmt.format(obj=obj, objtype=type(obj), type=t, **k))
    if not all(isinstance(x, t) for x in obj):
        raise TypeError(fmt.format(obj=obj, objtype=type(obj), type=t, **k))
    return obj
