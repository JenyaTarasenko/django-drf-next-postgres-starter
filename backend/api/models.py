from django.db import models


from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)           # Название
    description = models.TextField(blank=True)       # Описание
    image = models.ImageField(upload_to='images/')  # Картинка
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
