import logging
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import CartItem, Order, OrderItem

logger = logging.getLogger(__name__)


@transaction.atomic
def create_order_from_cart(user):
    cart_items = CartItem.objects.filter(user=user).select_related('product')

    if not cart_items.exists():
        raise ValidationError("Корзина пуста")

    # 1. Считаем сумму и проверяем остатки на складе
    total_amount = 0
    for item in cart_items:
        if item.product.stock < item.quantity:
            raise ValidationError(
                f"Недостаточно товара '{item.product.name}' на складе. Доступно: {item.product.stock}")
        total_amount += item.product.price * item.quantity

    # 2. Проверяем баланс
    if user.balance < total_amount:
        raise ValidationError("Недостаточно средств на балансе")

    # 3. Списание баланса и создание заказа
    user.balance -= total_amount
    user.save()

    order = Order.objects.create(user=user, total_amount=total_amount)

    # 4. Списание количества со склада и сохранение товаров в заказе
    order_items = []
    for item in cart_items:
        item.product.stock -= item.quantity
        item.product.save()

        order_items.append(
            OrderItem(order=order, product=item.product, price=item.product.price, quantity=item.quantity)
        )

    OrderItem.objects.bulk_create(order_items)

    # 5. Очистка корзины
    cart_items.delete()

    # 6. Логирование/уведомление
    logger.info(f"Успешный заказ #{order.id} от пользователя {user.username} на сумму {total_amount}")

    return order