# hatch-pex 🍳

This plugin adds a [PEX executable](https://github.com/pex-tool/pex) build target for [Hatch](https://github.com/pypa/hatch).


## Quickstart

To make the `'pex'` target available in Hatch, you just need to add `hatch-pex` as a dependency of the `pex` build target.

```toml
[tool.hatch.build.targets.pex]
dependencies = ["hatch-pex"]
```

From there, you can build with Hatch!

```console
$ hatch build -t pex
$ ls dist/pex
myapp.pex
```

To add a `scie` build, just set the scie type

```toml
[tool.hatch.build.targets.pex]
dependencies = ["hatch-pex"]
scie = "eager"
```

```console
$ hatch build -t pex
$ ls dist/pex
myapp.pex   myapp
```

## Comparison to PyApp

Hatch's built-in ['binary' build target](https://hatch.pypa.io/latest/plugins/builder/binary/) will generate a self-extracting binary including a Python interpreter and your code using [PyApp](https://github.com/ofek/pyapp). This is functionally identical to [PEX's `scie` binaries](https://docs.pex-tool.org/scie.html), except that a `scie` PEX does not need to be compiled for every Python project.

Instead, the `scie` binary is just a "dumb" pre-built binary that the PEX zipapp gets appended to (with some metadata to tell the binary how to run it). This works because executables can have arbitrary data appended to them, and a zip can have arbitrary data before it's header, and both are still valid.

## Configuration

Since all this plugin really does under the hood is call `pex` with your project and entry-points as arguments, it is about as configurable as the `pex` command itself. `pex --help` has a good explanation of all the options here, and [docs.pex-tool.org](https://docs.pex-tool.org) is also very informative.

When you run `hatch build -t pex`, the builder will effectively run the following command for each entry in your `project.scripts` table:

```console
$ pex \
    --project "${PROJECT}" \
    --output-file "${SCRIPT_NAME}.pex" \
    --entry-point "${SCRIPT_ENTRY_POINT}"
    # ... other config args here ...
```

Pretty much all of the below configuration is just passed straight to the `pex` command as arguments.

If you have an empty `project.scripts`, or you set `tool.hatch.build.targets.pex.scripts` to an empty list, then `hatch-pex` will build an interactive PEX.

### Options

```toml
[tool.hatch.build.targets.pex]
project = [] # NOTE: the current project is always added
scripts = [] # NOTE: use this to limit the entry points that get built
preamble-file = "path"
sources-directory = []
package = []
module = []
dependency-group = []
requirement = []
constraints = []
exclude = []
override = []
requirements-pex = []
seed = true | "none" | "args" | "verbose"
resolver-version = "pip-legacy-resolver" | "pip-2020-resolver"
pip-version = "version"
allow-pip-version-fallback = true | false
allow-pip-requirement = []
use-pip-config = true | false
keyring-provider = "provider"
pypi = true | false
find-links = "url or path"
index-url = "url or path"
retries = 0
timeout = 0
proxy = "url"
cert = "path"
client-cert = "path"
pex-repository = "path"
lock = "path"
path-mapping = []
pre-resolved-dist = []
pre = true | false
wheel = true | false
build = true | false
only-build = []
prefer-wheel = true | false
prefer-binary = true | false
use-pep517 = true | false
build-isolation = true | false
transitive = true | false
jobs = 0
pip-log = true | "path"
pex-path = "PEXPATH"
include-tools = true | false
layout = "zipapp" | "packed" | "loose"
pre-install-wheels = true | false
max-install-jobs = 0
check = "none" | "warn" | "error"
compress = true | false
venv = true | "prepend" | "append"
venv-copies = true | false
venv-site-packages-copies = true | false
venv-system-site-packages = true | false
non-hermetic-venv-scripts = true | false
scie = "lazy" | "eager"
scie-only = true | false
scie-name-style = "dynamic" | "platform-parent-dir" | "platform-file-suffix"
scie-busybox = []
scie-busybox-pex-entrypoint-env-passthrough = true | false
scie-platform = []
scie-pbs-release = "id"
scie-pypy-release = "id"
python-version = "ver"
scie-pbs-stripped = true | false
scie-hash-alg = []
scie-science-binary = "path or url"
ignore-errors = true | false
inherit-path = "false" | "prefer" | "fallback"
runtime-pex-root = "path"
strip-pex-env = true | false
python = []
python-path = "PYTHONPATH"
interpreter-constraint = []
platform = []
complete-platform = []
manylinux = true | ""
resolve-local-platforms = true | false
python-shebang = ""
sh-boot = true | false
validate-entry-point = true | false
inject-env = []
inject-python-args = []
inject-args = []

# any extra arguments that are not accounted
# for here can be passed here
extra-pex-args = []
```

## License

`hatch-pex` is distributed under the terms of the [MIT](/LICENSE) license.
