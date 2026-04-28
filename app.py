import os
import uuid
from datetime import datetime
from collections import defaultdict
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, jsonify, session
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ---------------- DB CONFIG ----------------
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres.cusbryojwnldabchhfkx:9788%40Srinithi@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres",
)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-change-me")

db = SQLAlchemy(app)


# ---------------- MODELS ----------------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)


class Colour(db.Model):
    __tablename__ = "colours"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(50), nullable=False)


class Size(db.Model):
    __tablename__ = "sizes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class Fabric(db.Model):
    __tablename__ = "fabrics"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    uom = db.Column(db.String(50), nullable=False)
    gsm = db.Column(db.String(50), nullable=False)
    dia_csv = db.Column(db.Text, default="")
    colour_csv = db.Column(db.Text, default="")

    @property
    def dia(self):
        return [x for x in (self.dia_csv or "").split(",") if x]

    @dia.setter
    def dia(self, values):
        self.dia_csv = ",".join(values or [])

    @property
    def colour(self):
        return [x for x in (self.colour_csv or "").split(",") if x]

    @colour.setter
    def colour(self, values):
        self.colour_csv = ",".join(values or [])


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    brand = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(120), nullable=False)
    fabric = db.Column(db.String(120), nullable=False)
    colors_csv = db.Column(db.Text, default="")
    sizes_csv = db.Column(db.Text, default="")

    @property
    def colors(self):
        return [x for x in (self.colors_csv or "").split(",") if x]

    @colors.setter
    def colors(self, values):
        self.colors_csv = ",".join(values or [])

    @property
    def sizes(self):
        return [x for x in (self.sizes_csv or "").split(",") if x]

    @sizes.setter
    def sizes(self, values):
        self.sizes_csv = ",".join(values or [])


class Program(db.Model):
    __tablename__ = "programs"
    id = db.Column(db.String(64), primary_key=True)
    program_no = db.Column(db.String(20), nullable=False, index=True)
    date = db.Column(db.String(20), nullable=False)
    fabric = db.Column(db.String(120), nullable=False)
    dia = db.Column(db.String(50))
    type = db.Column(db.String(120))
    product = db.Column(db.String(120), nullable=False)
    color = db.Column(db.String(120), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    ratio = db.Column(db.String(50), nullable=False)
    rolls = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class Counter(db.Model):
    __tablename__ = "counters"
    name = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Integer, default=0)


# ---------------- AUTH HELPERS ----------------
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            return redirect("/")
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            u = current_user()
            if not u:
                return redirect("/")
            if u.role not in roles:
                return "Access denied: you don't have permission for this page.", 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


@app.context_processor
def inject_user():
    """Make `current_user` available inside every template."""
    return {"current_user": current_user()}


# ---------------- DICT HELPERS ----------------
def _to_dict_colour(c):
    return {"id": c.id, "name": c.name, "code": c.code}


def _to_dict_size(s):
    return {"id": s.id, "name": s.name}


def _to_dict_fabric(f):
    return {
        "id": f.id, "name": f.name, "uom": f.uom, "gsm": f.gsm,
        "dia": f.dia, "colour": f.colour,
    }


def _to_dict_product(p):
    return {
        "id": p.id, "name": p.name, "brand": p.brand, "category": p.category,
        "type": p.type, "fabric": p.fabric, "colors": p.colors, "sizes": p.sizes,
    }


def _next_program_no():
    counter = Counter.query.get("program")
    if not counter:
        counter = Counter(name="program", value=0)
        db.session.add(counter)
    counter.value += 1
    db.session.commit()
    return f"PRG{counter.value:03d}"


def _grouped_programs():
    rows = (
        Program.query
        .order_by(Program.created_at.desc(), Program.program_no, Program.color)
        .all()
    )

    groups = {}
    order = []
    for r in rows:
        key = (r.program_no, r.color)
        if key not in groups:
            groups[key] = {
                "ids": [], "program_no": r.program_no, "date": r.date,
                "fabric": r.fabric, "dia": r.dia, "type": r.type,
                "product": r.product, "color": r.color,
                "sizes": [], "ratios": [], "rolls": r.rolls, "statuses": [],
            }
            order.append(key)
        groups[key]["ids"].append(r.id)
        groups[key]["sizes"].append(str(r.size))
        groups[key]["ratios"].append(str(r.ratio))
        groups[key]["statuses"].append((r.status or "pending").lower())

    out = []
    for key in order:
        g = groups[key]
        all_completed = g["statuses"] and all(s == "completed" for s in g["statuses"])
        out.append({
            "ids": ",".join(g["ids"]),
            "id": g["ids"][0],
            "program_no": g["program_no"],
            "date": g["date"],
            "fabric": g["fabric"],
            "dia": g["dia"],
            "type": g["type"],
            "product": g["product"],
            "color": g["color"],
            "size": ":".join(g["sizes"]),
            "ratio": ":".join(g["ratios"]),
            "rolls": g["rolls"],
            "status": "completed" if all_completed else "pending",
        })
    return out


