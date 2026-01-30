import pytest
from products.models import Category, Product


@pytest.fixture()#scope='function')
def products_fixture(db):
    """
    Fixture que carga automáticamente los datos de productos
    """
    from django.core.management import call_command
    call_command('loaddata', 'categories', 'tags', 'attributes', 'products', 'variants', 'images', verbosity=0)


def test_load_fixture_automatico(products_fixture):
    """
    Test que recibe los datos cargados automáticamente via fixture
    SIN necesidad de call_command manual
    """
    # Los datos ya están cargados por el fixture products_fixture

    # Verificar que los datos se cargaron
    categories = Category.objects.all()
    products = Product.objects.all()

    print(categories)
    print(products)

    # Assertions básicas
    assert len(categories) > 0, "No se cargaron categorías del fixture"
    assert len(products) > 0, "No se cargaron productos del fixture"