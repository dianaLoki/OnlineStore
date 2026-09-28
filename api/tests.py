import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Product, CartItem, Order

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user():
    return User.objects.create_user(
        username='testuser',
        password='password123',
        balance=Decimal('1000.00')
    )


@pytest.fixture
def auth_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def product():
    return Product.objects.create(
        name='Test Product',
        price=Decimal('100.00'),
        stock=5
    )


@pytest.mark.django_db
def test_add_to_cart(auth_client, product, test_user):
    response = auth_client.post('/api/cart/', {'product': product.id, 'quantity': 2})

    assert response.status_code == 201
    assert CartItem.objects.filter(user=test_user, product=product, quantity=2).exists()


@pytest.mark.django_db
def test_order_creation_success(auth_client, product, test_user):
    CartItem.objects.create(user=test_user, product=product, quantity=2)

    response = auth_client.post('/api/orders/')

    assert response.status_code == 201

    test_user.refresh_from_db()
    product.refresh_from_db()

    assert test_user.balance == Decimal('800.00')
    assert product.stock == 3
    assert CartItem.objects.filter(user=test_user).count() == 0


@pytest.mark.django_db
def test_order_insufficient_balance(auth_client, product, test_user):
    test_user.balance = Decimal('0.00')
    test_user.save()

    CartItem.objects.create(user=test_user, product=product, quantity=2)
    response = auth_client.post('/api/orders/')

    assert response.status_code == 400
    assert 'Недостаточно средств' in response.data['error']