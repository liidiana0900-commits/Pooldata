from flask import Flask, request, render_template_string
from datetime import date
import os

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pool Data</title>
    <style>
        body {
            font-family: Arial;
            background-color: #f2f2f2;
            padding: 40px;
        }
        .box {
            background: white;
            padding: 20px;
            max-width: 420px;
            margin: auto;
            border-radius: 8px;
        }
        h2 {
            text-align: center;
        }
        input, button {
            width: 100%;
            padding: 8px;
            margin-top: 10px;
        }
        .report {
            margin-top: 20px;
            background: #e8f5e9;
            padding: 10px;
            border-radius: 6px;
        }
    </style>
</head>
<body>
<div class="box">
    <h2>Pool Data</h2>

    <form method="post">
        <input type="text" name="client" placeholder="Client Name" required>
        <input type="number" step="0.01" name="balance" placeholder="Previous Balance" required>
        <button type="submit">Check Report</button>
    </form>

    {% if report %}
    <div class="report">
        <p><b>Client:</b> {{ client }}</p>
        <p><b>Date:</b> {{ today }}</p>
        <p><b>Daily Profit Rate:</b> {{ profit_rate }}%</p>
        <p><b>Profit Earned:</b> {{ earned }}</p>
        <p><b>New Balance:</b> {{ new_balance }}</p>
        <small>Note: Off-chain calculation, not on-chain verified.</small>
    </div>
    {% endif %}
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        client = request.form["client"]
        balance = float(request.form["balance"])
       # Auto profit percentage based on balance
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
    today=date.today(),
    earned=earned,
    new_balance=new_balance,
    profit_rate=profit_rate
)

    return render_template_string(HTML_PAGE, report=False)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


