import uuid

from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user

from extensions import db
from models import CartItem, Order, OrderItem, Product
from forms import CheckoutForm

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash("Your cart is empty.", "info")
        return redirect(url_for("cart.view"))

    for item in items:
        if item.product.stock < item.quantity:
            flash(
                f"Only {item.product.stock} of '{item.product.name}' available.",
                "error",
            )
            return redirect(url_for("cart.view"))

    total = sum(i.subtotal for i in items)
    form = CheckoutForm()

    if request.method == "GET":
        form.shipping_name.data = current_user.name
        form.shipping_phone.data = current_user.phone or ""
        form.shipping_address.data = current_user.address or ""
        form.shipping_city.data = current_user.city or ""

    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id,
            total=total,
            status="pending",
            payment_method=form.payment_method.data,
            shipping_name=form.shipping_name.data.strip(),
            shipping_phone=form.shipping_phone.data.strip(),
            shipping_address=form.shipping_address.data.strip(),
            shipping_city=form.shipping_city.data.strip(),
        )
        db.session.add(order)
        db.session.flush()

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
            )
            db.session.add(order_item)
            item.product.stock -= item.quantity

        if form.payment_method.data == "card":
            order.status = "paid"
            order.payment_ref = f"DEMO-{uuid.uuid4().hex[:10].upper()}"

        if not current_user.phone:
            current_user.phone = form.shipping_phone.data.strip()
        if not current_user.address:
            current_user.address = form.shipping_address.data.strip()
        if not current_user.city:
            current_user.city = form.shipping_city.data.strip()

        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        flash("Order placed successfully!", "success")
        return redirect(url_for("orders.detail", order_id=order.id))

    return render_template("orders/checkout.html", form=form, items=items, total=total)


@bp.route("/")
@login_required
def list_orders():
    orders = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template("orders/orders.html", orders=orders)


@bp.route("/<int:order_id>")
@login_required
def detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template("orders/order_detail.html", order=order)


@bp.route("/<int:order_id>/cancel", methods=["POST"])
@login_required
def cancel(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    if order.status not in ("pending", "paid"):
        flash("This order cannot be cancelled.", "error")
        return redirect(url_for("orders.detail", order_id=order.id))
    order.status = "cancelled"
    for item in order.items:
        if item.product:
            item.product.stock += item.quantity
    db.session.commit()
    flash("Order cancelled.", "info")
    return redirect(url_for("orders.detail", order_id=order.id))
