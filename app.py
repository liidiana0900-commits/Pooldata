from flask import Flask, request
import sqlite3, time

app = Flask(__name__)
DB = "pool.db"

DAILY_RATE = 0.02
ADMIN_PASSWORD = "admin123"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            wallet TEXT PRIMARY KEY,
            name TEXT,
            nationality TEXT,
            balance REAL,
            start_time INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- PROFIT ----------
def calculate_profit(balance, start_time):
    seconds = time.time() - start_time
    daily_profit = balance * DAILY_RATE
    per_second = daily_profit / 86400
    return round(seconds * per_second, 4)

# ---------- HOME ----------
@app.route("/", methods=["GET", "POST"])
def home():
    result = ""

    if request.method == "POST":
        name = request.form["name"]
        nationality = request.form["nationality"]
        wallet = request.form["wallet"]
        balance = float(request.form["balance"])

        if not wallet.startswith("0x") or len(wallet) != 42:
            result = "<p style='color:red'>Invalid wallet address</p>"
        else:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("SELECT start_time FROM users WHERE wallet=?", (wallet,))
            row = c.fetchone()

            if row:
                start_time = row[0]
            else:
                start_time = int(time.time())
                c.execute("""
                    INSERT INTO users (wallet, name, nationality, balance, start_time)
                    VALUES (?, ?, ?, ?, ?)
                """, (wallet, name, nationality, balance, start_time))
                conn.commit()

            profit = calculate_profit(balance, start_time)
            conn.close()

            note = ""
            if profit < 30:
                note = "<p style='color:red'>⚠️ You must reach 30 USDT profit to withdraw.</p>"

            result = f"""
                <h3>Live Profit: {profit} USDT</h3>
                {note}
                <p style="font-size:12px;color:#777;">
                Profit is calculated based on user-provided balance.
                </p>
            """

    return f"""
    <html>
    <head>
        <title>Pool Data</title>
        <style>
            body {{ font-family: Arial; background:#f4f4f4; }}
            .box {{ width:420px; margin:60px auto; background:white; padding:20px; }}
            input, select, button {{ width:100%; padding:10px; margin:6px 0; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Pool Profit Checker</h2>
            <form method="POST">
                <input name="name" placeholder="Full Name" required>
                <select name="nationality" required>
                    <option value="">Select Nationality</option>
                    <option>USA</option>
                    <option>UK</option>
                    <option>India</option>
                    <option>Pakistan</option>
                    <option>UAE</option>
                    <option>Other</option>
                </select>
                <input name="wallet" placeholder="ERC20 Wallet Address" required>
                <input name="balance" placeholder="USDT Balance" required>
                <button>Check Profit</button>
            </form>
            {result}
        </div>
    </body>
    </html>
    """

# ---------- ADMIN ----------
@app.route("/admin")
def admin():
    if request.args.get("password") != ADMIN_PASSWORD:
        return "Unauthorized"

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()

    html = "<h2>Admin Panel</h2><table border=1 cellpadding=6>"
    html += "<tr><th>Name</th><th>Nationality</th><th>Wallet</th><th>Balance</th><th>Live Profit</th></tr>"

    for u in users:
        profit = calculate_profit(u[3], u[4])
html += f"<tr><td>{u[1]}</td><td>{u[2]}</td><td>{u[0]}</td><td>{u[3]}</td><td>{profit}</td></tr>"

    html += "</table>"
    return html

if __name__ == "__main__":
    app.run(debug=True)
