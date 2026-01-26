from apps.processes.models.process_type import ProcessTypes
from .base import BaseProcessStrategy
from .default import DefaultStrategy
from .coat import CoatStrategy
from .mixing import MixingStrategy
from .alloy import AlloyStrategy

STRATEGY_MAP: dict[str, BaseProcessStrategy] = {
    "DEFAULT": DefaultStrategy,
    ProcessTypes.MIXING: MixingStrategy,
    ProcessTypes.COAT: CoatStrategy,  # Temirli oltin
    ProcessTypes.ALLOY: AlloyStrategy
}
