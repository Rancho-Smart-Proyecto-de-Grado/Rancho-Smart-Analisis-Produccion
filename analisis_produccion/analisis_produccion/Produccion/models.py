from django.db import models


class Produccion(models.Model):
    lote_id = models.IntegerField()
    animal_id = models.IntegerField()
    fecha = models.DateField()
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Registro: Lote {self.lote_id}, Animal {self.animal_id}, Fecha {self.fecha}"

