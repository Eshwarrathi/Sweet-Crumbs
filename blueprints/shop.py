from flask import Blueprint, render_template, request, abort, current_app
from sqlalchemy import or_

from extensions import db
from models import Product, Category, Review
from forms import ReviewForm

bp = Blueprint("shop", __name__)


@bp.route("/")
def home():
    categories = Category.query.order_by(Category.name).all()
    featured = (
        Product.query.filter_by(is_active=True)
        .order_by(Product.created_at.desc())
        .limit(8)
        .all()
    )
    return render_template("shop/home.html", categories=categories, featured=featured)


@bp.route("/products")
def products():
    page = request.args.get("page", 1, type=int)
    category_slug = request.args.get("category")
    q = request.args.get("q", "").strip()
    sort = request.args.get("sort", "newest")

    query = Product.query.filter_by(is_active=True)

    active_category = None
    if category_slug:
        active_category = Category.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter_by(category_id=active_category.id)

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(Product.name.ilike(pattern), Product.description.ilike(pattern))
        )

    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "name":
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    per_page = current_app.config["ITEMS_PER_PAGE"]
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.order_by(Category.name).all()

    return render_template(
        "shop/products.html",
        pagination=pagination,
        products=pagination.items,
        categories=categories,
        active_category=active_category,
        q=q,
        sort=sort,
    )


@bp.route("/product/<slug>", methods=["GET", "POST"])
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()

    review_form = ReviewForm()
    user_review = None
    from flask_login import current_user

    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            user_id=current_user.id, product_id=product.id
        ).first()

    related = (
        Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.is_active.is_(True),
        )
        .limit(4)
        .all()
    )

    return render_template(
        "shop/product_detail.html",
        product=product,
        review_form=review_form,
        user_review=user_review,
        related=related,
    )
