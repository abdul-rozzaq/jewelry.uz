from django.db import models

from apps.materials.models import Material


class ProcessItemRole(models.TextChoices):
    # === INPUT ROLES ===
    BASE_GOLD = "base_gold"  # Asosiy oltin (purity hisobiga kiradi)
    ADDITIVE_GOLD = "additive_gold"  # Qaynoq / qo‘shimcha oltin
    METAL = "metal"  # Temir, mis va h.k. (faqat massa)
    AUXILIARY = "auxiliary"  # Kimyoviy, flux, yo‘qoladi

    # === OUTPUT ROLES ===
    COMPOSITE = "composite"  # Yakuniy mahsulot (temirli oltin, alloy)
    PURE_GOLD = "pure_gold"  # Toza oltin chiqishi
    SCRAP = "scrap"  # Hurda
    LOSS = "loss"  # Hisobiy yo‘qotish (real product emas)


class ProcessTemplate(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return f"Template(name={self.name})"


class ProcessTemplateInputItem(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    template = models.ForeignKey(ProcessTemplate, on_delete=models.CASCADE, related_name="template_inputs")
    role = models.CharField(choices=ProcessItemRole.choices, max_length=127)

    use_all_material = models.BooleanField(default=False)

    def __str__(self):
        return f"InputItem(material={self.material}, use_all_material={self.use_all_material})"


class ProcessTemplateOutputItem(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    template = models.ForeignKey(ProcessTemplate, on_delete=models.CASCADE, related_name="template_outputs")
    role = models.CharField(choices=ProcessItemRole.choices, max_length=127)

    use_all_material = models.BooleanField(default=False)

    def __str__(self):
        return f"OutputItem(material={self.material}, use_all_material={self.use_all_material})"
