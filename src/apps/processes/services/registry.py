from .default import DefaultStrategy
from .mixing import MixingStrategy
from .base import BaseProcessStrategy

STRATEGY_MAP: dict[str, BaseProcessStrategy] = {
    "DEFAULT": DefaultStrategy,
    "MIXING": MixingStrategy,
    "COAT": MixingStrategy,  # Temirli oltin
}
