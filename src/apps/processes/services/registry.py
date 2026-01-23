from .default import DefaultStrategy
from .mixing import CoatStrategy
from .base import BaseProcessStrategy

STRATEGY_MAP: dict[str, BaseProcessStrategy] = {
    "DEFAULT": DefaultStrategy,
    "MIXING": CoatStrategy,
    "COAT": CoatStrategy,  # Temirli oltin
}
