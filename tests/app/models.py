from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]


class Company(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="companies"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
