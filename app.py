import os
import uuid
from datetime import datetime
from collections import defaultdict
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, jsonify, session
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ---------------- DB CONFIG ----------------
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres.cusbryojwnldabchhfkx:9788%40Srinithi@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres",
)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True, "pool_recycle": 300}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-change-me")

db = SQLAlchemy(app)


# ---------------- PERMISSIONS LIST ----------------
PERMISSION_GROUPS = [
    ("Colour Master", [
        ("colour_view","View"),("colour_add","Add"),
        ("colour_edit","Edit"),("colour_delete","Delete"),
    ]),
    ("Size Master", [
        ("size_view","View"),("size_add","Add"),
        ("size_edit","Edit"),("size_delete","Delete"),
    ]),
    ("Fabric Master", [
        ("fabric_view","View"),("fabric_add","Add"),
        ("fabric_edit","Edit"),("fabric_delete","Delete"),
    ]),
    ("Product Master", [
        ("product_view","View"),("product_add","Add"),
        ("product_edit","Edit"),("product_delete","Delete"),
    ]),
    ("Supplier Master", [
        ("supplier_view","View"),("supplier_add","Add"),
        ("supplier_edit","Edit"),("supplier_delete","Delete"),
    ]),
    ("Program Entry", [
        ("program_view","View"),("program_add","Add"),
        ("program_edit","Edit"),("program_delete","Delete"),
        ("program_status","Change Status / Proceed / Complete"),
    ]),
    ("Overall Programs", [
        ("overall_view","View"),("overall_status","Change Status"),
    ]),
    ("User Master", [
        ("user_view","View"),("user_add","Add"),
        ("user_edit","Edit"),("user_delete","Delete"),
    ]),
]
ALL_PERMISSIONS = [code for _, items in PERMISSION_GROUPS for code, _ in items]


# ---------------- MODELS ----------------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)
    permissions_csv = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw): self.password_hash = generate_password_hash(raw)
    def check_password(self, raw): return check_password_hash(self.password_hash, raw)

    @property
    def permissions(self):
        return [p for p in (self.permissions_csv or "").split(",") if p]
    @permissions.setter
    def permissions(self, values):
        self.permissions_csv = ",".join(values or [])

    def has(self, perm):
        if self.role == "admin": return True
        return perm in self.permissions


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
    def dia(self): return [x for x in (self.dia_csv or "").split(",") if x]
    @dia.setter
    def dia(self, values): self.dia_csv = ",".join(values or [])
    @property
    def colour(self): return [x for x in (self.colour_csv or "").split(",") if x]
    @colour.setter
    def colour(self, values): self.colour_csv = ",".join(values or [])


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
    def colors(self): return [x for x in (self.colors_csv or "").split(",") if x]
    @colors.setter
    def colors(self, values): self.colors_csv = ",".join(values or [])
    @property
    def sizes(self): return [x for x in (self.sizes_csv or "").split(",") if x]
    @sizes.setter
    def sizes(self, values): self.sizes_csv = ",".join(values or [])


class Supplier(db.Model):
    __tablename__ = "suppliers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(50), default="")
    contact = db.Column(db.String(120), default="")
    address = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


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
    status = db.Column(db.String(20), default="pending")  # pending / wip / completed
    supplier = db.Column(db.String(120), default="")
    lot_no = db.Column(db.String(50), default="")
    completed_date = db.Column(db.String(20), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class Counter(db.Model):
    __tablename__ = "counters"
    name = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Integer, default=0)


# ---------------- AUTH HELPERS ----------------
def current_user():
    uid = session.get("user_id")
    if not uid: return None
    return User.query.get(uid)

def login_required(view):
    @wraps(view)
    def wrapped(*a, **k):
        if not current_user(): return redirect("/")
        return view(*a, **k)
    return wrapped

def role_required(*roles):
    def deco(view):
        @wraps(view)
        def wrapped(*a, **k):
            u = current_user()
            if not u: return redirect("/")
            if u.role not in roles:
                return "Access denied.", 403
            return view(*a, **k)
        return wrapped
    return deco

def permission_required(perm):
    def deco(view):
        @wraps(view)
        def wrapped(*a, **k):
            u = current_user()
            if not u: return redirect("/")
            if not u.has(perm):
                return f"Access denied: missing permission '{perm}'.", 403
            return view(*a, **k)
        return wrapped
    return deco

@app.context_processor
def inject_user():
    return {"current_user": current_user()}


