from django.db import models

from .process_template import ProcessTemplate


def default_name():
    return {"uz": "", "en": "", "tr": ""}


class ProcessTypes(models.TextChoices):
    MELTING = "melting", "Melting"
    COAT = "coat", "Coat"  # Temirli oltin
    MIXING = "mixing", "Mixing"

    POLISHING = "polishing", "Polishing"
    CASTING = "casting", "Casting"
    CUTTING = "cutting", "Cutting"
    ASSEMBLING = "assembling", "Assembling"
    TESTING = "testing", "Testing"
    PACKAGING = "packaging", "Packaging"


class ProcessType(models.Model):
    name = models.JSONField(default=default_name)
    type = models.CharField(max_length=64, choices=ProcessTypes.choices, default=ProcessTypes.MIXING)
    template = models.ForeignKey(ProcessTemplate, null=True, blank=True, on_delete=models.SET_NULL)

    can_cause_loss = models.BooleanField(default=False, help_text="Bu jarayon material yo'qotilishiga olib kelishi mumkinligini ko'rsatadi.")

    def get_name(self, lang="en"):
        """Tilga qarab nomni qaytaradi. Agar mavjud bo‘lmasa, type nomini beradi."""
        return self.name.get(lang) or self.get_type_display()

    def __str__(self):
        return self.get_name("uz")
