"""
Common test fixtures and utilities for all test suites.

This module provides reusable pytest fixtures for creating test data
across content, orders, and products apps.
"""
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from products.models import Product, ProductVariant, Category
from orders.models import Cart, CartProduct

import os
import shutil
import tempfile
from django.conf import settings
from django.test import override_settings

User = get_user_model()


@pytest.fixture(scope='session', autouse=True)
def media_root_tmp(request):
    """
    Overrides MEDIA_ROOT with a temporary directory for the duration of the test session.
    This prevents tests from polluting the real media folder.
    """
    tmp_dir = tempfile.mkdtemp()
    
    with override_settings(MEDIA_ROOT=tmp_dir):
        yield tmp_dir
        
    # Cleanup after session
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


# ============================================================================
# API Client Fixtures
# ============================================================================

@pytest.fixture
def api_client():
    """Returns an unauthenticated API client."""
    return APIClient()


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def user(db):
    """Creates a standard test user."""
    return User.objects.create_user(
        email='test@example.com',
        password='password123'
    )


@pytest.fixture
def admin_user(db):
    """Creates an admin/superuser for testing admin-only endpoints."""
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def normal_user(db):
    """Creates a normal (non-admin) user."""
    return User.objects.create_user(
        email='user@example.com',
        password='userpass123'
    )


# ============================================================================
# Authenticated Client Fixtures
# ============================================================================

@pytest.fixture
def authenticated_client(api_client, user):
    """Returns an API client authenticated as a standard user."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Returns an API client authenticated as an admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client


# ============================================================================
# Product Model Fixtures
# ============================================================================

@pytest.fixture
def category(db):
    """Creates a test category."""
    return Category.objects.create(
        name='Test Category',
        slug='test-category',
        description='A test category'
    )


@pytest.fixture
def product(category):
    """
    Creates a test product with a category.
    Note: A default variant is automatically created by the signal.
    """
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        base_sku='TEST-PROD',
        category=category,
        default_price=Decimal('100.00'),
        default_stock=10,
        description='A test product'
    )


@pytest.fixture
def variant(product):
    """
    Returns the default variant for a product (created by signal).
    Updates stock to 10 for testing purposes.
    """
    v = product.variants.first()
    if v:
        v.stock = 10
        v.price = Decimal('100.00')
        v.save()
    else:
        # Fallback if signal didn't run
        v = ProductVariant.objects.create(
            product=product,
            name='Default',
            sku=f'{product.base_sku}-DEF',
            price=Decimal('100.00'),
            stock=10
        )
    return v


# ============================================================================
# Cart/Order Fixtures
# ============================================================================

@pytest.fixture
def cart(user):
    """Creates an empty cart for a user."""
    return Cart.objects.create(user=user)


@pytest.fixture
def cart_with_item(cart, variant):
    """Creates a cart with one item."""
    CartProduct.objects.create(
        cart=cart,
        product_variant=variant,
        quantity=2
    )
    return cart
