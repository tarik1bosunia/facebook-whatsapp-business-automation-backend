from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class ProductCategory(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='product_categories',
        verbose_name="Business Owner"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Category Name",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        ordering = ['name']
        unique_together = ('user', 'name')  # Prevents duplicate category names for the same user

    def __str__(self):
        return self.name