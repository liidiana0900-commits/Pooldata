from flask import Flask, request
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "data.db"

ADMIN_PASSWORD = "admin123"
DAILY_RATE = 0.02
WITHDRAW_LIMIT = 30


# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            wallet TEXT PRIMARY KEY,
            balance REAL,
            profit REAL,
            last_date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


# ---------- HOME ----------
@app.route("/", methods=["GET", "POST"])
def index():
    msg = ""
    profit = 0

    if request.method == "POST":
        wallet = request.form["wallet"]
        balance = float(request.form["balance"])
        today = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT profit, last_date FROM users WHERE wallet=?", (wallet,))
        row = c.fetchone()

        if row:
            old_profit, last_date = row
            if last_date != today:
                new_profit = old_profit + (balance * DAILY_RATE)
            else:
                new_profit = old_profit
        else:
            new_profit = balance * DAILY_RATE

        c.execute("""
            INSERT OR REPLACE INTO users
            (wallet, balance, profit, last_date)
            VALUES (?, ?, ?, ?)
        """, (wallet, balance, new_profit, today))

        conn.commit()
        conn.close()

        profit = round(new_profit, 2)

        if profit < WITHDRAW_LIMIT: 30
            msg = f"⚠️ Your profit is {profit} USDT. You must reach {30} USDT to withdraw."
        else:
            msg = "✅ Withdrawal unlocked (demo only)."

    return f"""
    <html>
    <head>
        <title>Pooldata – Demo</title>
        <style>
            body {{ font-family: Arial; background:#f4f4f4; padding:40px; }}
            .box {{ background:white; padding:20px; width:400px; margin:auto; }}
            input, button {{ width:100%; padding:10px; margin:5px 0; }}
            .note {{ color:red; font-size:14px; }}
        </style>
    </head>
    <body>

    <div class="box">
        <h2>Pooldata (Demo Simulation)</h2>

        <p class="note">
        ⚠️ Please don't share your personal information to anyone its can't be refundable.
        </p>

        <form method="POST">
            <input name="wallet" placeholder="Wallet address" required>
            <input name="balance" placeholder="USDT balance" required>
            <button>Check Profit</button>
        </form>

        <h3>Profit: {profit} USDT</h3>
        <p>{msg}</p>
    </div>

    </body>
    </html>
    """


# ---------- ADMIN PANEL ----------
@app.route("/admin")
def admin():
    if request.args.get("password") != ADMIN_PASSWORD:
        return "Unauthorized"

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY profit DESC")
    rows = c.fetchall()
    conn.close()

    html = """
    <h2>Admin Panel (Demo)</h2>
    <table border=1 cellpadding=8>
    <tr>
        <th>Wallet</th>
        <th>Balance</th>
        <th>Profit</th>
        <th>Last Check</th>
    </tr>
    """

    for r in rows:
        html += f"""
        <tr>
            <td>{r[0]}</td>
            <td>{r[1]}</td>
            <td>{round(r[2],2)}</td>
            <td>{r[3]}</td>
        </tr>
        """

    html += "</table>"
    return html


if __name__ == "__main__":
    app.run(debug=True)
