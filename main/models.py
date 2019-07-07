from django.db import models


class Town(models.Model):
    region_code = models.IntegerField()
    region_name = models.TextField()
    dept_code = models.TextField()
    distr_code = models.IntegerField()
    code = models.IntegerField()
    name = models.TextField()
    population = models.IntegerField()
    average_age = models.FloatField()

    def __str__(self):
        return self.name[:10]
