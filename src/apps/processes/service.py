from apps.processes.models import Process
from apps.processes.services.base import BaseProcessStrategy
from .services.registry import STRATEGY_MAP


class ProcessService:

    @staticmethod
    def complete_process(process: Process):
        process_type = process.process_type.type.upper() if process.process_type else "DEFAULT"
        strategy_class = STRATEGY_MAP.get(process_type)

        if not strategy_class:
            raise Exception(f"Strategy topilmadi: {process_type}")

        strategy: BaseProcessStrategy = strategy_class(process)

        return strategy.calculate()
