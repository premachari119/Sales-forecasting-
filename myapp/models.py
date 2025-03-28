from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    sales = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField()
    profit = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return self.name
