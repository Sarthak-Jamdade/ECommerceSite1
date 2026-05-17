from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
from mysql.connector import pooling
import os
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = "ecommerce_secret"

# -----------------------------------------------
# DATABASE — connection pool
# -----------------------------------------------
db_config = {
    "host"     : "localhost",
    "user"     : "root",
    "password" : "newpassword",
    "database" : "ecommerce",
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name = "ecommerce_pool",
    pool_size  = 5,
    **db_config
)

def get_db():
    return connection_pool.get_connection()


# -----------------------------------------------
# UPLOAD FOLDER
# -----------------------------------------------
UPLOAD_FOLDER      = "static/uploads/profiles"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -----------------------------------------------
# HELPER — parse first image from JSON array
# Your DB stores img as: ["url1", "url2", ...]
# -----------------------------------------------
def get_first_img(img_str):
    if not img_str:
        return ""
    try:
        imgs = json.loads(img_str)
        if isinstance(imgs, list) and imgs:
            return imgs[0]
        return img_str
    except Exception:
        return img_str


def fix_imgs(product_list):
    """Parse image for a list of product dicts."""
    for p in product_list:
        p["img"] = get_first_img(p.get("img", ""))
    return product_list


# -----------------------------------------------
# HELPER — CURRENT USER
# -----------------------------------------------
def get_current_user():
    return session.get("user", None)


