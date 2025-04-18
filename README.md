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

Hatch's built-in ['binary' build target](https://hatch.pypa.io/latest/plugins/builder/binary/) will generate a self-extracting binary including a Python interpreter and your code using [PyApp](https://github.com/ofek/pyapp). For 'standalone' binaries that include all their dependencies, this is functionally identical to [PEX's `scie` binaries](https://docs.pex-tool.org/scie.html), except that a `scie` PEX does not need to be compiled with cargo for every Python project. Both PEX and PyApp can fetch a Python interpreter at runtime, but only PyApp can fetch dependant wheels at runtime.

Finally, PEX executables can be configured at runtime to manipulate entry-points. PyApp executables have management commands (to purge pip caches, for example), but their entry-point is generally static. This may or may not be desirable for your usecase.

See https://github.com/a-scie/ for more information about how `scie` executables work.

## Configuration

Since all this plugin really does under the hood is call `pex` with your project and entry-points as arguments, it is about as configurable as the `pex` command itself. `pex --help` has a good explanation of all the options here, and [docs.pex-tool.org](https://docs.pex-tool.org) is also very informative.

When you run `hatch build -t pex`, the builder will effectively run the following command for each entry in your `project.scripts` table:

```console
$ pex \
    --project "${PROJECT}" \
    --output-file "${SCRIPT_NAME}.pex" \
    --script "${SCRIPT_NAME}"
    # ... other config args here ...
```

Pretty much all of the below configuration is just passed straight to the `pex` command as arguments.

If you have an empty `project.scripts`, or you set `tool.hatch.build.targets.pex.scripts` to an empty list, then `hatch-pex` will build an interactive PEX.

### Options

```toml
[tool.hatch.build.targets.pex]
scripts = [] # Limit the scripts that get made into PEXes
pex-args = ["--venv"] # Set default arguments to pass to `pex`
scie = false # Set to "eager" or "lazy" to build a scie PEX.
suffix = ".pex" # The suffix of the output file.

# Pass '--scie-only' or '--pex-only' to specify if
# you want one or the other

# You can override your defaults for each PEX,
# add extra arguments, or add additional PEXes by defining tables...
[tool.hatch.build.targets.pex.script.'somescript']
pex-args = []
extra-pex-args = [] 
scie = false
suffix = ".pex"
command = ["--script", "{script}"]
# "{script}" gets replaced with the above name

# If there are no scripts, an interactive PEX is built with the
# project name as the executable name.
# You can also manually configure one.
[tool.hatch.build.targets.pex.interactive]
name = "somename" # the project.name by default
pex-args = []
extra-pex-args = []
scie = false
suffix = ".pex"
# 'command' is not valid here
