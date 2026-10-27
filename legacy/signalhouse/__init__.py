"""Deprecated alias of the SignalHouse Python SDK, which moved to ``signalhouse-sms``.

Install ``signalhouse-sms`` and import ``signalhouse_sms`` instead. Until then, every name and
submodule of ``signalhouse_sms`` is reachable here under its old ``signalhouse`` name.
"""

import pkgutil
import sys
import warnings
from importlib import import_module

import signalhouse_sms
from signalhouse_sms import *  # noqa: F401,F403

__all__ = list(signalhouse_sms.__all__)
__version__ = signalhouse_sms.__version__

warnings.warn(
    "The signalhouse package has moved to signalhouse-sms. Run `pip install signalhouse-sms` "
    "and import signalhouse_sms instead.",
    DeprecationWarning,
    stacklevel=2,
)


def _alias_submodules():
    """Register every ``signalhouse_sms`` submodule under its old ``signalhouse.`` name.

    Old imports such as ``import signalhouse.exceptions`` then resolve to the same module objects,
    so ``isinstance`` and ``except`` checks match classes from either name.
    """
    for info in pkgutil.walk_packages(signalhouse_sms.__path__, "signalhouse_sms."):
        module = import_module(info.name)
        alias = "signalhouse" + info.name[len("signalhouse_sms"):]
        sys.modules[alias] = module
        if alias.count(".") == 1:
            globals()[alias.rpartition(".")[2]] = module


_alias_submodules()
