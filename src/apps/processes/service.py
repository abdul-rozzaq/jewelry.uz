from apps.processes.models import Process
from apps.processes.services.base import BaseProcessStrategy
from .services.registry import STRATEGY_MAP


class ProcessService:

    @staticmethod
    def complete_process(process: Process):
        strategy_class = ProcessService.get_strategy_class(process.process_type.type)

        strategy: BaseProcessStrategy = strategy_class(process)

        return strategy.calculate()

    @staticmethod
    def get_strategy_class(_type: tuple) -> BaseProcessStrategy:
        return STRATEGY_MAP.get(_type, STRATEGY_MAP["DEFAULT"])
