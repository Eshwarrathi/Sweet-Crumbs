from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user

from extensions import db
from models import Review, Product, OrderItem, Order
from forms import ReviewForm

bp = Blueprint("reviews", __name__, url_prefix="/reviews")


@bp.route("/product/<int:product_id>", methods=["POST"])
@login_required
def add(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()

    has_purchased = (
        db.session.query(OrderItem)
        .join(Order)
        .filter(
            Order.user_id == current_user.id,
            OrderItem.product_id == product.id,
            Order.status.in_(("paid", "shipped", "delivered")),
        )
        .first()
        is not None
    )
    if not has_purchased:
        flash("You can review only products you've purchased.", "error")
        return redirect(url_for("shop.product_detail", slug=product.slug))

    if not form.validate_on_submit():
        flash("Invalid review submission.", "error")
        return redirect(url_for("shop.product_detail", slug=product.slug))

    existing = Review.query.filter_by(
        user_id=current_user.id, product_id=product.id
    ).first()
    if existing:
        existing.rating = form.rating.data
        existing.comment = (form.comment.data or "").strip()
        flash("Review updated.", "success")
    else:
        review = Review(
            user_id=current_user.id,
            product_id=product.id,
            rating=form.rating.data,
            comment=(form.comment.data or "").strip(),
        )
        db.session.add(review)
        flash("Thank you for your review!", "success")

    db.session.commit()
    return redirect(url_for("shop.product_detail", slug=product.slug))


@bp.route("/<int:review_id>/delete", methods=["POST"])
@login_required
def delete(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id and not current_user.is_admin:
        flash("Not allowed.", "error")
        return redirect(request.referrer or url_for("shop.home"))
    product_slug = review.product.slug
    db.session.delete(review)
    db.session.commit()
    flash("Review deleted.", "info")
    return redirect(url_for("shop.product_detail", slug=product_slug))
