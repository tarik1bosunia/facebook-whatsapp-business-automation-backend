from django.db import models
from .product import Product

class ProductFAQ(models.Model):
    product = models.ForeignKey(Product, related_name='faqs', on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    answer = models.TextField()

    class Meta:
        ordering = ['question']

    def __str__(self):
        return f"{self.product.name} - {self.question}"