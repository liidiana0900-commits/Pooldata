from flask import Flask, request, render_template_string
from datetime import date
import os

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pool Data - Profit Calculator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #eef2f7;
            padding: 40px;
        }
        .box {
            background: #ffffff;
            padding: 25px;
            max-width: 420px;
            margin: auto;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        img.profile {
            width: 110px;
            height: 110px;
            border-radius: 50%;
            margin-bottom: 15px;
        }
        input, button {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            font-size: 15px;
        }
        button {
            background: #2e7dff;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }
        button:hover {
            background: #1b5fd6;
        }
        .error {
            color: red;
            margin-top: 10px;
        }
        .report {
            margin-top: 20px;
            background: #f1f7ff;
            padding: 15px;
            border-radius: 8px;
            text-align: left;
        }
        small {
            color: #666;
        }
    </style>
</head>
<body>

<div class="box">

    <!-- PROFILE / LOGO IMAGE -->
    <img class="profile"
         src="https://images.unsplash.com/photo-1642790106117-e829e14a8cbb?auto=format&fit=crop&w=300&q=80"
         alt="Pool Data Logo">

    <h2>Pool Data</h2>
    <p><small>Daily Profit Calculator (Minning Pool Data)</small></p>

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
        <p><b>Wallet Address:</b> {{ wallet }}</p>
        <p><b>Wallet Balance:</b> {{ balance }} USDT</p>
        <p><b>Daily Profit Rate:</b> {{ profit_rate }}%</p>
        <p><b>Daily Profit:</b> {{ earned }} USDT</p>
        <p><b>New Balance:</b> {{ new_balance }} USDT</p>
    </div>
    {% endif %}

    <br>
    <small>
        ⚠️ Profit shown is an estimation based on Wallet balance.<br>
        Do not share your wallet passwords to any one.
    </small>

</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        client = request.form["client"]
        wallet = request.form["wallet"]
        balance = float(request.form["balance"])

        if balance <= 0:
            return render_template_string(
                HTML_PAGE,
                error="Please check your wallet balance. Balance cannot be 0."
            )

        if balance < 5000:
            profit_rate = 2
        elif balance <= 10000:
            profit_rate = 2.5
        else:
            profit_rate = 3

        earned = round(balance * profit_rate / 100, 2)
        new_balance = round(balance + earned, 2)

        return render_template_string(
            HTML_PAGE,
            report=True,
            client=client,
            wallet=wallet,
            today=date.today(),
            balance=balance,
            profit_rate=profit_rate,
            earned=earned,
            new_balance=new_balance
        )

    return render_template_string(HTML_PAGE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


