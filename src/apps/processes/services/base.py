from rest_framework import exceptions

from apps.processes.models import Process


class BaseProcessStrategy:
    """
    Barcha process turlari uchun umumiy metodlar joyi.
    Masalan, inputlarni tekshirish, umumiy purity hisoblash, va h.k.
    """

    def __init__(self, process: Process):
        self.process = process

    def validate_inputs(self):
        if not self.process.inputs.exists():
            raise exceptions.ValidationError({"detail": "Processda inputlar mavjud emas."})

    def calculate(self):
        """Har bir subclass o‘zining hisoblash metodini yozadi"""
        raise NotImplementedError("Har bir strategiyada calculate() yozilishi kerak.")
