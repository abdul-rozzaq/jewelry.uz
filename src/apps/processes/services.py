from django.db import transaction
from rest_framework import exceptions

from apps.products.models import Product

from .models import Process, ProcessInput, ProcessOutput, ProcessStatus


class ProcessService:

    @staticmethod
    def complete_process(process: Process):
        with transaction.atomic():

            total_pure_gold = 0
            total_mass = 0

            for inp in process.inputs.all():
                inp: ProcessInput
                product = inp.product

                if inp.product.quantity < inp.quantity:
                    raise exceptions.ValidationError({"detail": f"{product} mahsuloti yetarli emas."})

                pure_gold = inp.quantity * (product.material.purity / 100)
                total_pure_gold += pure_gold
                total_mass += inp.quantity

                product.quantity -= inp.quantity
                product.save(update_fields=["quantity"])

            for outp in process.outputs.all():
                outp: ProcessOutput

                product, _ = Product.objects.get_or_create(organization=process.organization, material=outp.material, defaults={"quantity": 0})

                new_mass = product.quantity + outp.quantity

                output_purity = (total_pure_gold / new_mass) * 100 if new_mass else 0

                product.quantity = new_mass
                product.material.purity = output_purity
                product.material.save(update_fields=["purity"])
                product.save(update_fields=["quantity"])

            process.status = ProcessStatus.COMPLETED
            process.save(update_fields=["status"])

        return process

    @staticmethod
    def check_process_completion(process: Process):
        for i in process.inputs.all():
            if i.quantity <= 0:
                raise exceptions.ValidationError({"detail": "Kiritilgan mahsulotlarning miqdori musbat bo'lishi kerak."})

        # total_input_mass = sum(inp.quantity for inp in process.inputs.all())
        # total_output_mass = sum(outp.quantity for outp in process.outputs.all())

        # if total_input_mass != total_output_mass:
        #     raise exceptions.ValidationError({"detail": "Kiritilgan va chiqarilgan mahsulotlarning umumiy massasi mos kelmaydi."})
