from django.db import models


class Product(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Quintly(Product):
    class Meta:
        abstract = True

    quintly_profile_id = models.IntegerField()
