import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import config

logger = logging.getLogger(__name__)


def _build_html(deals: list[dict]) -> str:
    rows = ""
    for d in deals:
        rows += f"""
        <tr>
            <td>{d['destination_city']} ({d['destination']})</td>
            <td>{d['country']}</td>
            <td>{d['depart']}</td>
            <td>{d['return'] or '—'}</td>
            <td>${d['price']:.0f}</td>
            <td>{d['duration_hours']:.1f} h</td>
            <td>{d['trip_type'].capitalize()}</td>
            <td><a href="{d['booking_link']}">Book now</a></td>
        </tr>"""

    return f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
  h2 {{ color: #2c3e50; }}
  table {{ border-collapse: collapse; width: 100%; background: #fff; }}
  th {{ background: #2980b9; color: #fff; padding: 10px 14px; text-align: left; }}
  td {{ padding: 9px 14px; border-bottom: 1px solid #e0e0e0; }}
  tr:hover td {{ background: #eaf4fb; }}
  a {{ color: #2980b9; font-weight: bold; text-decoration: none; }}
</style>
</head>
<body>
<h2>✈ Flight Deals from {config.ORIGIN} — {datetime.utcnow().strftime('%Y-%m-%d')}</h2>
<p>Found <strong>{len(deals)}</strong> deal(s) matching your criteria.</p>
<table>
  <tr>
    <th>Destination</th>
    <th>Country</th>
    <th>Depart</th>
    <th>Return</th>
    <th>Price (USD)</th>
    <th>Duration</th>
    <th>Type</th>
    <th>Link</th>
  </tr>
  {rows}
</table>
<p style="color:#888;font-size:12px;">Prices are approximate and subject to change. Always verify before booking.</p>
</body>
</html>"""


def _build_text(deals: list[dict]) -> str:
    lines = [
        f"Flight Deals from {config.ORIGIN} — {datetime.utcnow().strftime('%Y-%m-%d')}",
        f"Found {len(deals)} deal(s).\n",
    ]
    for d in deals:
        lines.append(
            f"{d['destination_city']} ({d['destination']}, {d['country']})\n"
            f"  Type     : {d['trip_type'].capitalize()}\n"
            f"  Depart   : {d['depart']}\n"
            f"  Return   : {d['return'] or 'N/A'}\n"
            f"  Price    : ${d['price']:.0f}\n"
            f"  Duration : {d['duration_hours']:.1f} h\n"
            f"  Book     : {d['booking_link']}\n"
        )
    return "\n".join(lines)


def send_deals(deals: list[dict]) -> None:
    if not deals:
        logger.info("No deals to send.")
        return

    if not all([config.NOTIFY_EMAIL, config.SMTP_FROM, config.SMTP_PASSWORD]):
        logger.warning(
            "Email credentials not configured (NOTIFY_EMAIL / SMTP_FROM / SMTP_PASSWORD). "
            "Skipping notification."
        )
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"✈ {len(deals)} Flight Deal(s) from {config.ORIGIN}!"
    msg["From"] = config.SMTP_FROM
    msg["To"] = config.NOTIFY_EMAIL

    msg.attach(MIMEText(_build_text(deals), "plain"))
    msg.attach(MIMEText(_build_html(deals), "html"))

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(config.SMTP_FROM, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_FROM, config.NOTIFY_EMAIL, msg.as_string())
        logger.info("Alert email sent to %s.", config.NOTIFY_EMAIL)
    except Exception as exc:
        logger.error("Failed to send email: %s", exc)
        raise
