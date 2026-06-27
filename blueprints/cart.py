from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import login_required, current_user

from extensions import db
from models import CartItem, Product

bp = Blueprint("cart", __name__, url_prefix="/cart")


@bp.route("/")
@login_required
def view():
    items = (
        CartItem.query.filter_by(user_id=current_user.id)
        .order_by(CartItem.added_at.desc())
        .all()
    )
    total = sum(i.subtotal for i in items)
    return render_template("cart/cart.html", items=items, total=total)


@bp.route("/add/<int:product_id>", methods=["POST"])
@login_required
def add(product_id):
    product = Product.query.get_or_404(product_id)
    if not product.is_active or product.stock < 1:
        flash("Product is out of stock.", "error")
        return redirect(request.referrer or url_for("shop.products"))

    qty = max(1, request.form.get("quantity", 1, type=int))
    qty = min(qty, product.stock)

    item = CartItem.query.filter_by(
        user_id=current_user.id, product_id=product.id
    ).first()
    if item:
        item.quantity = min(item.quantity + qty, product.stock)
    else:
        item = CartItem(user_id=current_user.id, product_id=product.id, quantity=qty)
        db.session.add(item)

    db.session.commit()
    flash(f"Added '{product.name}' to cart.", "success")
    return redirect(request.referrer or url_for("cart.view"))


@bp.route("/update/<int:item_id>", methods=["POST"])
@login_required
def update(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash("Not allowed.", "error")
        return redirect(url_for("cart.view"))

    qty = request.form.get("quantity", 1, type=int)
    if qty < 1:
        db.session.delete(item)
        flash("Item removed from cart.", "info")
    else:
        item.quantity = min(qty, item.product.stock)
        flash("Cart updated.", "success")
    db.session.commit()
    return redirect(url_for("cart.view"))


@bp.route("/remove/<int:item_id>", methods=["POST"])
@login_required
def remove(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash("Not allowed.", "error")
        return redirect(url_for("cart.view"))
    db.session.delete(item)
    db.session.commit()
    flash("Item removed.", "info")
    return redirect(url_for("cart.view"))


@bp.route("/clear", methods=["POST"])
@login_required
def clear():
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash("Cart cleared.", "info")
    return redirect(url_for("cart.view"))
