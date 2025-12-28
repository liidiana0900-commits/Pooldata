from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mining Pool Data Calculator</title>
    <style>
        body { font-family: Arial; background:#f5f5f5; padding:40px; }
        .box { background:#fff; padding:30px; max-width:600px; margin:auto; border-radius:8px; }
        h1 { text-align:center; }
        input { width:100%; padding:10px; margin:8px 0; }
        button { padding:12px; width:100%; background:#007bff; color:white; border:none; font-size:16px; }
        .result { margin-top:20px; background:#eef; padding:15px; border-radius:6px; }
        footer { text-align:center; margin-top:30px; font-size:12px; color:#666; }
    </style>
</head>
<body>
<div class="box">
    <h1>Mining Pool Data Calculator</h1>

    <form method="post">
        <label>Hashrate (TH/s)</label>
        <input type="number" step="any" name="hashrate" required>

        <label>Power Usage (Watts)</label>
        <input type="number" step="any" name="power" required>

        <label>Electricity Cost ($/kWh)</label>
        <input type="number" step="any" name="electricity" required>

        <label>Block Reward (Coins)</label>
        <input type="number" step="any" name="reward" required>

        <label>Coin Price ($)</label>
        <input type="number" step="any" name="price" required>

        <label>Pool Fee (%)</label>
        <input type="number" step="any" name="fee" required>

        <button type="submit">Calculate</button>
    </form>

    {% if result %}
    <div class="result">
        <h3>Results (Estimated)</h3>
        <p><b>Daily Revenue:</b> ${{ result.revenue }}</p>
        <p><b>Electricity Cost:</b> ${{ result.electricity_cost }}</p>
        <p><b>Pool Fee:</b> ${{ result.pool_fee }}</p>
        <p><b>Net Daily Profit:</b> ${{ result.profit }}</p>
    </div>
    {% endif %}
</div>

<footer>
    This calculator is for educational and estimation purposes only.
</footer>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        hashrate = float(request.form["hashrate"])
        power = float(request.form["power"])
        electricity = float(request.form["electricity"])
        reward = float(request.form["reward"])
        price = float(request.form["price"])
        fee = float(request.form["fee"])

        # Simplified estimation formula
        daily_coins = hashrate * 0.00000001 * reward
        revenue = daily_coins * price

        electricity_cost = (power / 1000) * 24 * electricity
        pool_fee = revenue * (fee / 100)

        profit = revenue - electricity_cost - pool_fee

        result = {
            "revenue": round(revenue, 2),
            "electricity_cost": round(electricity_cost, 2),
            "pool_fee": round(pool_fee, 2),
            "profit": round(profit, 2)
        }

    return render_template_string(HTML_TEMPLATE, result=result)

if name == "__main__":
    app.run(debug=True)
