from flask import Flask, request, render_template_string
from datetime import date, datetime
import os
import re

app = Flask(__name__)

# ================== CONFIG ==================
ADMIN_PASSWORD = "admin123"   # CHANGE THIS
# ============================================

# ================== STORAGE ==================
CLIENT_WALLETS = {}     # client -> wallet
VISIT_LOGS = []         # admin logs
# ============================================

# ================== HTML ==================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pool Data</title>
    <style>
        body { font-family: Arial; background:#eef2f7; padding:40px; }
        .box { background:#fff; padding:25px; max-width:450px; margin:auto;
               border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1); text-align:center; }
        img { width:110px; height:110px; border-radius:50%; margin-bottom:15px; }
        input, button { width:100%; padding:10px; margin-top:10px; }
        button { background:#2e7dff; color:white; border:none; border-radius:5px; }
        .error { color:red; margin-top:10px; }
        .report { margin-top:20px; background:#f1f7ff; padding:15px; border-radius:8px; text-align:left; }
        small { color:#666; }
    </style>
</head>
<body>

<div class="box">

<img src="https://images.unsplash.com/photo-1642790106117-e829e14a8cbb?auto=format&fit=crop&w=300&q=80">

<h2>Pool Data</h2>
<small>Daily Profit Calculator (Demo)</small>

<form method="post">
    <input type="text" name="client" placeholder="Client Name" required>
    <input type="text" name="wallet" placeholder="Wallet Address" required>
    <input type="number" step="0.01" name="balance" placeholder="Wallet Balance (USDT)" required>
    <button type="submit">Check Profit</button>
</form>

{% if error %}
<p class="error"><b>{{ error }}</b></p>
{% endif %}

{% if report %}
<div class="report">
<p><b>Date:</b> {{ today }}</p>
<p><b>Client:</b> {{ client }}</p>
<p><b>Wallet:</b> {{ wallet }}</p>
<p><b>Balance:</b> {{ balance }} USDT</p>
<p><b>Profit Rate:</b> {{ profit_rate }}%</p>
<p><b>Daily Profit:</b> {{ earned }} USDT</p>
<p><b>New Balance:</b> {{ new_balance }} USDT</p>
</div>
{% endif %}

<br>
<small>Wallet locked on first use • Demo only</small>

</div>
</body>
</html>
"""

ADMIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin - Pool Data</title>
    <style>
        body { font-family: Arial; background:#f4f6f8; padding:30px; }
        table { border-collapse: collapse; width:100%; background:white; }
        th, td { border:1px solid #ccc; padding:8px; font-size:14px; }
        th { background:#2e7dff; color:white; }
        h2 { text-align:center; }
    </style>
</head>
<body>

<h2>Admin Panel – Client Activity</h2>

<table>
<tr>
<th>#</th>
<th>Date & Time</th>
<th>Client</th>
<th>Wallet</th>
<th>Balance</th>
<th>Profit %</th>
<th>Profit</th>
</tr>

{% for log in logs %}
<tr>
<td>{{ loop.index }}</td>
<td>{{ log.time }}</td>
<td>{{ log.client }}</td>
<td>{{ log.wallet }}</td>
<td>{{ log.balance }}</td>
<td>{{ log.rate }}</td>
<td>{{ log.profit }}</td>
</tr>
{% endfor %}

</table>

</body>
</html>
"""
# ============================================

def is_valid_wallet(wallet):
    return bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", wallet))

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        client = request.form["client"].strip()
        wallet = request.form["wallet"].strip()
        balance = float(request.form["balance"])

        if not is_valid_wallet(wallet):
            return render_template_string(HTML_PAGE, error="Invalid wallet address")

        if client in CLIENT_WALLETS and CLIENT_WALLETS[client] != wallet:
            return render_template_string(HTML_PAGE, error="Client already linked to another wallet")

        CLIENT_WALLETS.setdefault(client, wallet)

        if balance <= 0:
            return render_template_string(HTML_PAGE, error="Balance must be greater than 130")

        if balance < 5000:
            rate = 2
        elif balance <= 10000:
            rate = 2.5
            else:
            rate = 3

        profit = round(balance * rate / 100, 2)
        new_balance = round(balance + profit, 2)

        VISIT_LOGS.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "client": client,
            "wallet": wallet,
            "balance": balance,
            "rate": rate,
            "profit": profit
        })

        return render_template_string(
            HTML_PAGE,
            report=True,
            today=date.today(),
            client=client,
            wallet=wallet,
            balance=balance,
            profit_rate=rate,
            earned=profit,
            new_balance=new_balance
        )

    return render_template_string(HTML_PAGE)

@app.route("/admin")
def admin():
    password = request.args.get("password")
    if password != ADMIN_PASSWORD:
        return "Unauthorized", 401

    return render_template_string(ADMIN_PAGE, logs=VISIT_LOGS)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
