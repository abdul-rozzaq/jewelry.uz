from django.db import transaction
from rest_framework import exceptions

from apps.inventory.models import OrganizationInventory

from .models import Process, ProcessInput, ProcessOutput, ProcessStatus


class ProcessService:

    @staticmethod
    def complete_process(process: Process):
        with transaction.atomic():
            for inp in process.inputs.all():
                inp: ProcessInput
                inventory = inp.inventory

                if inp.inventory.quantity < inp.quantity:
                    raise exceptions.ValidationError({"detail": "Mahsulot yetarli emas"})

                inventory.quantity -= inp.quantity
                inventory.save(update_fields=["quantity"])

            for outp in process.outputs.all():
                outp: ProcessOutput

                inventory, created = OrganizationInventory.objects.get_or_create(organization=process.organization, material=outp.material, defaults={"quantity": 0})
                inventory.quantity += outp.quantity

                inventory.save(update_fields=["quantity"])

            process.status = ProcessStatus.COMPLETED
            process.save(update_fields=["status"])

        return process
