from __future__ import annotations

import os
import sys
import subprocess
from typing import Any, Callable, Optional

from hatchling.builders.config import BuilderConfig
from hatchling.builders.plugin.interface import BuilderInterface


class PexBuilderConfig(BuilderConfig):
    CFG_PATH = "tool.hatch.target.pex"

    def parse_config(self) -> list[str]:
        args = []
        fn = args.extend
        fn(self.parse_str("preamble-file"))
        fn(self.parse_list("sources-directory"))
        fn(self.parse_list("package"))
        fn(self.parse_list("module"))
        fn(self.parse_list("project"))
        fn(self.parse_list("dependency-group"))
        fn(self.parse_list("requirement"))
        fn(self.parse_list("constraints"))
        fn(self.parse_list("exclude"))
        fn(self.parse_list("override"))
        fn(self.parse_list("requirements-pex"))
        fn(self.parse_choices("seed", {"none", "args", "verbose"}, True))
        fn(self.parse_str("resolver-version"))
        fn(self.parse_str("pip-version"))
        fn(self.parse_bool("allow-pip-version-fallback"))
        fn(self.parse_list("allow-pip-requirement"))
        fn(self.parse_bool("use-pip-config"))
        fn(self.parse_str("keyring-provider"))
        fn(self.parse_bool("pypi"))
        fn(self.parse_str("find-links"))
        fn(self.parse_str("index-url"))
        fn(self.parse_int("retries"))
        fn(self.parse_int("timeout"))
        fn(self.parse_str("proxy"))
        fn(self.parse_str("cert"))
        fn(self.parse_str("client-cert"))
        fn(self.parse_str("pex-repository"))
        fn(self.parse_str("lock"))
        fn(self.parse_list("path-mapping"))
        fn(self.parse_list("pre-resolved-dist"))
        fn(self.parse_bool("pre"))
        fn(self.parse_bool("wheel"))
        fn(self.parse_bool("build"))
        fn(self.parse_list("only-build"))
        fn(self.parse_bool("prefer-wheel"))
        fn(self.parse_bool("prefer-binary"))
        fn(self.parse_bool("use-pep517"))
        fn(self.parse_bool("build-isolation"))
        fn(self.parse_bool("transitive"))
        fn(self.parse_int("jobs"))
        fn(self.parse_optional_str("pip-log"))
        fn(self.parse_str("pex-path"))
        fn(self.parse_flag("include-tools"))
        fn(self.parse_choices("layout", {"zipapp", "packed", "loose"}))
        fn(self.parse_bool("pre-install-wheels"))
        fn(self.parse_int("max-install-jobs"))
        fn(self.parse_choices("check", {"none", "warn", "error"}))
        fn(self.parse_bool("compress"))
        fn(self.parse_choices("venv", {"prepend", "append"}, True))
        fn(self.parse_bool("venv-copies"))
        fn(self.parse_bool("venv-site-packages-copies"))
        fn(self.parse_bool("venv-system-site-packages"))
        fn(self.parse_flag("non-hermetic-venv-scripts"))
        fn(self.parse_choices("scie", {"lazy", "eager"}))
        fn(self.parse_bool("scie-only"))
        _choices = {"dynamic", "platform-parent-dir", "platform-file-suffix"}
        fn(self.parse_choices("scie-name-style", _choices))
        fn(self.parse_list("scie-busybox"))
        fn(self.parse_bool("scie-busybox-pex-entrypoint-env-passthrough"))
        fn(self.parse_list("scie-platform"))
        fn(self.parse_str("scie-pbs-release"))
        fn(self.parse_str("scie-pypy-release"))
        fn(self.parse_str("python-version"))
        fn(self.parse_bool("scie-pbs-stripped"))
        fn(self.parse_list("scie-hash-alg"))
        fn(self.parse_str("scie-science-binary"))
        fn(self.parse_flag("ignore-errors"))
        fn(self.parse_choices("inherit-path", {"false", "prefer", "fallback"}))
        fn(self.parse_str("runtime-pex-root"))
        fn(self.parse_bool("strip-pex-env"))
        fn(self.parse_list("python"))
        fn(self.parse_str("python-path"))
        fn(self.parse_list("interpreter-constraint"))
        fn(self.parse_list("platform"))
        fn(self.parse_list("complete-platform"))
        fn(self.parse_optional_str("manylinux"))
        fn(self.parse_flag("resolve-local-platforms"))
        fn(self.parse_str("python-shebang"))
        fn(self.parse_bool("sh-boot"))
        fn(self.parse_flag("validate-entry-point"))
        fn(self.parse_list("inject-env"))
        fn(self.parse_list("inject-python-args"))
        fn(self.parse_list("inject-args"))
        if "extra-pex-args" in self.target_config:
            extra_args = self.target_config["extra-pex-args"]
            if not isinstance(extra_args, list):
                raise TypeError("%r: should be a list of strings.")
            if not all(isinstance(i, str) for i in extra_args):
                raise TypeError("%r: should be a list of strings.")
            return args + extra_args
        return args

    def validate_type(self, name, kls) -> Optional[Any]:
        if name not in self.target_config:
            return None
        value = self.target_config[name]
        if not isinstance(value, kls):
            path = "%s.%s" % (self.CFG_PATH, name)
            m = "%r: expected %r, got %r" % (path, kls, value)
            raise TypeError(m)
        return value

    def parse_flag(self, name: str, default=None) -> list[str]:
        value = self.validate_type(name, bool)
        if value is None:
            return []
        if not value:
            if default is None:
                default = []
            return default
        return ["--%s" % name]

    def parse_bool(self, name: str) -> list[str]:
        return self.parse_flag(name, ["--no-%s" % name])

    def parse_optional_str(self, name: str) -> list[str]:
        if name not in self.target_config:
            return []
        value = self.target_config[name]
        if value is False:
            return []
        if value is True:
            return ["--%s" % name]
        if not isinstance(value, str):
            path = "%s.%s" % (self.CFG_PATH, name)
            m = "%r: expected, true, false or a string. Got %r." % (path, value)
            raise TypeError(m)
        return ["--%s" % name, value]

    def parse_str(self, name: str, optional=False) -> list[str]:
        value = self.validate_type(name, str)
        if value is None:
            return []
        return ["--%s" % name, value]

    def parse_int(self, name: str) -> list[str]:
        value = self.validate_type(name, int)
        if value is None:
            return []
        return ["--%s" % name, str(value)]

    def parse_list(self, name: str) -> list[str]:
        value = self.validate_type(name, list)
        if value is None:
            return []
        args = []
        for i, v in enumerate(value):
            if not isinstance(v, str):
                path = "%s.%s" % (self.CFG_PATH, name)
                m = "%r expected list of strings, got %r at index %r" % (path, v, i)
                raise TypeError(m)
            args.append("--%s" % name)
            args.append(v)
        return args

    def parse_choices(
        self, name: str, choices: set[str], choice_optional=False
    ) -> list[str]:
        if name not in self.target_config:
            return []
        value = self.target_config[name]
        if choice_optional and value is True:
            return ["--%s" % name]
        if choice_optional and value is False:
            return []
        if value not in choices:
            path = "%s.%s" % (self.CFG_PATH, name)
            m = "%r must be one of %r, got %r" % (path, choices, value)
            raise ValueError(m)
        return ["--%s" % name, value]

    def scripts(self) -> list[str]:
        known = self.builder.metadata.core.scripts
        if "scripts" not in self.target_config:
            return list(known)
        desired = self.target_config.pop("scripts")
        message = "'scripts' must be a list of strings."
        if not isinstance(desired, list):
            raise TypeError(message)
        for item in desired:
            if not item:
                continue
            if item not in known:
                message = "unknown script %r" % item
                raise ValueError(message)
        return desired


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
        subdir = os.path.join(directory, self.PLUGIN_NAME)
        if not os.path.exists(subdir):
            os.mkdir(subdir)

        entry_points = self.metadata.core.scripts
        scripts = self.config.scripts()
        args = self.config.parse_config() + ["--project", self.root]

        jobs = []
        for script in scripts:
            if not script:
                script = self.metadata.name + "--interactive"
                entry_point = []
            else:
                entry_point = ["--entry-point", entry_points[script]]
            file = os.path.join(subdir, script + ".pex")
            output = ["--output-file", file]
            job = args + entry_point + output
            jobs.append(job)

        for args in jobs:
            self.build_single_pexfile(args)

        return subdir

    def build_single_pexfile(self, args: list[str], *a, **k) -> None:
        subprocess.run([sys.executable, "-m", "pex"] + args, *a, **k)
