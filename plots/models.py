# models.py
from django.db import models


class SpiralPlotImage(models.Model):
    image = models.ImageField(upload_to='spiral_plot_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SpiralPlotImage - {self.created_at}"
