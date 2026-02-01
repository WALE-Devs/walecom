# WALEcom

A robust e-commerce backend API built with Django 5.2 and Django REST Framework, featuring JWT authentication, product catalog management, order processing, and a flexible CMS for content pages.

## Features

- **JWT Authentication**: Secure token-based authentication using djangorestframework-simplejwt
- **Product Catalog**: Comprehensive product management with categories, tags, variants, and images
- **Order Management**: Shopping cart and order processing system
- **CMS**: Built-in content management system for static pages (About, FAQ, Contact)
- **Slug-based URLs**: SEO-friendly URLs with automatic slug generation
- **Docker Support**: Multi-stage Docker setup for development and production
- **PostgreSQL**: Production-ready database configuration
- **Media Storage**: Support for MinIO/S3 compatible object storage
- **Comprehensive Testing**: pytest-based test suite with good coverage

## Tech Stack

- **Backend**: Django 5.2, Django REST Framework 3.16
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Containerization**: Docker & Docker Compose
- **Object Storage**: MinIO/AWS S3 compatible (django-storages)
- **Testing**: pytest, pytest-django
- **Code Quality**: flake8

## Project Structure

```
src/
├── config/          # Django project configuration (settings, urls, wsgi, asgi)
├── products/        # Product catalog app with categories, tags, variants, images
├── orders/          # Order management and shopping cart
├── content/         # CMS for static content (About, FAQ, Contact pages)
├── utils/           # Shared utilities (slug generation)
└── media/           # User-uploaded images (gitignored)
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- PostgreSQL (for local development)

### Development with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/WALE-Devs/walecom
   cd walecom
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env.dev
   ```

3. **Edit .env.dev with your configuration** (optional for development, defaults work)

4. **Start the development server**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

   The API will be available at `http://localhost:8000`

5. **Load initial data** (optional)
   ```bash
   docker-compose -f docker-compose.dev.yml exec backend python manage.py loaddata products/fixtures/categories.json
   docker-compose -f docker-compose.dev.yml exec backend python manage.py loaddata products/fixtures/tags.json
   docker-compose -f docker-compose.dev.yml exec backend python manage.py loaddata products/fixtures/attributes.json
   docker-compose -f docker-compose.dev.yml exec backend python manage.py loaddata products/fixtures/products.json
   docker-compose -f docker-compose.dev.yml exec backend python manage.py loaddata content/fixtures/content_init.json
   ```

### Local Development

1. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment**
   ```bash
   cp .env.example .env.local
   cp .env.example .env.test

   # Edit .env.local & .env.test with localhost / 127.0.0.1
   ```

4. **Run migrations**
   ```bash
   cd src
   python manage.py migrate
   ```

5. **Load initial data** (optional)
   ```bash
   python manage.py loaddata products/fixtures/categories.json
   python manage.py loaddata products/fixtures/tags.json
   python manage.py loaddata products/fixtures/attributes.json
   python manage.py loaddata products/fixtures/products.json
   python manage.py loaddata content/fixtures/content_init.json
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/token/verify/` - Verify JWT token

### Products
- `GET /api/products/` - List products (supports filtering by `category` and `tags`, search by `name`)
- `GET /api/products/<slug>/` - Retrieve product details
- `POST /api/products/` - Create product (admin only)
- `PUT/PATCH /api/products/<slug>/` - Update product (admin only)
- `DELETE /api/products/<slug>/` - Delete product (admin only)

### Categories
- `GET /api/categories/` - List categories
- `GET /api/categories/<slug>/` - Retrieve category details
- `POST /api/categories/` - Create category (admin only)
- `PUT/PATCH /api/categories/<slug>/` - Update category (admin only)
- `DELETE /api/categories/<slug>/` - Delete category (admin only)

### Product Images
- `GET /api/product-images/` - List product images
- `POST /api/product-images/` - Upload product image (admin only)
- `DELETE /api/product-images/<id>/` - Delete product image (admin only)

### Orders & Cart
- `GET /api/cart/` - Retrieve user's cart
- `POST /api/cart/` - Create cart or add items
- `PUT /api/cart/` - Update cart
- `DELETE /api/cart/` - Clear cart

### Content (CMS)
- `GET /api/content/` - List all content pages
- `GET /api/content/<identifier>/` - Retrieve content page by identifier (e.g., 'about', 'faq', 'contact')
