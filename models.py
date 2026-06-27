from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship(
        "CartItem", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    orders = db.relationship("Order", backref="user", lazy=True)
    reviews = db.relationship("Review", backref="user", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def cart_total(self):
        return sum(item.subtotal for item in self.cart_items)

    @property
    def cart_count(self):
        return sum(item.quantity for item in self.cart_items)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)

    products = db.relationship("Product", backref="category", lazy=True)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship(
        "Review", backref="product", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def average_rating(self):
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    @property
    def review_count(self):
        return len(self.reviews)

    @property
    def in_stock(self):
        return self.stock > 0


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")

    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),
    )

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)
    # statuses: pending, paid, shipped, delivered, cancelled
    payment_method = db.Column(db.String(40), default="cod")
    payment_ref = db.Column(db.String(80))

    shipping_name = db.Column(db.String(120), nullable=False)
    shipping_phone = db.Column(db.String(20), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    shipping_city = db.Column(db.String(80), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        "OrderItem", backref="order", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def item_count(self):
        return sum(i.quantity for i in self.items)


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship("Product")

    @property
    def subtotal(self):
        return self.price * self.quantity


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", name="uq_review_user_product"),
    )
