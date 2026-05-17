# LeetCodeNotes

### Solutions and Notes of LeetCode Problems


| # | Title | Solution | Difficulty |
|---| ----- | -------- | ---------- |
|1|[Two Sum](https://leetcode.com/problems/two-sum/) |[Python](TwoSum.py)|Easy|
|2|[Add Two Numbers](https://leetcode.com/problems/add-two-numbers/) |[Python](AddTwoNumbers.py)|Medium|

---

## Flight Deal Alert System

Automatically searches for cheap flights departing from Pittsburgh (PIT) using the [Kiwi.com Tequila API](https://tequila.kiwi.com/) and sends an HTML email alert when deals are found.

### Files

| File | Purpose |
|------|---------|
| `main.py` | Search logic, filtering, console summary |
| `config.py` | All thresholds and settings (env-var driven) |
| `notifier.py` | Gmail SMTP email sender |
| `requirements.txt` | Python dependencies |
| `.github/workflows/daily_check.yml` | GitHub Actions schedule |

---

### Quick Start (local)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set required environment variables
export TEQUILA_API_KEY="your_kiwi_api_key"
export NOTIFY_EMAIL="you@example.com"
export SMTP_FROM="sender@gmail.com"
export SMTP_PASSWORD="gmail_app_password"

# 3. Run
python main.py
```

---

### Getting a Kiwi / Tequila API Key

1. Go to <https://tequila.kiwi.com/> and click **Sign up**.
2. Create an account and log in to the [Tequila portal](https://partners.kiwi.com/).
3. Under **My APIs**, create a new API and select the **Search** endpoint (free tier is sufficient).
4. Copy the **API key** shown on the API detail page.

---

### Gmail App Password

Gmail requires an **app password** (not your regular password) when using SMTP:

1. Enable **2-Step Verification** on your Google account (<https://myaccount.google.com/security>).
2. Go to **Security → App passwords**.
3. Generate a password for "Mail / Other (custom name)".
4. Use that 16-character password as `SMTP_PASSWORD`.

---

### GitHub Actions Setup

All sensitive values are stored as **GitHub Secrets** and optional tunables as **Repository Variables**.

#### Required Secrets (`Settings → Secrets → Actions`)

| Secret | Value |
|--------|-------|
| `TEQUILA_API_KEY` | Your Kiwi/Tequila API key |
| `NOTIFY_EMAIL` | Email address to receive alerts |
| `SMTP_FROM` | Gmail address used to send alerts |
| `SMTP_PASSWORD` | Gmail app password |

#### Optional Repository Variables (`Settings → Variables → Actions`)

Set these to override the defaults from `config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `ORIGIN` | `PIT` | IATA code of departure airport |
| `MAX_PRICE_ROUND_TRIP` | `300` | Max USD for round-trip deals |
| `MAX_PRICE_ONE_WAY` | `150` | Max USD for one-way deals |
| `MAX_FLIGHT_HOURS` | `24` | Max total travel time (hours) |
| `DAYS_FROM_NOW_MIN` | `7` | Earliest departure (days from today) |
| `SEARCH_WINDOW_DAYS` | `90` | How far ahead to search (days) |
| `TRIP_TYPE` | `both` | `round`, `oneway`, or `both` |
| `EXCLUDE_DESTINATIONS` | *(empty)* | Comma-separated IATA codes to skip |
| `INCLUDE_DESTINATIONS` | *(empty)* | Comma-separated IATA codes to allow only |

#### Manual trigger

After pushing, go to **Actions → Daily Flight Deal Check → Run workflow** to test immediately without waiting for the 08:00 UTC schedule.

---

### Customising Thresholds Locally

Override any setting with an environment variable:

```bash
# Only look for round trips under $200, max 10 hours, at least 14 days out
export MAX_PRICE_ROUND_TRIP=200
export TRIP_TYPE=round
export MAX_FLIGHT_HOURS=10
export DAYS_FROM_NOW_MIN=14
python main.py
```

Or export a `.env` file and source it:

```bash
source .env && python main.py
```

---

### Sample Console Output

```
=======================================================================
  3 DEAL(S) FOUND FROM PIT
=======================================================================
Destination              Type     Depart       Return       Price    Hrs
-----------------------------------------------------------------------
Cancun (CUN), Mexico     round    2026-06-10   2026-06-17   $248    14.5h
Orlando (MCO), Florida   round    2026-06-22   2026-06-29   $189     2.8h
Chicago (ORD), Illinois  oneway   2026-07-04   N/A          $89      1.6h
=======================================================================
```
