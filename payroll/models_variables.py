from django.db import models

class PayrollVariable(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la variable")
    value = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Valeur")
    unit = models.CharField(max_length=20, blank=True, verbose_name="Unité", help_text="% ou €")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Variable de paie"
        verbose_name_plural = "Variables de paie"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.value}{self.unit})"

class PayrollContribution(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la cotisation")
    rate = models.DecimalField(max_digits=6, decimal_places=4, verbose_name="Taux (%)")
    ceiling = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Plafond (€)")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cotisation sociale"
        verbose_name_plural = "Cotisations sociales"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.rate}%)"