# ---------------- LOGIN / LOGOUT ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u_name = (request.form.get("username") or "").strip()
        p = request.form.get("password") or ""
        user = User.query.filter_by(username=u_name).first()
        if user and user.check_password(p):
            session.clear()
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            return redirect("/dashboard")
        error = "Invalid username or password"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- USER MASTER (admin only) ----------------
@app.route("/users")
@role_required("admin")
def users():
    all_users = User.query.order_by(User.id).all()
    return render_template("user_master.html", users=all_users)


@app.route("/users/new", methods=["GET", "POST"])
@role_required("admin")
def user_new():
    error = None
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        role = (request.form.get("role") or "user").strip().lower()
        if role not in ("admin", "user"):
            role = "user"
        if not username or not password:
            error = "Username and password are required."
        elif User.query.filter_by(username=username).first():
            error = f"Username '{username}' already exists."
        else:
            u = User(username=username, role=role)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            return redirect("/users")
    return render_template("user_form.html", user=None, error=error)


@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_user(user_id):
    u = User.query.get_or_404(user_id)
    error = None
    if request.method == "POST":
        new_username = (request.form.get("username") or "").strip()
        new_password = request.form.get("password") or ""
        new_role = (request.form.get("role") or u.role).strip().lower()

        if new_username and new_username != u.username:
            if User.query.filter_by(username=new_username).first():
                error = f"Username '{new_username}' already exists."
            else:
                u.username = new_username

        if not error:
            if new_role in ("admin", "user"):
                # Don't allow demoting yourself out of admin (lock-out safety)
                me = current_user()
                if me and me.id == u.id and new_role != "admin":
                    error = "You can't change your own role from admin."
                else:
                    u.role = new_role

        if not error and new_password:
            u.set_password(new_password)

        if not error:
            db.session.commit()
            return redirect("/users")

    return render_template("user_form.html", user=u, error=error)


@app.route("/delete_user/<int:user_id>")
@role_required("admin")
def delete_user(user_id):
    me = current_user()
    if me and me.id == user_id:
        return "You cannot delete your own account.", 400
    u = User.query.get(user_id)
    if u:
        db.session.delete(u)
        db.session.commit()
    return redirect("/users")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ---------------- COLOUR (admin only) ----------------
@app.route("/colour", methods=["GET", "POST"])
@role_required("admin")
def colour():
    search = request.args.get("search", "")
    if request.method == "POST":
        c = Colour(name=request.form["colour"], code=request.form["code"])
        db.session.add(c)
        db.session.commit()
        return redirect("/colour")
    query = Colour.query
    if search:
        query = query.filter(Colour.name.ilike(f"%{search}%"))
    colours = [_to_dict_colour(c) for c in query.order_by(Colour.id).all()]
    return render_template("colour_master.html", colours=colours)


@app.route("/delete_colour/<int:index>")
@role_required("admin")
def delete_colour(index):
    c = Colour.query.get(index)
    if c:
        db.session.delete(c)
        db.session.commit()
    return redirect("/colour")


@app.route("/edit_colour/<int:index>", methods=["GET", "POST"])
@role_required("admin")
def edit_colour(index):
    c = Colour.query.get_or_404(index)
    if request.method == "POST":
        c.name = request.form["colour"]
        c.code = request.form["code"]
        db.session.commit()
        return redirect("/colour")
    return render_template("edit_colour.html", colour=_to_dict_colour(c), index=c.id)


# ---------------- SIZE (admin only) ----------------
@app.route("/size", methods=["GET", "POST"])
@role_required("admin")
def size():
    search = request.args.get("search", "")
    if request.method == "POST":
        s = Size(name=request.form["size"])
        db.session.add(s)
        db.session.commit()
        return redirect("/size")
    query = Size.query
    if search:
        query = query.filter(Size.name.ilike(f"%{search}%"))
    sizes = [_to_dict_size(s) for s in query.order_by(Size.id).all()]
    return render_template("size_master.html", sizes=sizes)


@app.route("/delete_size/<int:index>")
@role_required("admin")
def delete_size(index):
    s = Size.query.get(index)
    if s:
        db.session.delete(s)
        db.session.commit()
    return redirect("/size")


@app.route("/edit_size/<int:index>", methods=["GET", "POST"])
@role_required("admin")
def edit_size(index):
    s = Size.query.get_or_404(index)
    if request.method == "POST":
        s.name = request.form["size"]
        db.session.commit()
        return redirect("/size")
    return render_template("edit_size.html", size=_to_dict_size(s), index=s.id)


