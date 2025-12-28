from flask import Flask, request, render_template_string, redirect, url_for
import re
import datetime
import os

app = Flask(__name__)

# Simple in-memory wallet registry (demo)
REGISTERED_WALLETS = {}

# Admin password (change this)
ADMIN_PASSWORD = "admin123"

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
    <title>Pooldata - Daily Profit</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
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
def index():
    error = None
    profit = None
    wallet = None

    if request.method == "POST":
        wallet = request.form.get("wallet", "").strip()

        if not wallet:
            error = "Please provide a wallet address."
        elif not ETH_WALLET_REGEX.match(wallet):
            error = "Invalid wallet address format."
        else:
            ip = request.remote_addr
            log_visitor(wallet, ip)

            # Register wallet if first time
            if ip not in REGISTERED_WALLETS:
                REGISTERED_WALLETS[ip] = wallet
            else:
                if REGISTERED_WALLETS[ip] != wallet:
                    error = "You must use the same wallet address as registered."
                    return render_template_string(HTML_TEMPLATE, error=error)

            # Demo profit logic
            profit = round((int(wallet[-4:], 16) % 500) / 10, 2)

    return render_template_string(
        HTML_TEMPLATE,
        error=error,
        profit=profit,
        wallet=wallet
    )


@app.route("/admin")
def admin():
    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return "Unauthorized", 401

    if not os.path.exists(VISITOR_LOG):
        return "No visitors yet."

    with open(VISITOR_LOG) as f:
        logs = f.read().replace("\n", "<br>")

    return f"<h2>Visitor Log</h2><hr>{logs}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
