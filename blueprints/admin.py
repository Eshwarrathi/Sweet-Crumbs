from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy import func

from extensions import db
from models import Product, Category, Order, User, OrderItem
from forms import ProductForm, CategoryForm, UpdateStatusForm
from helpers import admin_required, save_upload, unique_slug

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.before_request
@login_required
@admin_required
def require_admin():
    pass


@bp.route("/")
def dashboard():
    stats = {
        "products": Product.query.count(),
        "users": User.query.count(),
        "orders": Order.query.count(),
        "revenue": db.session.query(func.coalesce(func.sum(Order.total), 0))
        .filter(Order.status.in_(("paid", "shipped", "delivered")))
        .scalar(),
        "pending_orders": Order.query.filter_by(status="pending").count(),
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    low_stock = (
        Product.query.filter(Product.stock < 5)
        .order_by(Product.stock.asc())
        .limit(6)
        .all()
    )
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_orders=recent_orders,
        low_stock=low_stock,
    )


# ----- Products -----
@bp.route("/products")
def products():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    query = Product.query
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/products.html", pagination=pagination, products=pagination.items, q=q
    )


@bp.route("/products/new", methods=["GET", "POST"])
def product_create():
    form = ProductForm()
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]
    if not form.category_id.choices:
        flash("Please create a category first.", "error")
        return redirect(url_for("admin.categories"))

    if form.validate_on_submit():
        product = Product(
            name=form.name.data.strip(),
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            category_id=form.category_id.data,
            is_active=form.is_active.data,
        )
        product.slug = unique_slug(Product, product.name)
        filename = save_upload(form.image.data)
        if filename:
            product.image = filename
        db.session.add(product)
        db.session.commit()
        flash("Product created.", "success")
        return redirect(url_for("admin.products"))

    return render_template(
        "admin/product_form.html", form=form, title="Create Product", product=None
    )


@bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]

    if form.validate_on_submit():
        product.name = form.name.data.strip()
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.category_id = form.category_id.data
        product.is_active = form.is_active.data
        filename = save_upload(form.image.data)
        if filename:
            product.image = filename
        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("admin.products"))

    return render_template(
        "admin/product_form.html",
        form=form,
        title="Edit Product",
        product=product,
    )


@bp.route("/products/<int:product_id>/delete", methods=["POST"])
def product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "info")
    return redirect(url_for("admin.products"))


# ----- Categories -----
@bp.route("/categories", methods=["GET", "POST"])
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data.strip()).first():
            flash("Category already exists.", "error")
        else:
            cat = Category(name=form.name.data.strip())
            cat.slug = unique_slug(Category, cat.name)
            db.session.add(cat)
            db.session.commit()
            flash("Category added.", "success")
        return redirect(url_for("admin.categories"))

    cats = Category.query.order_by(Category.name).all()
    return render_template("admin/categories.html", form=form, categories=cats)


@bp.route("/categories/<int:cat_id>/delete", methods=["POST"])
def category_delete(cat_id):
    cat = Category.query.get_or_404(cat_id)
    if cat.products:
        flash("Cannot delete category with products.", "error")
    else:
        db.session.delete(cat)
        db.session.commit()
        flash("Category deleted.", "info")
    return redirect(url_for("admin.categories"))


# ----- Orders -----
@bp.route("/orders")
def orders():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "").strip()
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/orders.html",
        pagination=pagination,
        orders=pagination.items,
        status=status,
    )


@bp.route("/orders/<int:order_id>", methods=["GET", "POST"])
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    form = UpdateStatusForm(status=order.status)
    if form.validate_on_submit():
        new_status = form.status.data
        if order.status != "cancelled" and new_status == "cancelled":
            for item in order.items:
                if item.product:
                    item.product.stock += item.quantity
        order.status = new_status
        db.session.commit()
        flash("Order status updated.", "success")
        return redirect(url_for("admin.order_detail", order_id=order.id))
    return render_template("admin/order_detail.html", order=order, form=form)


# ----- Users -----
@bp.route("/users")
def users():
    page = request.args.get("page", 1, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/users.html", pagination=pagination, users=pagination.items
    )


@bp.route("/users/<int:user_id>/toggle-admin", methods=["POST"])
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    from flask_login import current_user

    if user.id == current_user.id:
        flash("You cannot change your own admin status.", "error")
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f"Updated {user.name}'s admin status.", "success")
    return redirect(url_for("admin.users"))
