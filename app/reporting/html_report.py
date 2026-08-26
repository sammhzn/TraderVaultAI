from datetime import datetime


class HTMLReport:

    def generate(self, report):

        html = f"""
<!DOCTYPE html>

<html>

<head>

<title>TraderVaultAI Backtest</title>

<style>

body {{
    font-family: Arial;
    background:#f3f3f3;
    padding:40px;
}}

.card {{
    background:white;
    padding:30px;
    border-radius:10px;
    width:700px;
    margin:auto;
}}

table {{
    width:100%;
    border-collapse:collapse;
}}

td {{
    padding:10px;
    border-bottom:1px solid #ddd;
}}

h1 {{
    color:#2b2b2b;
}}

</style>

</head>

<body>

<div class="card">

<h1>TraderVaultAI Backtest Report</h1>

<table>

<tr><td>Total Trades</td><td>{report.total_trades}</td></tr>
<tr><td>Wins</td><td>{report.wins}</td></tr>
<tr><td>Losses</td><td>{report.losses}</td></tr>
<tr><td>Win Rate</td><td>{report.win_rate}%</td></tr>

<tr><td>Gross Profit</td><td>{report.gross_profit}</td></tr>
<tr><td>Gross Loss</td><td>{report.gross_loss}</td></tr>
<tr><td>Net Profit</td><td>{report.net_profit}</td></tr>
<tr><td>Profit Factor</td><td>{report.profit_factor}</td></tr>

</table>

<p>
Generated:
{datetime.now()}
</p>

</div>

</body>

</html>
"""

        with open("backtest_report.html", "w", encoding="utf-8") as f:
            f.write(html)

        return "backtest_report.html"