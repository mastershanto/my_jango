from django.db import models


class AppUser(models.Model):
    """User model with type hints."""
    name = models.CharField(max_length=100)  
    email = models.EmailField(unique=True)  
    phone = models.CharField(max_length=15, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self) -> str:
        return self.name  

    def get_full_info(self) -> str:
        """Return formatted user info with type hints."""
        return f"{self.name} ({self.email})" 

    class Meta:
        ordering = ['-created_at']
        verbose_name = "User"
        verbose_name_plural = "Users"


class Product(models.Model):
    """Product model with type hints."""
    title = models.CharField(max_length=200)  
    description = models.TextField(blank=True, null=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    stock = models.PositiveIntegerField(default=0)  
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self) -> str:
        return self.title  

    def is_in_stock(self) -> bool:
        """Check if product is available with type hints."""
        return self.stock > 0  

    def get_price_display(self) -> str:
        """Return formatted price with type hints."""
        return f"${self.price:.2f}"  

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product"
        verbose_name_plural = "Products"
