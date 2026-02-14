from apps.processes.models.process_type import ProcessTypes
from .base import BaseProcessStrategy
from .default import DefaultStrategy
from .coat import CoatStrategyV2
from .mixing import MixingStrategyV2
from .alloy import AlloyStrategy

STRATEGY_MAP: dict[str, BaseProcessStrategy] = {
    "DEFAULT": DefaultStrategy,
    ProcessTypes.MIXING: MixingStrategyV2,
    ProcessTypes.COAT: CoatStrategyV2,
    ProcessTypes.ALLOY: AlloyStrategy,
}
