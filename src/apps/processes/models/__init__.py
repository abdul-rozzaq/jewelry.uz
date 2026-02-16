from .base import BaseProcess, ProcessStatus
from .coat_process import CoatProcess
from .gold_downgrade_process import GoldDowngradeProcess

def default_name():
    return {}

__all__ = [
    "BaseProcess",
    "CoatProcess",
    "GoldDowngradeProcess",
    "ProcessStatus",
    "default_name",
]