# ---------------- FABRIC MASTER (admin only) ----------------
@app.route("/fabric")
@role_required("admin")
def fabric_list():
    fabrics = [_to_dict_fabric(f) for f in Fabric.query.order_by(Fabric.id).all()]
    return render_template("fabric_master.html", fabrics=fabrics)


@app.route("/fabric/new", methods=["GET", "POST"])
@role_required("admin")
def fabric_new():
    if request.method == "POST":
        f = Fabric(
            name=request.form["name"],
            uom=request.form["uom"],
            gsm=request.form["gsm"],
        )
        f.dia = request.form.getlist("dia[]")
        f.colour = request.form.getlist("colour[]")
        db.session.add(f)
        db.session.commit()
        return redirect("/fabric")
    colours = [_to_dict_colour(c) for c in Colour.query.order_by(Colour.id).all()]
    return render_template("fabric_form.html", colours=colours)


@app.route("/get-colors/<fabric_value>")
@login_required
def get_colors(fabric_value):
    fabric_value = fabric_value.strip()
    for f in Fabric.query.all():
        full_name = f"{f.name.strip()} ({str(f.gsm).strip()})"
        if full_name == fabric_value:
            return jsonify(f.colour)
    return jsonify([])


@app.route("/edit_fabric/<int:index>", methods=["GET", "POST"])
@role_required("admin")
def edit_fabric(index):
    f = Fabric.query.get_or_404(index)
    if request.method == "POST":
        f.name = request.form["name"]
        f.uom = request.form["uom"]
        f.gsm = request.form["gsm"]
        f.dia = request.form.getlist("dia[]")
        f.colour = request.form.getlist("colour[]")
        db.session.commit()
        return redirect("/fabric")
    colours = [_to_dict_colour(c) for c in Colour.query.order_by(Colour.id).all()]
    return render_template(
        "fabric_form.html", fabric=_to_dict_fabric(f), colours=colours
    )


@app.route("/delete_fabric/<int:index>")
@role_required("admin")
def delete_fabric(index):
    f = Fabric.query.get(index)
    if f:
        db.session.delete(f)
        db.session.commit()
    return redirect("/fabric")


# ---------------- PRODUCT MASTER (admin only) ----------------
@app.route("/product")
@role_required("admin")
def product_list():
    search = request.args.get("search", "")
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    products = [_to_dict_product(p) for p in query.order_by(Product.id).all()]
    return render_template("product_master.html", products=products)


@app.route("/product/new", methods=["GET", "POST"])
@role_required("admin")
def product_new():
    if request.method == "POST":
        p = Product(
            name=request.form["name"],
            brand=request.form["brand"],
            category=request.form["category"],
            type=request.form["type"],
            fabric=request.form["fabric"],
        )
        p.colors = [c for c in request.form.getlist("colors[]") if c]
        p.sizes = [s for s in request.form.getlist("sizes[]") if s]
        db.session.add(p)
        db.session.commit()
        return redirect("/product")
    return render_template(
        "product_form.html",
        colours=[_to_dict_colour(c) for c in Colour.query.order_by(Colour.id).all()],
        sizes=[_to_dict_size(s) for s in Size.query.order_by(Size.id).all()],
        fabrics=[_to_dict_fabric(f) for f in Fabric.query.order_by(Fabric.id).all()],
    )


@app.route("/edit_product/<int:index>", methods=["GET", "POST"])
@role_required("admin")
def edit_product(index):
    p = Product.query.get_or_404(index)
    if request.method == "POST":
        p.name = request.form["name"]
        p.brand = request.form["brand"]
        p.category = request.form["category"]
        p.type = request.form["type"]
        p.fabric = request.form["fabric"]
        p.colors = [c for c in request.form.getlist("colors[]") if c]
        p.sizes = [s for s in request.form.getlist("sizes[]") if s]
        db.session.commit()
        return redirect("/product")
    return render_template(
        "product_form.html",
        product=_to_dict_product(p),
        colours=[_to_dict_colour(c) for c in Colour.query.order_by(Colour.id).all()],
        sizes=[_to_dict_size(s) for s in Size.query.order_by(Size.id).all()],
        fabrics=[_to_dict_fabric(f) for f in Fabric.query.order_by(Fabric.id).all()],
    )


@app.route("/delete_product/<int:index>")
@role_required("admin")
def delete_product(index):
    p = Product.query.get(index)
    if p:
        db.session.delete(p)
        db.session.commit()
    return redirect("/product")


