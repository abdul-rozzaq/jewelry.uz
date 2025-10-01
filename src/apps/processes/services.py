from django.db import transaction
from rest_framework import exceptions

from apps.products.models import Product

from .models import Process, ProcessInput, ProcessOutput, ProcessStatus


class ProcessService:

    @staticmethod
    def complete_process(process: Process):
        with transaction.atomic():
            for inp in process.inputs.all():
                inp: ProcessInput
                product = inp.product

                if inp.product.quantity < inp.quantity:
                    raise exceptions.ValidationError({"detail": "Mahsulot yetarli emas"})

                product.quantity -= inp.quantity
                product.save(update_fields=["quantity"])

            for outp in process.outputs.all():
                outp: ProcessOutput

                product, created = Product.objects.get_or_create(organization=process.organization, material=outp.material, defaults={"quantity": 0})
                product.quantity += outp.quantity

                product.save(update_fields=["quantity"])

            process.status = ProcessStatus.COMPLETED
            process.save(update_fields=["status"])

        return process
