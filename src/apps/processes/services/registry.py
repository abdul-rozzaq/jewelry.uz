from .default import DefaultStrategy
from .coat import CoatStrategy  
from .mixing import MixingStrategy
from .base import BaseProcessStrategy

STRATEGY_MAP: dict[str, BaseProcessStrategy] = {
    "DEFAULT": DefaultStrategy,
    "MIXING": MixingStrategy,
    "COAT": CoatStrategy,  # Temirli oltin
}