# ---------------- PROGRAM ENTRY ----------------
@app.route("/program", methods=["GET", "POST"])
@login_required
def program():
    if request.method == "POST":
        fabric = request.form.get("fabric")
        dia = request.form.get("dia")
        type_ = request.form.get("type")
        product = request.form.get("product")

        sizes_in = request.form.getlist("sizes[]")
        ratios = request.form.getlist("ratios[]")
        colors = request.form.getlist("colors[]")
        rolls = request.form.getlist("rolls[]")

        if not fabric or not product:
            return "Fabric & Product required!"
        if len(sizes_in) != len(ratios):
            return "Size & Ratio mismatch!"
        if len(colors) != len(rolls):
            return "Color & Rolls mismatch!"

        program_no = _next_program_no()
        today = datetime.now().strftime("%d-%m-%Y")

        for i in range(len(colors)):
            for j in range(len(sizes_in)):
                row = Program(
                    id=str(uuid.uuid4()),
                    program_no=program_no,
                    date=today,
                    fabric=fabric,
                    dia=dia,
                    type=type_,
                    product=product,
                    color=colors[i],
                    size=sizes_in[j],
                    ratio=ratios[j],
                    rolls=rolls[i],
                    status="pending",
                )
                db.session.add(row)
        db.session.commit()
        return redirect("/program")

    fabrics = [_to_dict_fabric(f) for f in Fabric.query.order_by(Fabric.id).all()]
    products = [_to_dict_product(p) for p in Product.query.order_by(Product.id).all()]
    programs = _grouped_programs()
    return render_template(
        "program_entry.html", fabrics=fabrics, products=products, programs=programs
    )


@app.route("/program/<program_no>")
@login_required
def view_program(program_no):
    data = Program.query.filter_by(program_no=program_no).all()
    if not data:
        return "No Data Found"
    first = data[0]
    header = {
        "program_no": first.program_no, "date": first.date, "fabric": first.fabric,
        "dia": first.dia, "type": first.type, "product": first.product,
    }
    size_ratio = {row.size: row.ratio for row in data}
    colour_rolls = defaultdict(int)
    for row in data:
        try:
            colour_rolls[row.color] += int(row.rolls)
        except (TypeError, ValueError):
            pass
    return render_template(
        "program_view.html",
        header=header, size_ratio=size_ratio, colour_rolls=colour_rolls,
    )


@app.route("/delete_program/<id>")
@role_required("admin")
def delete_program(id):
    row = Program.query.get(id)
    if row:
        db.session.delete(row)
        db.session.commit()
    return redirect("/program")


@app.route("/delete_program_group")
@role_required("admin")
def delete_program_group():
    ids_csv = request.args.get("ids", "")
    ids = [i for i in ids_csv.split(",") if i]
    for pid in ids:
        row = Program.query.get(pid)
        if row:
            db.session.delete(row)
    db.session.commit()
    return redirect("/program")


@app.route("/edit_program/<id>", methods=["GET", "POST"])
@role_required("admin")
def edit_program(id):
    row = Program.query.get(id)
    if not row:
        return "Not Found", 404

    if request.method == "POST":
        if "ratio" in request.form:
            row.ratio = request.form.get("ratio", row.ratio)
        if "rolls" in request.form:
            row.rolls = request.form.get("rolls", row.rolls)
        if "status" in request.form:
            new_status = (request.form.get("status") or "").strip().lower()
            if new_status in ("pending", "completed"):
                row.status = new_status
        db.session.commit()
        referer = request.headers.get("Referer", "")
        if "/overall_programs" in referer:
            return redirect("/overall_programs")
        return redirect("/program")

    p = {
        "id": row.id, "program_no": row.program_no, "date": row.date,
        "fabric": row.fabric, "dia": row.dia, "type": row.type,
        "product": row.product, "color": row.color, "size": row.size,
        "ratio": row.ratio, "rolls": row.rolls, "status": row.status,
    }
    return render_template("edit_program.html", p=p)


@app.route("/edit_program_group", methods=["POST"])
@login_required
def edit_program_group():
    """Bulk status update — allowed for any logged-in user (daily workflow)."""
    ids_csv = request.form.get("ids", "")
    new_status = (request.form.get("status") or "").strip().lower()
    if new_status not in ("pending", "completed"):
        return "Invalid status", 400
    ids = [i for i in ids_csv.split(",") if i]
    for pid in ids:
        row = Program.query.get(pid)
        if row:
            row.status = new_status
    db.session.commit()
    return redirect("/overall_programs")


@app.route("/overall_programs")
@login_required
def overall_programs():
    programs = _grouped_programs()
    return render_template("overall_programs.html", programs=programs)


# ---------------- BOOTSTRAP ----------------
with app.app_context():
    db.create_all()
    # Seed a default admin if no users exist
    if User.query.count() == 0:
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print(">>> Default admin created: username=admin  password=admin123")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)