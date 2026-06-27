"""Seed database with admin user, sample categories, and sample products."""
from app import create_app
from extensions import db
from models import User, Category, Product
from helpers import unique_slug


BAKERY_CATEGORIES = [
    "Cakes",
    "Cookies",
    "Pastries",
    "Breads",
    "Cupcakes",
    "Donuts",
]

BAKERY_PRODUCTS = [
    ("Chocolate Fudge Cake", "Cakes", 2499, 15,
     "Rich three-layer chocolate fudge cake with Belgian chocolate ganache. Perfect for celebrations.",
     "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600"),
    ("Red Velvet Cake", "Cakes", 2799, 10,
     "Classic red velvet cake with cream cheese frosting. Moist, fluffy, and absolutely divine.",
     "https://images.unsplash.com/photo-1586788680434-30d324b2d46f?w=600"),
    ("Pineapple Upside-Down Cake", "Cakes", 2199, 8,
     "Caramelized pineapple rings on a soft vanilla cake. A tropical delight.",
     "https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?w=600"),
    ("Strawberry Cheesecake", "Cakes", 2999, 12,
     "Creamy New York style cheesecake topped with fresh strawberry compote.",
     "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=600"),
    ("Chocolate Chip Cookies (Pack of 12)", "Cookies", 699, 50,
     "Classic homemade chocolate chip cookies. Crispy edges, gooey center. Freshly baked daily.",
     "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=600"),
    ("Double Chocolate Cookies (Pack of 6)", "Cookies", 499, 40,
     "Ultra-rich double chocolate cookies with dark and white chocolate chunks.",
     "https://images.unsplash.com/photo-1590080872582-1e8cdb9b7e2e?w=600"),
    ("Oatmeal Raisin Cookies (Pack of 12)", "Cookies", 649, 35,
     "Chewy oatmeal cookies with plump raisins and a hint of cinnamon.",
     "https://images.unsplash.com/photo-1621534294663-0a561e0e0cfc?w=600"),
    ("Butter Cookies (Pack of 20)", "Cookies", 549, 60,
     "Melt-in-your-mouth butter cookies. Light, crispy, and perfectly sweetened.",
     "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600"),
    ("Flaky Croissant (Pack of 4)", "Pastries", 899, 25,
     "Buttery, golden, flaky French croissants. Baked fresh every morning.",
     "https://images.unsplash.com/photo-1555507036-ab1f40380241?w=600"),
    ("Apple Turnover (Pack of 4)", "Pastries", 749, 20,
     "Puff pastry filled with cinnamon-spiced apple filling. Golden and delicious.",
     "https://images.unsplash.com/photo-1622473590775-f58a4f3a8708?w=600"),
    ("Cream Puff - Dozen", "Pastries", 1199, 18,
     "Light choux pastry filled with silky vanilla pastry cream. Dusted with powdered sugar.",
     "https://images.unsplash.com/photo-1591287083679-0437c42f867d?w=600"),
    ("Pain au Chocolat (Pack of 4)", "Pastries", 999, 22,
     "Flaky croissant dough wrapped around rich dark chocolate batons.",
     "https://images.unsplash.com/photo-1555947299-8c644d2ad102?w=600"),
    ("Sourdough Loaf", "Breads", 499, 20,
     "Artisan sourdough with crispy crust and soft, tangy crumb. Naturally fermented 24 hours.",
     "https://images.unsplash.com/photo-1585478259715-876a8c3d1e93?w=600"),
    ("Whole Wheat Bread Loaf", "Breads", 349, 30,
     "Hearty whole wheat bread packed with fiber. Perfect for sandwiches and toast.",
     "https://images.unsplash.com/photo-1598373182133-52452f1a0e1a?w=600"),
    ("Brioche Bun (Pack of 6)", "Breads", 599, 25,
     "Soft, buttery French brioche buns. Perfect for burgers or sweet toppings.",
     "https://images.unsplash.com/photo-1549931319-a545563bfed0?w=600"),
    ("Cinnamon Roll (Pack of 4)", "Cupcakes", 899, 30,
     "Soft cinnamon rolls with cream cheese icing. Baked fresh and gooey.",
     "https://images.unsplash.com/photo-1509365465985-25d11c17e812?w=600"),
    ("Vanilla Cupcake with Buttercream", "Cupcakes", 399, 40,
     "Light vanilla cupcake topped with silky buttercream and rainbow sprinkles.",
     "https://images.unsplash.com/photo-1550617931-e17a7b70dce2?w=600"),
    ("Chocolate Cupcake with Ganache", "Cupcakes", 449, 40,
     "Moist chocolate cupcake with a rich dark chocolate ganache swirl.",
     "https://images.unsplash.com/photo-1599785209707-a456fc1337bb?w=600"),
    ("Classic Glazed Donut (Pack of 6)", "Donuts", 549, 45,
     "Light and fluffy yeast donuts with a sweet glossy glaze. A timeless favorite.",
     "https://images.unsplash.com/photo-1551024601-bec78aea704b?w=600"),
    ("Chocolate Donut with Sprinkles (Pack of 6)", "Donuts", 649, 40,
     "Chocolate frosted donuts topped with rainbow sprinkles. Fun and delicious!",
     "https://images.unsplash.com/photo-1612240498936-65f5101365d2?w=600"),
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        admin_email = app.config["ADMIN_EMAIL"]
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(name="Admin", email=admin_email, is_admin=True)
            admin.set_password(app.config["ADMIN_PASSWORD"])
            db.session.add(admin)
            print(f"  -> admin created: {admin_email} / {app.config['ADMIN_PASSWORD']}")
        else:
            print(f"  -> admin already exists: {admin_email}")

        Product.query.delete()
        Category.query.delete()
        db.session.flush()

        cat_map = {}
        for name in BAKERY_CATEGORIES:
            cat = Category(name=name, slug=unique_slug(Category, name))
            db.session.add(cat)
            db.session.flush()
            cat_map[name] = cat
        print(f"  -> {len(cat_map)} categories ready")

        added = 0
        for name, cat_name, price, stock, desc, img_url in BAKERY_PRODUCTS:
            product = Product(
                name=name,
                slug=unique_slug(Product, name),
                description=desc,
                price=price,
                stock=stock,
                category_id=cat_map[cat_name].id,
                image=img_url,
                is_active=True,
            )
            db.session.add(product)
            added += 1
        print(f"  -> {added} products added")

        db.session.commit()
        print("\nSeeding complete!")
        print("=" * 50)
        print(f"  Admin Login:  {admin_email}")
        print(f"  Password:     {app.config['ADMIN_PASSWORD']}")
        print("=" * 50)


if __name__ == "__main__":
    seed()