# ---------------- DICT HELPERS ----------------
def _to_dict_colour(c): return {"id":c.id,"name":c.name,"code":c.code}
def _to_dict_size(s):   return {"id":s.id,"name":s.name}
def _to_dict_fabric(f): return {"id":f.id,"name":f.name,"uom":f.uom,"gsm":f.gsm,"dia":f.dia,"colour":f.colour}
def _to_dict_product(p):
    return {"id":p.id,"name":p.name,"brand":p.brand,"category":p.category,
            "type":p.type,"fabric":p.fabric,"colors":p.colors,"sizes":p.sizes}
def _to_dict_supplier(s):
    return {"id":s.id,"name":s.name,"code":s.code,"contact":s.contact,
            "address":s.address,"created_at":s.created_at}

def _next_program_no():
    counter = Counter.query.get("program")
    if not counter:
        counter = Counter(name="program", value=0)
        db.session.add(counter)
    counter.value += 1
    db.session.commit()
    return f"PRG{counter.value:03d}"


def _grouped_programs():
    rows = (Program.query
            .order_by(Program.created_at.desc(), Program.program_no, Program.color)
            .all())
    groups = {}; order = []
    for r in rows:
        key = (r.program_no, r.color)
        if key not in groups:
            groups[key] = {
                "ids": [], "program_no": r.program_no, "date": r.date,
                "fabric": r.fabric, "dia": r.dia, "type": r.type,
                "product": r.product, "color": r.color,
                "sizes": [], "ratios": [], "rolls": r.rolls, "statuses": [],
                "supplier": r.supplier or "", "lot_no": r.lot_no or "",
                "completed_date": r.completed_date or "",
            }
            order.append(key)
        groups[key]["ids"].append(r.id)
        groups[key]["sizes"].append(str(r.size))
        groups[key]["ratios"].append(str(r.ratio))
        groups[key]["statuses"].append((r.status or "pending").lower())

    out = []
    for key in order:
        g = groups[key]
        sts = g["statuses"]
        if sts and all(s == "completed" for s in sts):
            status = "completed"
        elif any(s == "wip" for s in sts):
            status = "wip"
        elif any(s == "completed" for s in sts):
            status = "wip"   # mixed → still in progress
        else:
            status = "pending"
        out.append({
            "ids": ",".join(g["ids"]),
            "id": g["ids"][0],
            "program_no": g["program_no"],
            "date": g["date"], "fabric": g["fabric"], "dia": g["dia"],
            "type": g["type"], "product": g["product"], "color": g["color"],
            "size": ":".join(g["sizes"]),
            "ratio": ":".join(g["ratios"]),
            "rolls": g["rolls"], "status": status,
            "supplier": g["supplier"], "lot_no": g["lot_no"],
            "completed_date": g["completed_date"],
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
    session.clear(); return redirect("/")


# ---------------- USER MASTER ----------------
@app.route("/users")
@role_required("admin")
def users():
    return render_template("user_master.html",
        users=User.query.order_by(User.id).all(),
        permission_groups=PERMISSION_GROUPS)

@app.route("/users/new", methods=["GET", "POST"])
@role_required("admin")
def user_new():
    error = None
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        role = (request.form.get("role") or "user").strip().lower()
        if role not in ("admin","user"): role = "user"
        selected = [p for p in request.form.getlist("perms") if p in ALL_PERMISSIONS]
        if not username or not password:
            error = "Username and password are required."
        elif User.query.filter_by(username=username).first():
            error = f"Username '{username}' already exists."
        else:
            u = User(username=username, role=role)
            u.set_password(password)
            u.permissions = ALL_PERMISSIONS if role == "admin" else selected
            db.session.add(u); db.session.commit()
            return redirect("/users")
    return render_template("user_form.html", user=None, error=error,
                           permission_groups=PERMISSION_GROUPS,
                           all_permissions=ALL_PERMISSIONS)

@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_user(user_id):
    u = User.query.get_or_404(user_id); error = None
    if request.method == "POST":
        new_username = (request.form.get("username") or "").strip()
        new_password = request.form.get("password") or ""
        new_role = (request.form.get("role") or u.role).strip().lower()
        selected = [p for p in request.form.getlist("perms") if p in ALL_PERMISSIONS]
        if new_username and new_username != u.username:
            if User.query.filter_by(username=new_username).first():
                error = f"Username '{new_username}' already exists."
            else: u.username = new_username
        if not error and new_role in ("admin","user"):
            me = current_user()
            if me and me.id == u.id and new_role != "admin":
                error = "You can't change your own role from admin."
            else: u.role = new_role
        if not error and new_password: u.set_password(new_password)
        if not error:
            u.permissions = ALL_PERMISSIONS if u.role == "admin" else selected
            db.session.commit(); return redirect("/users")
    return render_template("user_form.html", user=u, error=error,
                           permission_groups=PERMISSION_GROUPS,
                           all_permissions=ALL_PERMISSIONS)

@app.route("/delete_user/<int:user_id>")
@role_required("admin")
def delete_user(user_id):
    me = current_user()
    if me and me.id == user_id: return "You cannot delete your own account.", 400
    u = User.query.get(user_id)
    if u: db.session.delete(u); db.session.commit()
    return redirect("/users")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ---------------- COLOUR ----------------
@app.route("/colour", methods=["GET", "POST"])
@login_required
def colour():
    u = current_user()
    if not u.has("colour_view"): return "Access denied.", 403
    search = request.args.get("search", "")
    if request.method == "POST":
        if not u.has("colour_add"): return "Access denied.", 403
        c = Colour(name=request.form["colour"], code=request.form["code"])
        db.session.add(c); db.session.commit()
        return redirect("/colour")
    q = Colour.query
    if search: q = q.filter(Colour.name.ilike(f"%{search}%"))
    return render_template("colour_master.html",
        colours=[_to_dict_colour(c) for c in q.order_by(Colour.id).all()])

@app.route("/delete_colour/<int:index>")
@permission_required("colour_delete")
def delete_colour(index):
    c = Colour.query.get(index)
    if c: db.session.delete(c); db.session.commit()
    return redirect("/colour")

@app.route("/edit_colour/<int:index>", methods=["GET", "POST"])
@permission_required("colour_edit")
def edit_colour(index):
    c = Colour.query.get_or_404(index)
    if request.method == "POST":
        c.name = request.form["colour"]; c.code = request.form["code"]
        db.session.commit(); return redirect("/colour")
    return render_template("edit_colour.html", colour=_to_dict_colour(c), index=c.id)


# ---------------- SIZE ----------------
@app.route("/size", methods=["GET", "POST"])
@login_required
def size():
    u = current_user()
    if not u.has("size_view"): return "Access denied.", 403
    search = request.args.get("search", "")
    if request.method == "POST":
        if not u.has("size_add"): return "Access denied.", 403
        s = Size(name=request.form["size"])
        db.session.add(s); db.session.commit()
        return redirect("/size")
    q = Size.query
    if search: q = q.filter(Size.name.ilike(f"%{search}%"))
    return render_template("size_master.html",
        sizes=[_to_dict_size(s) for s in q.order_by(Size.id).all()])

@app.route("/delete_size/<int:index>")
@permission_required("size_delete")
def delete_size(index):
    s = Size.query.get(index)
    if s: db.session.delete(s); db.session.commit()
    return redirect("/size")

@app.route("/edit_size/<int:index>", methods=["GET", "POST"])
@permission_required("size_edit")
def edit_size(index):
    s = Size.query.get_or_404(index)
    if request.method == "POST":
        s.name = request.form["size"]
        db.session.commit(); return redirect("/size")
    return render_template("edit_size.html", size=_to_dict_size(s), index=s.id)


# ---------------- FABRIC ----------------
@app.route("/fabric")
@permission_required("fabric_view")
def fabric():
    return render_template("fabric_master.html",
        fabrics=[_to_dict_fabric(f) for f in Fabric.query.order_by(Fabric.id).all()])

@app.route("/fabric/new", methods=["GET", "POST"])
@permission_required("fabric_add")
def fabric_new():
    if request.method == "POST":
        f = Fabric(name=request.form["name"],
                   uom=request.form.get("uom",""),
                   gsm=request.form.get("gsm",""))
        f.dia = [d.strip() for d in request.form.getlist("dia[]") if d.strip()]
        f.colour = [c.strip() for c in request.form.getlist("colour[]") if c.strip()]
        db.session.add(f); db.session.commit()
        return redirect("/fabric")
    return render_template("fabric_form.html", fabric=None,
        colours=[_to_dict_colour(c) for c in Colour.query.order_by(Colour.id).all()])

@app.route("/edit_fabric/<int:fid>", methods=["GET", "POST"])
@permission_required("fabric_edit")
def edit_fabric(fid):
    f = Fabric.query.get_or_404(fid)
    if request.method == "POST":
        f.name = request.form["name"]
        f.uom = request.form.get("uom","")
        f.gsm = request.form.get("gsm","")
        f.dia = [d.strip() for d in request.form.getlist("dia[]") if d.strip()]
        f.colour = [c.strip() for c in request.form.getlist("colour[]") if c.strip()]
        db.session.commit(); return redirect("/fabric")
    return render_template("fabric_form.html", fabric=_to_dict_fabric(f),
        colours=[_to_dict_colour(c) for c in Colour.query.order_by(Colour.id).all()])

@app.route("/delete_fabric/<int:fid>")
@permission_required("fabric_delete")
def delete_fabric(fid):
    f = Fabric.query.get(fid)
    if f: db.session.delete(f); db.session.commit()
    return redirect("/fabric")


# ---------------- PRODUCT ----------------
@app.route("/product")
@permission_required("product_view")
def product():
    search = request.args.get("search", "")
    q = Product.query
    if search: q = q.filter(Product.name.ilike(f"%{search}%"))
    return render_template("product_master.html",
        products=[_to_dict_product(p) for p in q.order_by(Product.id).all()])

@app.route("/product/new", methods=["GET", "POST"])
@permission_required("product_add")
def product_new():
    if request.method == "POST":
        p = Product(name=request.form["name"],
                    brand=request.form.get("brand",""),
                    category=request.form.get("category",""),
                    type=request.form.get("type",""),
                    fabric=request.form.get("fabric",""))
        p.colors = [c for c in request.form.getlist("colors[]") if c]
        p.sizes = [s for s in request.form.getlist("sizes[]") if s]
        db.session.add(p); db.session.commit()
        return redirect("/product")
    return render_template("product_form.html", product=None,
        fabrics=[_to_dict_fabric(f) for f in Fabric.query.order_by(Fabric.id).all()],
        colours=[_to_dict_colour(c) for c in Colour.query.order_by(Colour.id).all()],
        sizes=[_to_dict_size(s) for s in Size.query.order_by(Size.id).all()])

@app.route("/edit_product/<int:pid>", methods=["GET", "POST"])
@permission_required("product_edit")
def edit_product(pid):
    p = Product.query.get_or_404(pid)
    if request.method == "POST":
        p.name = request.form["name"]
        p.brand = request.form.get("brand","")
        p.category = request.form.get("category","")
        p.type = request.form.get("type","")
        p.fabric = request.form.get("fabric","")
        p.colors = [c for c in request.form.getlist("colors[]") if c]
        p.sizes = [s for s in request.form.getlist("sizes[]") if s]
        db.session.commit(); return redirect("/product")
    return render_template("product_form.html", product=_to_dict_product(p),
        fabrics=[_to_dict_fabric(f) for f in Fabric.query.order_by(Fabric.id).all()],
        colours=[_to_dict_colour(c) for c in Colour.query.order_by(Colour.id).all()],
        sizes=[_to_dict_size(s) for s in Size.query.order_by(Size.id).all()])

@app.route("/delete_product/<int:pid>")
@permission_required("product_delete")
def delete_product(pid):
    p = Product.query.get(pid)
    if p: db.session.delete(p); db.session.commit()
    return redirect("/product")

@app.route("/get-colors/<path:fabric>")
@login_required
def get_colors(fabric):
    f_name = fabric.split(" (")[0]
    f = Fabric.query.filter_by(name=f_name).first()
    if not f: return jsonify([])
    return jsonify(f.colour)


# ---------------- SUPPLIER MASTER ----------------
@app.route("/supplier", methods=["GET", "POST"])
@login_required
def supplier():
    u = current_user()
    if not u.has("supplier_view"): return "Access denied.", 403
    if request.method == "POST":
        if not u.has("supplier_add"): return "Access denied.", 403
        s = Supplier(
            name=(request.form.get("name") or "").strip(),
            code=(request.form.get("code") or "").strip(),
            contact=(request.form.get("contact") or "").strip(),
            address=(request.form.get("address") or "").strip(),
        )
        if s.name:
            db.session.add(s); db.session.commit()
        return redirect("/supplier")

    search = request.args.get("search", "").strip()
    contact = request.args.get("contact", "").strip()
    code = request.args.get("code", "").strip()
    q = Supplier.query
    if search: q = q.filter(Supplier.name.ilike(f"%{search}%"))
    if contact: q = q.filter(Supplier.contact.ilike(f"%{contact}%"))
    if code:    q = q.filter(Supplier.code.ilike(f"%{code}%"))
    suppliers = [_to_dict_supplier(s) for s in q.order_by(Supplier.id).all()]
    return render_template("supplier_master.html", suppliers=suppliers,
                           f_search=search, f_contact=contact, f_code=code)

@app.route("/edit_supplier/<int:sid>", methods=["GET", "POST"])
@permission_required("supplier_edit")
def edit_supplier(sid):
    s = Supplier.query.get_or_404(sid)
    if request.method == "POST":
        s.name = (request.form.get("name") or "").strip()
        s.code = (request.form.get("code") or "").strip()
        s.contact = (request.form.get("contact") or "").strip()
        s.address = (request.form.get("address") or "").strip()
        db.session.commit(); return redirect("/supplier")
    return render_template("supplier_form.html", supplier=_to_dict_supplier(s))

@app.route("/delete_supplier/<int:sid>")
@permission_required("supplier_delete")
def delete_supplier(sid):
    s = Supplier.query.get(sid)
    if s: db.session.delete(s); db.session.commit()
    return redirect("/supplier")


# ---------------- PROGRAM ----------------
@app.route("/program", methods=["GET", "POST"])
@login_required
def program():
    u = current_user()
    if not u.has("program_view"): return "Access denied.", 403

    if request.method == "POST":
        if not u.has("program_add"): return "Access denied.", 403
        program_no = _next_program_no()
        date_str = datetime.now().strftime("%d-%m-%Y")
        fabric = request.form.get("fabric","")
        dia = request.form.get("dia","")
        ptype = request.form.get("type","")
        product = request.form.get("product","")
        sizes  = request.form.getlist("sizes[]")
        ratios = request.form.getlist("ratios[]")
        colors = request.form.getlist("colors[]")
        rolls  = request.form.getlist("rolls[]")
        for ci, color in enumerate(colors):
            roll_val = rolls[ci] if ci < len(rolls) else ""
            for si, sz in enumerate(sizes):
                ratio_val = ratios[si] if si < len(ratios) else ""
                row = Program(
                    id=str(uuid.uuid4()), program_no=program_no, date=date_str,
                    fabric=fabric, dia=dia, type=ptype, product=product,
                    color=color, size=sz, ratio=ratio_val, rolls=roll_val,
                    status="pending",
                )
                db.session.add(row)
        db.session.commit()
        return redirect("/program")

    return render_template("program_entry.html",
        fabrics=[_to_dict_fabric(f) for f in Fabric.query.order_by(Fabric.id).all()],
        products=[_to_dict_product(p) for p in Product.query.order_by(Product.id).all()],
        programs=_grouped_programs())


@app.route("/program/<program_no>")
@login_required
def program_view(program_no):
    rows = Program.query.filter_by(program_no=program_no).all()
    if not rows: return "Program not found", 404
    header = {
        "program_no": rows[0].program_no, "date": rows[0].date,
        "fabric": rows[0].fabric, "dia": rows[0].dia,
        "product": rows[0].product,
        "supplier": rows[0].supplier or "",
        "lot_no": rows[0].lot_no or "",
        "status": (rows[0].status or "pending").lower(),
        "completed_date": rows[0].completed_date or "",
    }
    size_ratio = {}; colour_rolls = {}
    for r in rows:
        size_ratio.setdefault(r.size, r.ratio)
        colour_rolls.setdefault(r.color, r.rolls)
    mode = request.args.get("mode", "")
    suppliers = []
    if mode == "allocate":
        suppliers = [_to_dict_supplier(s) for s in Supplier.query.order_by(Supplier.name).all()]
    return render_template("program_view.html",
        header=header, size_ratio=size_ratio, colour_rolls=colour_rolls,
        mode=mode, suppliers=suppliers)


@app.route("/allocate_supplier", methods=["POST"])
@permission_required("program_status")
def allocate_supplier():
    program_no = request.form.get("program_no", "").strip()
    supplier_name = request.form.get("supplier", "").strip()
    if not program_no or not supplier_name:
        return "Program No and Supplier are required.", 400
    rows = Program.query.filter_by(program_no=program_no).all()
    if not rows: return "Program not found.", 404
    for r in rows:
        r.supplier = supplier_name
        r.status = "wip"
    db.session.commit()
    return redirect(f"/program/{program_no}/print")


@app.route("/program/<program_no>/print")
@login_required
def program_print(program_no):
    rows = Program.query.filter_by(program_no=program_no).all()
    if not rows: return "Program not found", 404
    header = {
        "program_no": rows[0].program_no, "date": rows[0].date,
        "fabric": rows[0].fabric, "dia": rows[0].dia,
        "product": rows[0].product,
        "supplier": rows[0].supplier or "",
        "status": (rows[0].status or "pending").lower(),
    }
    size_ratio = {}; colour_rolls = {}
    for r in rows:
        size_ratio.setdefault(r.size, r.ratio)
        colour_rolls.setdefault(r.color, r.rolls)
    return render_template("program_print.html",
        header=header, size_ratio=size_ratio, colour_rolls=colour_rolls)


@app.route("/cutting_completion", methods=["POST"])
@permission_required("program_status")
def cutting_completion():
    program_no = request.form.get("program_no", "").strip()
    lot_no = request.form.get("lot_no", "").strip()
    if not program_no or not lot_no:
        return "Program No and Lot No are required.", 400
    rows = Program.query.filter_by(program_no=program_no).all()
    if not rows: return "Program not found.", 404
    today = datetime.now().strftime("%d-%m-%Y")
    for r in rows:
        r.lot_no = lot_no
        r.status = "completed"
        r.completed_date = today
    db.session.commit()
    return redirect(request.referrer or "/overall_programs")


@app.route("/edit_program/<pids>", methods=["GET", "POST"])
@permission_required("program_edit")
def edit_program(pids):
    id_list = [i.strip() for i in pids.split(",") if i.strip()]
    rows = Program.query.filter(Program.id.in_(id_list)).all()
    if not rows:
        return "Program not found", 404
        
    rows_dict = {r.id: r for r in rows}
    ordered_rows = [rows_dict[i] for i in id_list if i in rows_dict]
    
    if request.method == "POST":
        new_status = (request.form.get("status") or ordered_rows[0].status or "pending").lower()
        if new_status not in ("pending","wip","completed"):
            new_status = "pending"
        new_rolls = request.form.get("rolls", ordered_rows[0].rolls)
        
        for r in ordered_rows:
            r.ratio = request.form.get(f"ratio_{r.id}", r.ratio)
            r.rolls = new_rolls
            r.status = new_status
        db.session.commit()
        return redirect("/program")
        
    return render_template("edit_program.html", rows=ordered_rows, p=ordered_rows[0])


@app.route("/edit_program_group", methods=["POST"])
@login_required
def edit_program_group():
    u = current_user()
    if not (u.has("program_status") or u.has("overall_status")):
        return "Access denied.", 403
    ids_csv = request.form.get("ids", "")
    new_status = (request.form.get("status") or "pending").lower()
    if new_status not in ("pending","wip","completed"):
        new_status = "pending"
    ids = [i for i in ids_csv.split(",") if i]
    if ids:
        Program.query.filter(Program.id.in_(ids)).update(
            {"status": new_status}, synchronize_session=False)
        db.session.commit()
    return redirect(request.referrer or "/overall_programs")


@app.route("/delete_program_group")
@permission_required("program_delete")
def delete_program_group():
    ids_csv = request.args.get("ids", "")
    ids = [i for i in ids_csv.split(",") if i]
    if ids:
        Program.query.filter(Program.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
    return redirect(request.referrer or "/program")


# ---------------- OVERALL PROGRAMS ----------------
@app.route("/overall_programs")
@permission_required("overall_view")
def overall_programs():
    return render_template("overall_programs.html", programs=_grouped_programs())


# ---------------- STARTUP MIGRATION + ADMIN SEED ----------------
def _safe_migrate():
    with db.engine.begin() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS permissions_csv TEXT DEFAULT ''"))
        conn.execute(text("ALTER TABLE programs ADD COLUMN IF NOT EXISTS supplier VARCHAR(120) DEFAULT ''"))
        conn.execute(text("ALTER TABLE programs ADD COLUMN IF NOT EXISTS lot_no VARCHAR(50) DEFAULT ''"))
        conn.execute(text("ALTER TABLE programs ADD COLUMN IF NOT EXISTS completed_date VARCHAR(20) DEFAULT ''"))

def _seed_admin():
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        admin.permissions = ALL_PERMISSIONS
        db.session.add(admin); db.session.commit()

with app.app_context():
    db.create_all()
    try: _safe_migrate()
    except Exception as e: print("Migration warning:", e)
    _seed_admin()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)