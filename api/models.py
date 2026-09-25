from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # Личный баланс (можно пополнять)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


class Product(models.Model):
    # Требования к товару: Название, Описание, Цена, Кол-во на складе
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product')  # Чтобы один товар не дублировался разными строками


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Фиксируем цену на момент покупки
    quantity = models.PositiveIntegerField()