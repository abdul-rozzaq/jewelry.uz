from apps.processes.models.process_type import ProcessTypes
from .base import BaseProcessStrategy
from .default import DefaultStrategy
from .coat_v2 import CoatStrategyV2
from .mixing import MixingStrategy
from .alloy import AlloyStrategy

STRATEGY_MAP: dict[str, BaseProcessStrategy] = {
    "DEFAULT": DefaultStrategy,
    ProcessTypes.MIXING: MixingStrategy,
    ProcessTypes.COAT: CoatStrategyV2,
    ProcessTypes.ALLOY: AlloyStrategy,
}
