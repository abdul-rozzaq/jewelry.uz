from apps.processes.models.process_type import ProcessTypes
from .default import DefaultStrategy
from .coat import CoatStrategy
from .mixing import MixingStrategy
from .base import BaseProcessStrategy

STRATEGY_MAP: dict[str, BaseProcessStrategy] = {
    "DEFAULT": DefaultStrategy,
    ProcessTypes.MIXING: MixingStrategy,
    ProcessTypes.COAT: CoatStrategy,  # Temirli oltin
}
