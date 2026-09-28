import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Product, CartItem, Order

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user():
    # Создаем пользователя с балансом 1000 для тестов
    return User.objects.create_user(username='testuser', password='password123', balance=1000.00)


@pytest.fixture
def auth_client(api_client, test_user):
    # Клиент, который уже авторизован под test_user
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def product():
    # Создаем тестовый товар: цена 100, на складе 5 штук
    return Product.objects.create(name='Test Product', price=100.00, stock=5)


@pytest.mark.django_db
def test_add_to_cart(auth_client, product, test_user):
    """Проверяем, что товар успешно добавляется в корзину"""
    response = auth_client.post('/api/cart/', {'product': product.id, 'quantity': 2})

    assert response.status_code == 201  # Код успешного создания
    assert CartItem.objects.filter(user=test_user, product=product, quantity=2).exists()


@pytest.mark.django_db
def test_order_creation_success(auth_client, product, test_user):
    """Проверяем успешный заказ: списание денег, остатков и очистку корзины"""
    # 1. Кладем товар в корзину (2 штуки по 100 = 200)
    CartItem.objects.create(user=test_user, product=product, quantity=2)

    # 2. Делаем заказ
    response = auth_client.post('/api/orders/')

    # 3. Проверяем результаты
    assert response.status_code == 201

    test_user.refresh_from_db()
    product.refresh_from_db()

    # Баланс был 1000, потратили 200, должно остаться 800
    assert test_user.balance == 800.00
    # На складе было 5, купили 2, должно остаться 3
    assert product.stock == 3
    # Корзина должна стать пустой
    assert CartItem.objects.filter(user=test_user).count() == 0


@pytest.mark.django_db
def test_order_insufficient_balance(auth_client, product, test_user):
    """Проверяем, что заказ не пройдет, если нет денег"""
    # Обнуляем баланс пользователя
    test_user.balance = 0
    test_user.save()

    CartItem.objects.create(user=test_user, product=product, quantity=2)
    response = auth_client.post('/api/orders/')

    assert response.status_code == 400
    assert 'Недостаточно средств' in response.data['error']