# ----------------------------------------------------
# Real-World E-commerce Webapp
# ----------------------------------------------------
#
# This file contains the updated code for  Flask e-commerce application.
# It addresses the key areas:
# 1. Security (Auth and SQL Injection)
# 2. Payment Integration (Stripe)

import sqlite3
import stripe
import os
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)

# ---------------------------------
# STRIPE INTEGRATION
# ---------------------------------

# Use os.environ.get() to securely get keys from environment variables
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "SK_TEST_PLACEHOLDER")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "PK_TEST_PLACEHOLDER")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "WHSEC_PLACEHOLDER")


# ----------------------------------------------------
# 1. Database Connection and Helper Functions
# ----------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_item(item_id):
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM Items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if item is None:
        abort(404)
    return item


# ----------------------------------------------------
# 2. Flask-Login Integration for Secure Authentication
# ----------------------------------------------------
# To address the direct URL access issue, we'll use Flask-Login.

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY", "Default_Insecure_Fallback_Key"
)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "sign_in"  # Tells Flask-Login where the login page is


# A simple user class to work with Flask-Login.
class Admin(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username
        self.is_admin = True

    def is_active(self):
        return True


class AppUser(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username
        self.is_admin = False

    def is_active(self):
        return True


# This is a callback function required by Flask-Login.
# It reloads the user object from the user ID stored in the session.
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    # Check for admin
    user_data = conn.execute(
        "SELECT * FROM Admin WHERE a_id = ?", (user_id,)
    ).fetchone()
    if user_data:
        return Admin(user_data["a_id"], user_data["username"])
    # Check for regular user
    user_data = conn.execute("SELECT * FROM User WHERE u_id = ?", (user_id,)).fetchone()
    if user_data:
        return AppUser(user_data["u_id"], user_data["u_username"])
    return None


# ----------------------------------------------------
# 3. Main Routes (Updated with security features)
# ----------------------------------------------------


@app.route("/")
def index():
    return render_template("index.html")


# Admin sign-in route
@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if current_user.is_authenticated:
        return redirect(url_for("category"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        admin_data = conn.execute(
            "SELECT * FROM Admin WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if admin_data and check_password_hash(admin_data["password"], password):
            # Log in the user using Flask-Login
            admin = Admin(admin_data["a_id"], admin_data["username"])
            login_user(admin)
            flash("Logged in successfully!", "success")
            return redirect(url_for("category"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("sign_in.html")


# Logout route
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/category", methods=("GET", "POST"))
@login_required
def category():
    # Since we are using login_required, we know the user is authenticated.
    # Now, let's make sure they are an admin.
    if not current_user.is_admin:
        abort(403)

    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM Categories").fetchall()
    conn.close()

    if request.method == "POST":
        category_name = request.form["category_name"]
        if not category_name:
            flash("Category name is required!")
        else:
            conn = get_db_connection()
            conn.execute("INSERT INTO Categories (c_name) VALUES (?)", (category_name,))
            conn.commit()
            conn.close()
            return redirect(url_for("category"))

    return render_template("category.html", categories=categories)


@app.route("/<int:c_id>/c_edit", methods=("GET", "POST"))
@login_required
def c_edit(c_id):
    if not current_user.is_admin:
        abort(403)
    conn = get_db_connection()
    category = conn.execute("SELECT * FROM Categories WHERE c_id=?", (c_id,)).fetchone()
    conn.close()

    if request.method == "POST":
        category_name = request.form["category_name"]
        if not category_name:
            flash("Name is required!")
        else:
            conn = get_db_connection()
            conn.execute(
                "UPDATE Categories SET c_name = ? WHERE c_id = ?", (category_name, c_id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("category"))
    return render_template("c_edit.html", category=category)


@app.route("/<int:c_id>/c_delete", methods=("POST",))
@login_required
def c_delete(c_id):
    if not current_user.is_admin:
        abort(403)
    conn = get_db_connection()
    category = conn.execute("SELECT * FROM Categories WHERE c_id=?", (c_id,)).fetchone()
    conn.execute("DELETE from Categories WHERE c_id = ?", (c_id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(category["c_name"]))
    return redirect(url_for("category"))


@app.route("/category/<int:c_id>/items_list", methods=("GET", "POST"))
@login_required
def items_list(c_id):
    if not current_user.is_admin:
        abort(403)
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM Items WHERE c_id=?", (c_id,)).fetchall()
    conn.close()
    if request.method == "POST":
        item_name = request.form["item_name"]
        item_wt = request.form["item_wt"]
        price_per_unit = request.form["price_per_unit"]
        if not item_name:
            flash("Item name is required!")
        else:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO Items (name, weight, price_per_unit, c_id) VALUES (?, ?, ?, ?)",
                (item_name, item_wt, price_per_unit, c_id),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("items_list", c_id=c_id))
    return render_template("items_list.html", items=items)


@app.route("/<int:c_id>/<int:id>/add_stock", methods=("GET", "POST"))
@login_required
def add_stock(c_id, id):
    if not current_user.is_admin:
        abort(403)
    item = get_item(id)
    if request.method == "POST":
        newstock_wt = request.form["newstock_wt"]
        if not newstock_wt:
            flash("Enter valid input!")
        else:
            conn = get_db_connection()
            add = float(newstock_wt) + float(item["weight"])
            conn.execute("UPDATE Items SET weight=? WHERE id = ?", (add, id))
            conn.commit()
            conn.close()
            return redirect(url_for("items_list", c_id=c_id))
    return render_template("add_stock.html", item=item)


@app.route("/<int:c_id>/<int:id>/item_edit", methods=("GET", "POST"))
@login_required
def item_edit(c_id, id):
    if not current_user.is_admin:
        abort(403)
    item = get_item(id)
    if request.method == "POST":
        item_name = request.form["item_name"]
        price_per_unit = request.form["price_per_unit"]
        if not item_name:
            flash("Error!")
        else:
            conn = get_db_connection()
            conn.execute(
                "UPDATE Items SET name = ?, price_per_unit = ? WHERE id = ?",
                (item_name, price_per_unit, id),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("items_list", c_id=c_id))
    return render_template("item_edit.html", item=item)


@app.route("/<int:c_id>/<int:id>/delete", methods=("POST",))
@login_required
def delete(c_id, id):
    if not current_user.is_admin:
        abort(403)
    item = get_item(id)
    conn = get_db_connection()
    conn.execute("DELETE from Items WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(item["name"]))
    return redirect(url_for("items_list", c_id=c_id))


@app.route("/orders", methods=("GET", "POST"))
@login_required
def orders():
    if not current_user.is_admin:
        abort(403)
    conn = get_db_connection()
    orders = conn.execute(
        "SELECT * FROM( Orders inner join Items on item_id=id)inner join User on User.u_id=Orders.u_id"
    ).fetchall()
    conn.close()
    if request.method == "POST":
        u_id = request.form["u_id"]
        if not u_id:
            flash("user_id is required!")
        else:
            conn = get_db_connection()
            u_orders = conn.execute(
                "SELECT * FROM( Orders inner join Items on item_id=id)inner join User on User.u_id=Orders.u_id WHERE Orders.u_id = ?",
                (u_id,),
            ).fetchall()
            return render_template("orders.html", orders=u_orders, u_id=u_id)
    return render_template("orders.html", orders=orders)


@app.route("/<int:order_id>/collected", methods=("POST",))
@login_required
def collected(order_id):
    if not current_user.is_admin:
        abort(403)
    conn = get_db_connection()
    order = conn.execute(
        "SELECT * FROM Orders WHERE order_id = ?", (order_id,)
    ).fetchone()
    conn.close()
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO History (order_id, u_id, item_id, quantity, price) VALUES (?, ?, ?, ?, ?)",
        (
            order["order_id"],
            order["u_id"],
            order["item_id"],
            order["quantity"],
            order["price"],
        ),
    )
    conn.commit()
    conn.close()
    conn = get_db_connection()
    conn.execute("DELETE from Orders WHERE order_id = ?", (order_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("orders"))


@app.route("/<int:order_id>/delete_order", methods=("POST",))
@login_required
def delete_order(order_id):
    if not current_user.is_admin:
        abort(403)
    conn = get_db_connection()
    order = conn.execute(
        "SELECT * FROM Orders WHERE order_id = ?", (order_id,)
    ).fetchone()
    conn.close()
    item = get_item(order["item_id"])
    q = order["quantity"]
    add = float(q) + float(item["weight"])
    conn = get_db_connection()
    conn.execute("UPDATE Items SET weight = ? WHERE id = ?", (add, order["item_id"]))
    conn.commit()
    conn.close()
    conn = get_db_connection()
    conn.execute("DELETE from Orders WHERE order_id = ?", (order_id,))
    conn.commit()
    conn.close()
    flash('order_id = "{}" was successfully deleted!'.format(order["order_id"]))
    return redirect(url_for("orders"))


@app.route("/history", methods=("GET", "POST"))
@login_required
def history():
    if not current_user.is_admin:
        abort(403)
    conn = get_db_connection()
    orders = conn.execute(
        "SELECT * FROM (History inner join User on History.u_id=User.u_id) inner join Items on Items.id=item_id"
    ).fetchall()
    conn.close()
    if request.method == "POST":
        u_id = request.form["u_id"]
        if not u_id:
            flash("user_id is required!")
        else:
            conn = get_db_connection()
            u_orders = conn.execute(
                "SELECT * FROM( History inner join Items on item_id=id)inner join User on User.u_id=History.u_id WHERE History.u_id = ?",
                (u_id,),
            ).fetchall()
            return render_template("history.html", orders=u_orders, u_id=u_id)
    return render_template("history.html", orders=orders)


@app.route("/out_of_stock", methods=("GET", "POST"))
@login_required
def out_of_stock():
    if not current_user.is_admin:
        abort(403)
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM Items WHERE weight=?", (0,)).fetchall()
    conn.close()
    return render_template("out_of_stock.html", items=items)


@app.route("/<int:id>/add_stock", methods=("GET", "POST"))
@login_required
def out_of_stock_add(id):
    if not current_user.is_admin:
        abort(403)
    item = get_item(id)
    if request.method == "POST":
        newstock_wt = request.form["newstock_wt"]
        if not newstock_wt:
            flash("weight is required!")
        else:
            conn = get_db_connection()
            add = float(newstock_wt) + float(item["weight"])
            conn.execute("UPDATE Items SET weight = ? WHERE id = ?", (add, id))
            conn.commit()
            conn.close()
            return redirect(url_for("out_of_stock"))
    return render_template("out_of_stock_add.html", item=item)


@app.route("/add_user", methods=["GET", "POST"])
@login_required
def add_user():
    if not current_user.is_admin:
        abort(403)
    if request.method == "POST":
        username = request.form["u_username"]
        password = request.form["u_password"]

        # CRITICAL FIX: Hash the password before storing it
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO User (u_username, u_password) VALUES (?,?)",
            (username, hashed_password),
        )
        conn.commit()
        conn.close()
        flash("User added successfully!", "success")
        return redirect(url_for("add_user"))
    return render_template("add_user.html")


# User-specific routes
@app.route("/user_signin", methods=["GET", "POST"])
def user_signin():
    if current_user.is_authenticated:
        return redirect(url_for("u_category"))

    if request.method == "POST":
        username = request.form["u_username"]
        password = request.form["u_password"]

        conn = get_db_connection()
        user_data = conn.execute(
            "SELECT * FROM User WHERE u_username = ?", (username,)
        ).fetchone()
        conn.close()

        if user_data and check_password_hash(user_data["u_password"], password):
            user = AppUser(user_data["u_id"], user_data["u_username"])
            login_user(user)
            flash("Logged in as user successfully!", "success")
            return redirect(url_for("u_category"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("user_signin.html")


@app.route("/u_category", methods=("GET", "POST"))
@login_required
def u_category():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM Categories").fetchall()
    conn.close()
    return render_template("u_category.html", categories=categories)


@app.route("/u_category/<int:c_id>/u_items_list", methods=("GET", "POST"))
@login_required
def u_items_list(c_id):
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM Items WHERE c_id = ?", (c_id,)).fetchall()
    conn.close()
    return render_template("u_items_list.html", items=items, c_id=c_id)


@app.route(
    "/u_category/<int:c_id>/u_items_list/<int:i_id>/pre_book", methods=["GET", "POST"]
)
@login_required
def pre_book(c_id, i_id):
    item = get_item(i_id)

    if item["weight"] == 0:
        flash("Out of stock!", "warning")
        return redirect(url_for("u_items_list", c_id=c_id))

    if request.method == "POST":
        item_wt = request.form["item_wt"]
        if not item_wt or float(item_wt) <= 0:
            flash("Please enter a valid weight.", "danger")
        else:
            # Check if cart exists in session, if not create one
            if "cart" not in session:
                session["cart"] = {}

            # Add item to the cart in the session, Use the item ID as the key
            session["cart"][str(i_id)] = {
                "name": item["name"],
                "price": item["price_per_unit"],
                "quantity": float(item_wt),
            }
            # The session needs to be modified directly to trigger saving
            session.modified = True

            flash(f"'{item['name']}' added to your cart!", "success")
            # return redirect(url_for("user_orders"))
            return redirect(url_for("u_items_list", c_id=c_id))
    return render_template("pre_book.html", item=item)


@app.route("/remove_from_cart/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    if "cart" in session and str(item_id) in session["cart"]:
        session["cart"].pop(str(item_id))
        session.modified = True
        flash("Item removed from cart.", "info")
    else:
        flash("Item not found in cart or cart is empty.", "warning")

    return redirect(url_for("user_orders"))


@app.route("/user_orders", methods=("GET",))
@login_required
def user_orders():
    # We now get the user ID from the session via `current_user.id`
    conn = get_db_connection()
    user_orders = conn.execute(
        "SELECT * FROM Orders inner join Items on item_id=id WHERE u_id=?",
        (current_user.id,),
    ).fetchall()
    conn.close()
    return render_template("user_orders.html", orders=user_orders)


@app.route("/<int:order_id>/cancel_order", methods=("POST",))
@login_required
def cancel_order(order_id):
    conn = get_db_connection()
    order = conn.execute(
        "SELECT * FROM Orders WHERE order_id = ?", (order_id,)
    ).fetchone()
    conn.close()

    if order and order["u_id"] == current_user.id:
        item = get_item(order["item_id"])
        q = order["quantity"]
        add = float(q) + float(item["weight"])

        conn = get_db_connection()
        conn.execute(
            "UPDATE Items SET weight = ? WHERE id = ?", (add, order["item_id"])
        )
        conn.commit()
        conn.close()

        conn = get_db_connection()
        conn.execute("DELETE from Orders WHERE order_id = ?", (order_id,))
        conn.commit()
        conn.close()
        flash("Order was successfully canceled!".format(order["order_id"]), "info")
    else:
        flash("You do not have permission to cancel this order.", "danger")

    return redirect(url_for("user_orders"))


@app.route("/user_history", methods=("GET",))
@login_required
def user_history():
    conn = get_db_connection()
    orders = conn.execute(
        "SELECT * FROM History inner join Items on item_id=id where u_id = ?",
        (current_user.id,),
    ).fetchall()
    conn.close()
    return render_template("user_history.html", orders=orders)


# ----------------------------------------------------
# 4. Stripe Payment Integration Routes
# ----------------------------------------------------


@app.route("/create-checkout-session", methods=["POST"])
@login_required
def create_checkout_session():
    # Use the items from the user's session cart
    cart = session.get("cart", {})
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("user_orders"))

    line_items = []
    for item_id, item_data in cart.items():
        # Fetch the real-time item details from the database
        conn = get_db_connection()
        db_item = conn.execute(
            "SELECT * FROM Items WHERE id = ?", (item_id,)
        ).fetchone()
        conn.close()

        if not db_item:
            flash(f"Item with ID {item_id} not found.", "danger")
            continue

        # Create the line item for Stripe based on dynamic data
        unit_price_in_cents = int(float(db_item["price_per_unit"]) * 100)

        item_quantity = int(item_data["quantity"])

        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": db_item["name"],
                    },
                    "unit_amount": unit_price_in_cents,
                },
                "quantity": item_quantity,
            }
        )

    if not line_items:
        flash("There was an issue with your cart items.", "danger")
        return redirect(url_for("user_orders"))

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode="payment",
            success_url=url_for("user_orders", _external=True),
            cancel_url=url_for("user_orders", _external=True),
        )
        # Store checkout session ID and other data to use in the webhook later
        session["checkout_session_id"] = checkout_session.id
        session.modified = True
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return str(e)


# Route to handle successful payment confirmation from Stripe
@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("stripe-signature")
    event = None

    global STRIPE_WEBHOOK_SECRET
    WEBHOOK_SECRET = STRIPE_WEBHOOK_SECRET

    # ---- verification ------

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except ValueError as e:
        # Invalid payload (data format error)
        print("Webhook Error: Invalid payload")
        return "Invalid payload received.", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature(potential hacking attempt)
        print("Webhook Error: Invalid signature")
        return "Invalid signature.", 400
    except Exception as e:
        # general unexpected error
        print(f"webhook error: {e}")
        return "An error occurred.", 400

    # If the code reaches here, the message is 100% verified as coming from Stripe.
    print("Webhook verification successful.")

    # --- Process the event ---
    # Check Event Type for Successful Payment
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # --- ORDER FINALIZATION ---
        user_id = session["metadata"].get("user_id")

        # Extract item data we stored (e.g., item_1_id, item_1_qty, item_2_id, item_2_qty)
        item_data = {}
        for key, value in session["metadata"].items():
            if key.startswith("item_") and key.endswith("_id"):
                item_id = value
                # Construct the key for the quantity
                qty_key = key.replace("_id", "_qty")
                quantity = session["metadata"].get(qty_key)

                if item_id and quantity:
                    item_data[item_id] = float(quantity)

        # ----- Database Transaction -----
        conn = get_db_connection()
        try:
            conn.execute("BEGIN TRANSACTION;")

            for item_id_str, quantity in item_data.items():
                item_id = int(item_id_str)
                item = conn.execute(
                    "SELECT * FROM Items WHERE id = ?", (item_id,)
                ).fetchone()

                if item and item["weight"] >= quantity:
                    item_price = item["price_per_unit"] * quantity
                    ## Deduct Stock
                    new_weight = item["weight"] - quantity
                    conn.execute(
                        "UPDATE Items SET weight = ? WHERE id = ?",
                        (new_weight, item_id),
                    )

                    # create final order in the database
                    conn.execute(
                        "INSERT INTO Orders (u_id, item_id, quantity, price) VALUES (?, ?, ?, ?)",
                        (user_id, item_id, quantity, item_price),
                    )
                else:
                    print(
                        f"WARNING: Insufficient stock for item ID {item_id} or item not found. Order skipped for this item."
                    )

            conn.commit()  # Save all changes
        except Exception as e:
            conn.rollback()  # Rollback changes if any error occurs
            print(f"Database transaction failed: {e}")
            return "Database error", 500
        finally:
            conn.close()

    # We must respond to Stripe quickly, regardless of the outcome
    return "Success", 200
