# ShopHub - Full E-Commerce Website

A complete user-based e-commerce web application built with **Flask + SQLite + Tailwind CSS**.

## Features

- **User Authentication** — register, login, logout (passwords hashed with Werkzeug)
- **Product Catalog** — browse, search, filter by category, sort by price/name/newest
- **Shopping Cart** — add, update quantity, remove items (per-user, persistent)
- **Checkout & Orders** — place orders, view order history, cancel orders
- **Payment** — Cash on Delivery + Demo card payment (Stripe-ready structure)
- **Reviews & Ratings** — verified buyers can rate and review products (1-5 stars)
- **Admin Panel** — dashboard, manage products, categories, orders, users
- **Responsive Design** — mobile-first, Tailwind CSS, modern UI

## Quick Start (Windows)

Double-click `run.bat` — that's it.

Or manually:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py          # creates DB + sample products + admin user
python app.py           # starts dev server on http://127.0.0.1:5000
```

## Default Admin Login

```
Email:    admin@shophub.com
Password: admin123
```

Change this in `config.py` or via environment variables before going live.

## Project Structure

```
ecommerce/
├── app.py                  # Flask app factory & entry point
├── config.py               # Configuration (DB URL, secret key, etc.)
├── extensions.py           # SQLAlchemy & LoginManager instances
├── models.py               # DB models (User, Product, Category, Cart, Order, Review)
├── forms.py                # WTForms (auth, product, checkout, review)
├── helpers.py              # slugify, file upload, admin_required decorator
├── seed.py                 # Seed DB with sample data
├── requirements.txt
├── run.bat                 # Windows quick-start script
├── blueprints/
│   ├── auth.py             # /auth/register, /auth/login, /auth/logout
│   ├── shop.py             # /, /products, /product/<slug>
│   ├── cart.py             # /cart, /cart/add, /cart/update, /cart/remove
│   ├── orders.py           # /orders/checkout, /orders, /orders/<id>
│   ├── reviews.py          # /reviews/product/<id>
│   └── admin.py            # /admin/* (products, categories, orders, users)
├── templates/
│   ├── base.html           # main layout (header, footer, flash messages)
│   ├── _macros.html        # reusable: product_card, pagination
│   ├── auth/               # login, register, profile
│   ├── shop/               # home, products list, product detail
│   ├── cart/               # cart view
│   ├── orders/             # checkout, orders list, order detail
│   ├── admin/              # dashboard + all CRUD pages
│   └── errors/             # 403, 404, 500
└── static/
    └── uploads/            # uploaded product images
```

## How to Use

### As a Customer
1. Click **Sign Up** in the header — create your account.
2. Browse products by category or use the search bar.
3. Click any product, add to cart, adjust quantity.
4. Open cart, click **Proceed to Checkout**.
5. Fill shipping address, choose payment (COD or Demo Card).
6. Order placed — view it in **My Orders**.
7. After your order is marked Paid/Shipped/Delivered, you can review the product.

### As an Admin
1. Login with `admin@shophub.local` / `admin123`.
2. You'll land on **Admin Dashboard** with stats (products, users, orders, revenue).
3. **Products** — add new products (with image upload), edit, delete.
4. **Categories** — create/delete categories.
5. **Orders** — view all orders, filter by status, update status (pending → paid → shipped → delivered).
6. **Users** — view all customers, promote/demote admin role.

## Configuration

Edit `config.py` or set environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (insecure) | **CHANGE FOR PRODUCTION** |
| `DATABASE_URL` | sqlite:///instance/shop.db | SQLAlchemy DB URL |
| `STORE_NAME` | ShopHub | Brand name shown everywhere |
| `CURRENCY_SYMBOL` | Rs. | e.g. `$`, `€`, `₹` |
| `ADMIN_EMAIL` | admin@shophub.local | Default admin account email |
| `ADMIN_PASSWORD` | admin123 | Default admin password |

## Tech Stack

- **Flask 3** — web framework
- **Flask-SQLAlchemy** — ORM
- **Flask-Login** — session-based authentication
- **Flask-WTF** — forms + CSRF protection
- **Werkzeug** — password hashing
- **SQLite** — zero-config database
- **Tailwind CSS** (via CDN) — utility-first styling
- **Pillow** — image processing (for uploads)

## Production Checklist

Before deploying live:

- [ ] Change `SECRET_KEY` to a long random string
- [ ] Change default admin password
- [ ] Set `debug=False` (production runs via gunicorn/waitress, not `python app.py`)
- [ ] Switch SQLite to PostgreSQL/MySQL for concurrent users
- [ ] Install Tailwind locally (build instead of CDN) for offline + custom themes
- [ ] Integrate real Stripe (replace the mock in `blueprints/orders.py` line ~75)
- [ ] Add HTTPS (reverse proxy via nginx/Caddy)
- [ ] Configure proper email service for order confirmations

## License

MIT — free to use, modify, and sell.
