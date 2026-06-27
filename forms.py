from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    TextAreaField,
    IntegerField,
    FloatField,
    SelectField,
    BooleanField,
    HiddenField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    NumberRange,
    Optional,
)


_email_validator = Email(check_deliverability=False)


class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(2, 120)])
    email = StringField("Email", validators=[DataRequired(), _email_validator])
    password = PasswordField("Password", validators=[DataRequired(), Length(6, 128)])
    confirm = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", "Passwords must match")],
    )


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), _email_validator])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(2, 200)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=4000)])
    price = FloatField("Price", validators=[DataRequired(), NumberRange(min=0.01)])
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    image = FileField(
        "Image",
        validators=[
            Optional(),
            FileAllowed(["png", "jpg", "jpeg", "webp", "gif"], "Images only!"),
        ],
    )
    is_active = BooleanField("Active", default=True)


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(2, 80)])


class CheckoutForm(FlaskForm):
    shipping_name = StringField("Full Name", validators=[DataRequired(), Length(2, 120)])
    shipping_phone = StringField("Phone", validators=[DataRequired(), Length(7, 20)])
    shipping_address = TextAreaField("Address", validators=[DataRequired(), Length(5, 500)])
    shipping_city = StringField("City", validators=[DataRequired(), Length(2, 80)])
    payment_method = SelectField(
        "Payment Method",
        choices=[("cod", "Cash on Delivery"), ("card", "Credit/Debit Card (Demo)")],
        validators=[DataRequired()],
    )


class ReviewForm(FlaskForm):
    rating = SelectField(
        "Rating",
        choices=[(5, "5 - Excellent"), (4, "4 - Good"), (3, "3 - Average"), (2, "2 - Poor"), (1, "1 - Terrible")],
        coerce=int,
        validators=[DataRequired()],
    )
    comment = TextAreaField("Review", validators=[Optional(), Length(max=1000)])


class UpdateStatusForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("shipped", "Shipped"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelled"),
        ],
        validators=[DataRequired()],
    )
