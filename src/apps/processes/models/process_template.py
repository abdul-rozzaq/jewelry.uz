from django.db import models

from apps.materials.models import Material


class ProcessTemplateItem(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    use_all_material = models.BooleanField(default=False)

    class Meta:
        unique_together = ("material", "use_all_material")

    def __str__(self):
        return f"Item(material={self.material}, use_all_material={self.use_all_material})"


class ProcessTemplate(models.Model):
    name = models.CharField(max_length=256)

    inputs = models.ManyToManyField(ProcessTemplateItem, related_name="template_inputs")
    outputs = models.ManyToManyField(ProcessTemplateItem, related_name="template_outputs")

    def __str__(self):
        return f"Template(name={self.name})"
