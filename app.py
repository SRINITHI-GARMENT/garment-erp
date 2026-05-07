from flask import Flask, render_template, request, redirect
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# 🔴 REPLACE WITH YOUR NEON CONNECTION STRING
DATABASE_URL = "postgresql://neondb_owner:npg_BHQFbufE1a8h@ep-late-dew-apjmndh7.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Create DB engine
engine = create_engine(DATABASE_URL)

actual_df = None

# ───────── LOAD BASE DATA ─────────
def load_base():
    try:
        df = pd.read_sql("SELECT * FROM stock", engine)

        if df.empty:
            return pd.DataFrame(
                columns=["ebo", "product", "color", "size", "base_qty"]
            )

        df["base_qty"] = pd.to_numeric(
            df["base_qty"],
            errors="coerce"
        ).fillna(0)

        return df

    except Exception as e:
        print("DB Error:", e)

        return pd.DataFrame(
            columns=["ebo", "product", "color", "size", "base_qty"]
        )

# ───────── DASHBOARD ─────────
@app.route('/')
def dashboard():

    df = load_base()

    total_actual_qty = None
    if actual_df is not None:
        total_actual_qty = int(actual_df["actual_qty"].sum())

    return render_template(
        "dashboard.html",
        total_ebos=df["ebo"].nunique(),
        total_products=df["product"].nunique(),
        total_base_qty=int(df["base_qty"].sum()),
        total_actual_qty=total_actual_qty
    )

# ───────── UPLOAD BASE STOCK ─────────
@app.route('/upload-base', methods=['POST'])
def upload_base():

    file = request.files['file']

    df = pd.read_excel(file)

    # Clean columns
    df.columns = [c.lower().strip() for c in df.columns]

    # Rename if needed
    df = df.rename(columns={
        "actual_qty": "base_qty"
    })

    # Keep only required columns
    df = df[[
        "ebo",
        "product",
        "color",
        "size",
        "base_qty"
    ]]

    # Remove old data
    with engine.begin() as conn:
        conn.exec_driver_sql("DELETE FROM stock")

    # Upload new data
    df.to_sql(
        "stock",
        engine,
        if_exists="append",
        index=False
    )

    return redirect('/base-stock')

# ───────── BASE PAGE ─────────
@app.route('/base-stock')
def base():

    df = load_base()

    return render_template(
        "base_stock.html",
        data=df.to_dict("records")
    )

# ───────── UPLOAD ACTUAL STOCK ─────────
@app.route('/upload-actual', methods=['POST'])
def upload_actual():

    global actual_df

    file = request.files['file']

    actual_df = pd.read_excel(file)

    actual_df.columns = [
        c.lower().strip()
        for c in actual_df.columns
    ]

    actual_df = actual_df.rename(columns={
        "actual qty": "actual_qty"
    })

    return redirect('/ebo-report')

# ───────── EBO REPORT ─────────
@app.route('/ebo-report')
def ebo():

    global actual_df

    df = load_base()

    if actual_df is None:
        return render_template(
            "ebo_report.html",
            data=[]
        )

    merged = df.merge(
        actual_df,
        on=["ebo", "product", "color", "size"],
        how="left"
    )

    merged["actual_qty"] = merged["actual_qty"].fillna(0)

    merged["required"] = (
        merged["base_qty"] -
        merged["actual_qty"]
    )

    return render_template(
        "ebo_report.html",
        data=merged.to_dict("records")
    )

# ───────── PRODUCT REPORT ─────────
@app.route('/product-report')
def product():

    global actual_df

    df = load_base()

    if actual_df is None:
        return render_template(
            "product_report.html",
            data=[]
        )

    merged = df.merge(
        actual_df,
        on=["ebo", "product", "color", "size"],
        how="left"
    )

    merged["actual_qty"] = merged["actual_qty"].fillna(0)

    merged["required"] = (
        merged["base_qty"] -
        merged["actual_qty"]
    )

    return render_template(
        "product_report.html",
        data=merged.to_dict("records")
    )

# ───────── EXCESS REPORT ─────────
@app.route('/excess-stock')
def excess():

    global actual_df

    df = load_base()

    if actual_df is None:
        return render_template(
            "excess_stock.html",
            data=[]
        )

    merged = df.merge(
        actual_df,
        on=["ebo", "product", "color", "size"],
        how="left"
    )

    merged["actual_qty"] = merged["actual_qty"].fillna(0)

    merged["excess_qty"] = (
        merged["actual_qty"] -
        merged["base_qty"]
    )

    result = merged[
        merged["excess_qty"] > 0
    ]

    return render_template(
        "excess_stock.html",
        data=result.to_dict("records")
    )

# ───────── RUN APP ─────────
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )