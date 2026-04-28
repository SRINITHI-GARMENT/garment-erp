import os
import uuid
from datetime import datetime
from collections import defaultdict

from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ---------------- DB CONFIG ----------------
# IMPORTANT: set DATABASE_URL in Render -> Environment, do NOT hardcode credentials.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///app.db",  # local fallback
)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret")

db = SQLAlchemy(app)

USER = {"admin": "1234"}


# ---------------- MODELS ----------------
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


# ---------------- HELPERS ----------------
def _to_dict_colour(c):
    return {"id": c.id, "name": c.name, "code": c.code}


def _to_dict_size(s):
    return {"id": s.id, "name": s.name}


def _to_dict_fabric(f):
    return {
        "id": f.id,
        "name": f.name,
        "uom": f.uom,
        "gsm": f.gsm,
        "dia": f.dia,
        "colour": f.colour,
    }


def _to_dict_product(p):
    return {
        "id": p.id,
        "name": p.name,
        "brand": p.brand,
        "category": p.category,
        "type": p.type,
        "fabric": p.fabric,
        "colors": p.colors,
        "sizes": p.sizes,
    }


def _next_program_no():
    counter = Counter.query.get("program")
    if not counter:
        counter = Counter(name="program", value=0)
        db.session.add(counter)
    counter.value += 1
    db.session.commit()
    return f"PRG{counter.value:03d}"


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u in USER and USER[u] == p:
            return redirect("/dashboard")
        else:
            error = "Invalid Login"
    return render_template("login.html", error=error)


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ---------------- COLOUR ----------------
@app.route("/colour", methods=["GET", "POST"])
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
def delete_colour(index):
    c = Colour.query.get(index)
    if c:
        db.session.delete(c)
        db.session.commit()
    return redirect("/colour")


@app.route("/edit_colour/<int:index>", methods=["GET", "POST"])
def edit_colour(index):
    c = Colour.query.get_or_404(index)
    if request.method == "POST":
        c.name = request.form["colour"]
        c.code = request.form["code"]
        db.session.commit()
        return redirect("/colour")
    return render_template("edit_colour.html", colour=_to_dict_colour(c), index=c.id)


# ---------------- SIZE ----------------
@app.route("/size", methods=["GET", "POST"])
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
def delete_size(index):
    s = Size.query.get(index)
    if s:
        db.session.delete(s)
        db.session.commit()
    return redirect("/size")


@app.route("/edit_size/<int:index>", methods=["GET", "POST"])
def edit_size(index):
    s = Size.query.get_or_404(index)
    if request.method == "POST":
        s.name = request.form["size"]
        db.session.commit()
        return redirect("/size")
    return render_template("edit_size.html", size=_to_dict_size(s), index=s.id)


# ---------------- FABRIC MASTER ----------------
@app.route("/fabric")
def fabric_list():
    fabrics = [_to_dict_fabric(f) for f in Fabric.query.order_by(Fabric.id).all()]
    return render_template("fabric_master.html", fabrics=fabrics)


@app.route("/fabric/new", methods=["GET", "POST"])
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
def get_colors(fabric_value):
    fabric_value = fabric_value.strip()
    for f in Fabric.query.all():
        full_name = f"{f.name.strip()} ({str(f.gsm).strip()})"
        if full_name == fabric_value:
            return jsonify(f.colour)
    return jsonify([])


@app.route("/edit_fabric/<int:index>", methods=["GET", "POST"])
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
def delete_fabric(index):
    f = Fabric.query.get(index)
    if f:
        db.session.delete(f)
        db.session.commit()
    return redirect("/fabric")


# ---------------- PRODUCT MASTER ----------------
@app.route("/product")
def product_list():
    search = request.args.get("search", "")
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    products = [_to_dict_product(p) for p in query.order_by(Product.id).all()]
    return render_template("product_master.html", products=products)


