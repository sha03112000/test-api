from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    
    def __str__(self):
        return f"{self.name} ({self.email})"