# -----------------------------------------------
# DECORATORS
# -----------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_user():
            flash("Please login to continue.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user or user["role"] != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def seller_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user or user["role"] != "seller":
            flash("Seller access only.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# -----------------------------------------------
# HOME
# -----------------------------------------------
@app.route("/")
def index():
    return redirect(url_for("newHome"))


@app.route("/home")
def newHome():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products LIMIT 8")
    products = cursor.fetchall()

    cursor.execute("SELECT * FROM products ORDER BY p_id DESC LIMIT 8")
    new_products = cursor.fetchall()

    cursor.close()
    conn.close()

    # ── Fix images ──
    fix_imgs(products)
    fix_imgs(new_products)

    return render_template("index.html",
        products     = products,
        new_products = new_products,
        user         = get_current_user()
    )


# -----------------------------------------------
# SHOP
# -----------------------------------------------
@app.route("/shop")
def shop():
    conn     = get_db()
    cursor   = conn.cursor(dictionary=True)
    category = request.args.get("category", "").strip()

    if category:
        cursor.execute(
            "SELECT * FROM products WHERE LOWER(category) LIKE %s LIMIT 200",
            (f"%{category.lower()}%",)
        )
    else:
        cursor.execute("SELECT * FROM products LIMIT 200")

    products = cursor.fetchall()
    cursor.close()
    conn.close()

    # ── Fix images ──
    fix_imgs(products)

    return render_template("shop.html",
        products = products,
        user     = get_current_user()
    )


# -----------------------------------------------
# SEARCH
# -----------------------------------------------
@app.route("/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return redirect(url_for("shop"))

    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    like_q = f"%{query.lower()}%"
    cursor.execute(
        """
        SELECT * FROM products
        WHERE LOWER(name)  LIKE %s
           OR LOWER(brand) LIKE %s
        LIMIT 60
        """,
        (like_q, like_q)
    )

    search_results = cursor.fetchall()
    cursor.close()
    conn.close()

    # ── Fix images ──
    fix_imgs(search_results)

    return render_template("shop.html",
        products = search_results,
        user     = get_current_user()
    )


# -----------------------------------------------
# PRODUCT DETAIL
# -----------------------------------------------
@app.route("/product/<int:p_id>")
def product(p_id):
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p_id, name, price, colour, brand,
               img, ratingCount, avg_rating, description, category
        FROM products
        WHERE p_id = %s
    """, (p_id,))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        conn.close()
        flash("Product not found.", "error")
        return redirect(url_for("shop"))

    # ── Fix main product image ──
    product["img"] = get_first_img(product.get("img", ""))

    # gallery — empty list (fetch from gallery table here if you have one)
    gallery = []

    # RELATED — Tier 1: same category
    related_products = []
    if product.get("category"):
        cursor.execute("""
            SELECT p_id, name, brand, price, img
            FROM products
            WHERE LOWER(TRIM(category)) = LOWER(TRIM(%s))
              AND p_id != %s
            LIMIT 4
        """, (product["category"], p_id))
        related_products = cursor.fetchall()

    # RELATED — Tier 2: same brand
    if not related_products and product.get("brand"):
        cursor.execute("""
            SELECT p_id, name, brand, price, img
            FROM products
            WHERE LOWER(TRIM(brand)) = LOWER(TRIM(%s))
              AND p_id != %s
            LIMIT 4
        """, (product["brand"], p_id))
        related_products = cursor.fetchall()

    # RELATED — Tier 3: any 4 products (absolute fallback)
    if not related_products:
        cursor.execute("""
            SELECT p_id, name, brand, price, img
            FROM products
            WHERE p_id != %s
            LIMIT 4
        """, (p_id,))
        related_products = cursor.fetchall()

    cursor.close()
    conn.close()

    # ── Fix related product images ──
    related_products = [dict(r) for r in related_products]
    for r in related_products:
        r["img"] = get_first_img(r.get("img",""))
    thumb_images = [product["img"]]
    for r in related_products[:2]:
        if r.get("img") and r["img"] != product["img"]:
            thumb_images.append(r["img"])
    while len(thumb_images) < 3:
        thumb_images.append(product["img"])

    return render_template("product.html",
        thumb_images     = thumb_images,
        product          = product,
        gallery          = gallery,
        related_products = related_products,
        user             = get_current_user()
    )


# -----------------------------------------------
# ADD TO CART
# -----------------------------------------------
@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    customer_name  = request.form.get("customer_name", "").strip()
    customer_email = request.form.get("customer_email", "").strip()
    p_id           = str(request.form.get("p_id"))
    price          = float(request.form.get("price"))
    quantity       = int(request.form.get("quantity", 1))
    product_name   = request.form.get("product_name", "")
    img            = request.form.get("img", "")
    total_amount   = price * quantity

    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]

    existing = next((item for item in cart if str(item["p_id"]) == p_id), None)

    if existing:
        existing["quantity"] += quantity
        session.modified = True
    else:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders
                (customer_name, customer_email, total_amount, payment_status, order_status)
            VALUES (%s, %s, %s, 'Pending', 'Pending')
        """, (customer_name, customer_email, total_amount))
        conn.commit()
        order_id = cursor.lastrowid
        cursor.close()
        conn.close()

        cart.append({
            "order_id" : order_id,
            "p_id"     : p_id,
            "name"     : product_name,
            "img"      : img,
            "price"    : price,
            "quantity" : quantity
        })

    session["cart"]  = cart
    session.modified = True

    return redirect(url_for("cart"))


# -----------------------------------------------
# CART
# -----------------------------------------------
@app.route("/cart")
def cart():
    cart        = session.get("cart", [])
    total_price = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("cart.html",
        cart        = cart,
        total_price = total_price,
        user        = get_current_user()
    )


# -----------------------------------------------
# REMOVE FROM CART
# -----------------------------------------------
@app.route("/remove-from-cart", methods=["POST"])
def remove_from_cart():
    order_id = request.form.get("order_id")
    cart     = session.get("cart", [])
    cart     = [item for item in cart if str(item["order_id"]) != str(order_id)]

    session["cart"]  = cart
    session.modified = True

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM orders WHERE order_id = %s AND payment_status = 'Pending'",
        (order_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("cart"))


# -----------------------------------------------
# PAYMENT
# -----------------------------------------------
@app.route("/payment", methods=["POST"])
def payment():
    customer_name  = request.form.get("customer_name")
    customer_email = request.form.get("customer_email")
    total_amount   = request.form.get("total_amount")
    order_ids      = request.form.getlist("order_id")
    p_ids          = request.form.getlist("p_id")
    prices         = request.form.getlist("price")
    quantities     = request.form.getlist("quantity")

    return render_template("payment.html",
        customer_name  = customer_name,
        customer_email = customer_email,
        total_amount   = total_amount,
        order_ids      = order_ids,
        p_ids          = p_ids,
        prices         = prices,
        quantities     = quantities,
        user           = get_current_user()
    )


# -----------------------------------------------
# PAYMENT SUCCESS
# -----------------------------------------------
@app.route("/payment-success", methods=["POST"])
def payment_success():
    order_ids  = request.form.getlist("order_id")
    p_ids      = request.form.getlist("p_id")
    prices     = request.form.getlist("price")
    quantities = request.form.getlist("quantity")

    if not order_ids or not p_ids:
        flash("No items to complete payment for.", "error")
        return redirect(url_for("cart"))

    conn   = get_db()
    cursor = conn.cursor()

    for i in range(len(p_ids)):
        cursor.execute("""
            INSERT INTO order_items (order_id, p_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """, (order_ids[i], p_ids[i], int(quantities[i]), float(prices[i])))

        cursor.execute("""
            UPDATE orders
            SET payment_status = 'Paid', order_status = 'Processing'
            WHERE order_id = %s
        """, (order_ids[i],))

    conn.commit()
    cursor.close()
    conn.close()

    session.pop("cart", None)

    return redirect(url_for("order_success", order_id=order_ids[0]))


# -----------------------------------------------
# ORDER SUCCESS
# -----------------------------------------------
@app.route("/order-success/<int:order_id>")
def order_success(order_id):
    return render_template("order_success.html",
        order_id = order_id,
        user     = get_current_user()
    )


# -----------------------------------------------
# REGISTER
# -----------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone    = request.form.get("phone", "").strip()
        address  = request.form.get("address", "").strip()
        role     = request.form.get("role", "customer")

        if not name or not email or not password:
            flash("Name, email and password are required.", "error")
            return redirect(url_for("register"))

        profile_photo = "uploads/profiles/default.png"
        if "profile_photo" in request.files:
            file = request.files["profile_photo"]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{email}_{file.filename}")
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                profile_photo = f"uploads/profiles/{filename}"

        hashed_password = generate_password_hash(password)

        conn   = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users
                    (name, email, password, phone, address, profile_photo, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, email, hashed_password, phone, address, profile_photo, role))
            conn.commit()
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for("login"))

        except mysql.connector.IntegrityError:
            flash("An account with that email already exists.", "error")
            return redirect(url_for("register"))
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html", user=get_current_user())


