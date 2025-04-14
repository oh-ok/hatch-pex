from __future__ import annotations

import os
import sys
import subprocess
from typing import Any, Callable, Optional

from hatchling.builders.config import BuilderConfig
from hatchling.builders.plugin.interface import BuilderInterface

from .util import PExecutable, check_type, check_list_type


class PexBuilderConfig(BuilderConfig):
    CFG_PATH = "tool.hatch.target.pex"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__scripts = None
        self.__pex_template = None
        self.__interactive = None

    @property
    def pex_config_template(self):
        if self.__pex_template is not None:
            return self.__pex_template
        config = self.target_config.copy()
        valid = {"command", "scie", "suffix", "pex-args"}
        template = {k: config[k] for k in valid if k in config}
        if "command" not in template:
            template["command"] = ["--script", "{script}"]

        # type check all this..
        check_list_type(template["command"], str)
        if "scie" in template:
            check_type(template["scie"], (bool, str))
        elif "suffix" in template:
            check_type(template["suffix"], str)
        elif "pex-args" in template:
            check_list_type(template["pex-args"], str)

        self.__pex_template = template
        return template

    @property
    def pexes(self) -> dict[str, PExecutable]:
        if self.__scripts is not None:
            return self.__scripts

        # return if theres no scripts
        known = set(self.builder.metadata.core.scripts)
        known.update(check_type(self.target_config.get("script", {}), dict))
        scripts = self.target_config.get("scripts")
        if scripts is None or scripts is True:
            scripts = list(known)

        check_list_type(scripts, str)
        # return an interactive pex if there are no scripts.
        if not scripts:
            pexes = {self.builder.metadata.core.name: self.interactive}
            self.__scripts = pexes
            return pexes

        # check that any script names are valid.
        for script in scripts:
            check_type(script, str)
            if script not in known:
                raise ValueError("Unknown script: {!r}".format(script))

        pexes = {k: PExecutable.from_config(self.pex_config(k)) for k in scripts}

        # add an interactive pex if the config specifies one.
        if "interactive" in self.target_config:
            i_config = check_type(self.target_config["interactive"], dict)
            if i_config.get("name"):
                name = check_type(i_config["name"], str)
            else:
                name = self.builder.metadata.core.name
            pexes[name] = self.interactive

        self.__scripts = pexes
        return pexes

    @property
    def interactive(self) -> Optional[PExecutable]:
        if self.__interactive is not None:
            return self.__interactive

        config = self.pex_config_template.copy()
        config["command"] = []
        config.update(check_type(self.target_config.get("interactive", {}), dict))
        if config["command"]:
            raise ValueError("Command must be empty for an interactive PEX.")
        pex = PExecutable.from_config(config)
        self.__iteractive = pex
        return pex

    def pex_config(self, name, template=None):
        if template is None:
            template = self.pex_config_template
        config = dict(template)
        local_config = self.target_config.get("script", {})
        if "script" in local_config:
            valid = {"command", "scie", "suffix", "pex-args", "extra-pex-args"}
            config.update({k: local_config[k] for k in valid if k in local_config})
        for k in config:
            value = config[k]
            if isinstance(value, str):
                config[k] = value.format(script=name)
            elif isinstance(value, list):
                config[k] = [v.format(script=name) for v in value]
        return config


class PexBuilder(BuilderInterface):
    PLUGIN_NAME = "pex"

    @classmethod
    def get_config_class(cls) -> type[BuilderConfig]:
        return PexBuilderConfig

    @classmethod
    def get_default_versions(cls):
        return ["pexfile"]

    def get_version_api(self) -> dict[str, Callable]:
        return {"pexfile": self.build_pexfile}

    def build_pexfile(self, directory: str, **build_data: Any) -> str:
        config: PexBuilderConfig = self.config

        subdir = os.path.join(directory, self.PLUGIN_NAME)
        if not os.path.exists(subdir):
            os.mkdir(subdir)

        pexes = config.pexes
        args = ["--project", self.root]

        for exe, spec in pexes.items():
            file = os.path.join(subdir, exe + spec.suffix)
            output = ["--output-file", file]
            self.build_executable(spec.as_arguments(prepend=args + output))

        return subdir

    def build_executable(self, args: list[str], *a, **k) -> None:
        return subprocess.run([sys.executable, "-m", "pex"] + args, *a, **k)