@app.route("/product/new", methods=["GET", "POST"])
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
def delete_product(index):
    p = Product.query.get(index)
    if p:
        db.session.delete(p)
        db.session.commit()
    return redirect("/product")


# ---------------- PROGRAM ENTRY ----------------
@app.route("/program", methods=["GET", "POST"])
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
    programs = [
        {
            "id": p.id,
            "program_no": p.program_no,
            "date": p.date,
            "fabric": p.fabric,
            "dia": p.dia,
            "type": p.type,
            "product": p.product,
            "color": p.color,
            "size": p.size,
            "ratio": p.ratio,
            "rolls": p.rolls,
            "status": p.status,
        }
        for p in Program.query.order_by(Program.created_at.desc()).all()
    ]
    return render_template(
        "program_entry.html", fabrics=fabrics, products=products, programs=programs
    )


@app.route("/program/<program_no>")
def view_program(program_no):
    data = Program.query.filter_by(program_no=program_no).all()
    if not data:
        return "No Data Found"

    first = data[0]
    header = {
        "program_no": first.program_no,
        "date": first.date,
        "fabric": first.fabric,
        "dia": first.dia,
        "type": first.type,
        "product": first.product,
    }

    size_ratio = {}
    for row in data:
        size_ratio[row.size] = row.ratio

    colour_rolls = defaultdict(int)
    for row in data:
        try:
            colour_rolls[row.color] += int(row.rolls)
        except (TypeError, ValueError):
            pass

    return render_template(
        "program_view.html",
        header=header,
        size_ratio=size_ratio,
        colour_rolls=colour_rolls,
    )


@app.route("/delete_program/<id>")
def delete_program(id):
    row = Program.query.get(id)
    if row:
        db.session.delete(row)
        db.session.commit()
    return redirect("/program")


# ---------------- EDIT PROGRAM (FIXED) ----------------
# The inline status dropdown on overall_programs.html only sends `status`.
# The full edit form on edit_program.html sends `ratio`, `rolls`, and `status`.
# Use .get() with defaults so both work, and only update fields that were sent.
@app.route("/edit_program/<id>", methods=["GET", "POST"])
def edit_program(id):
    row = Program.query.get(id)
    if not row:
        return "Not Found", 404

    if request.method == "POST":
        # Only update fields that were actually submitted
        if "ratio" in request.form:
            row.ratio = request.form.get("ratio", row.ratio)
        if "rolls" in request.form:
            row.rolls = request.form.get("rolls", row.rolls)
        if "status" in request.form:
            new_status = (request.form.get("status") or "").strip().lower()
            if new_status in ("pending", "completed"):
                row.status = new_status

        db.session.commit()

        # If the request came from the overall list (inline dropdown),
        # send the user back there instead of the program entry page.
        referer = request.headers.get("Referer", "")
        if "/overall_programs" in referer:
            return redirect("/overall_programs")
        return redirect("/program")

    p = {
        "id": row.id,
        "program_no": row.program_no,
        "date": row.date,
        "fabric": row.fabric,
        "dia": row.dia,
        "type": row.type,
        "product": row.product,
        "color": row.color,
        "size": row.size,
        "ratio": row.ratio,
        "rolls": row.rolls,
        "status": row.status,
    }
    return render_template("edit_program.html", p=p)


@app.route("/overall_programs")
def overall_programs():
    programs = [
        {
            "id": p.id,
            "program_no": p.program_no,
            "date": p.date,
            "fabric": p.fabric,
            "dia": p.dia,
            "type": p.type,
            "product": p.product,
            "color": p.color,
            "size": p.size,
            "ratio": p.ratio,
            "rolls": p.rolls,
            "status": p.status,
        }
        for p in Program.query.order_by(Program.created_at.desc()).all()
    ]
    return render_template("overall_programs.html", programs=programs)


@app.route("/logout")
def logout():
    return redirect("/")


# ---------------- BOOTSTRAP ----------------
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)