# -----------------------------------------------
# LOGIN
# -----------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn   = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = {
                "user_id"       : user["user_id"],
                "name"          : user["name"].split()[0],
                "email"         : user["email"],
                "role"          : user["role"],
                "profile_photo" : user["profile_photo"]
            }

            if user["role"] == "admin":
                return redirect(url_for("admin_orders"))
            elif user["role"] == "seller":
                return redirect(url_for("seller_dashboard"))
            else:
                return redirect(url_for("newHome"))

        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html", user=get_current_user())


# -----------------------------------------------
# LOGOUT
# -----------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -----------------------------------------------
# PROFILE
# -----------------------------------------------
@app.route("/profile")
@login_required
def profile():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (get_current_user()["user_id"],))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("profile.html", user=get_current_user(), user_data=user_data)


# -----------------------------------------------
# ADMIN — ORDERS
# -----------------------------------------------
@app.route("/admin/orders")
@admin_required
def admin_orders():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            o.*,
            oi.p_id,
            oi.quantity,
            oi.price          AS item_price,
            p.name            AS product_name,
            p.img             AS product_img,
            p.brand           AS product_brand
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        LEFT JOIN products    p  ON oi.p_id    = p.p_id
        ORDER BY o.created_at DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    orders = {}
    for row in rows:
        oid = row["order_id"]
        if oid not in orders:
            orders[oid] = {
                "order_id"       : row["order_id"],
                "customer_name"  : row["customer_name"],
                "customer_email" : row["customer_email"],
                "total_amount"   : row["total_amount"],
                "payment_status" : row["payment_status"],
                "order_status"   : row["order_status"],
                "created_at"     : row["created_at"],
                "items"          : []
            }
        if row["p_id"]:
            orders[oid]["items"].append({
                "product_name"  : row["product_name"],
                "product_img"   : get_first_img(row["product_img"]),
                "product_brand" : row["product_brand"],
                "quantity"      : row["quantity"],
                "price"         : row["item_price"]
            })

    return render_template("admin_orders.html",
        orders = list(orders.values()),
        user   = get_current_user()
    )


# -----------------------------------------------
# ADMIN — UPDATE ORDER STATUS
# -----------------------------------------------
@app.route("/admin/update-order-status", methods=["POST"])
@admin_required
def admin_update_order_status():
    order_id     = request.form.get("order_id")
    order_status = request.form.get("order_status")

    valid_statuses = {"Pending", "Processing", "Shipped", "Delivered", "Cancelled"}
    if order_status not in valid_statuses:
        flash("Invalid status.", "error")
        return redirect(url_for("admin_orders"))

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET order_status = %s WHERE order_id = %s",
        (order_status, order_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Order #{order_id} updated to {order_status}.", "success")
    return redirect(url_for("admin_orders"))


# -----------------------------------------------
# SELLER DASHBOARD
# -----------------------------------------------
@app.route("/seller/dashboard")
@seller_required
def seller_dashboard():
    user   = get_current_user()
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM products WHERE seller_id = %s ORDER BY p_id DESC",
            (user["user_id"],)
        )
        seller_products = cursor.fetchall()
        fix_imgs(seller_products)
    except Exception:
        seller_products = []

    cursor.close()
    conn.close()

    return render_template("seller_dashboard.html",
        user            = user,
        seller_products = seller_products
    )


# -----------------------------------------------
# STATIC PAGES
# -----------------------------------------------
@app.route("/blog")
def blog():
    return render_template("blog.html", user=get_current_user())


@app.route("/contact")
def contact():
    return render_template("contact.html", user=get_current_user())


@app.route("/about")
def about():
    return render_template("about.html", user=get_current_user())


# -----------------------------------------------
# RUN
# -----------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)