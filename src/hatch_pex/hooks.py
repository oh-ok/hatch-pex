from hatchling.plugin import hookimpl

from .builder import PexBuilder


@hookimpl
def hatch_register_builder():
    return PexBuilder
