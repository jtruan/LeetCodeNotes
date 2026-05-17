import os

# --- API ---
TEQUILA_API_KEY = os.getenv("TEQUILA_API_KEY", "")
TEQUILA_BASE_URL = "https://api.tequila.kiwi.com/v2/search"

# --- Origin ---
ORIGIN = os.getenv("ORIGIN", "PIT")

# --- Search window ---
DAYS_FROM_NOW_MIN = int(os.getenv("DAYS_FROM_NOW_MIN", "7"))   # at least 7 days out
SEARCH_WINDOW_DAYS = int(os.getenv("SEARCH_WINDOW_DAYS", "90"))  # search next 3 months

# --- Trip types ---
# "oneway" | "round" | "both"
TRIP_TYPE = os.getenv("TRIP_TYPE", "both")

# Round-trip stay length (days)
ROUND_TRIP_MIN_STAY = int(os.getenv("ROUND_TRIP_MIN_STAY", "3"))
ROUND_TRIP_MAX_STAY = int(os.getenv("ROUND_TRIP_MAX_STAY", "7"))

# --- Price thresholds (USD) ---
MAX_PRICE_ROUND_TRIP = float(os.getenv("MAX_PRICE_ROUND_TRIP", "300"))
MAX_PRICE_ONE_WAY = float(os.getenv("MAX_PRICE_ONE_WAY", "150"))

# --- Duration filter ---
MAX_FLIGHT_HOURS = float(os.getenv("MAX_FLIGHT_HOURS", "24"))  # total travel time

# --- Destination filters ---
# Comma-separated IATA codes or country codes to exclude, e.g. "YYZ,CDG"
EXCLUDE_DESTINATIONS = [
    d.strip().upper()
    for d in os.getenv("EXCLUDE_DESTINATIONS", "").split(",")
    if d.strip()
]
# If set, only include these destinations (comma-separated IATA codes)
INCLUDE_DESTINATIONS = [
    d.strip().upper()
    for d in os.getenv("INCLUDE_DESTINATIONS", "").split(",")
    if d.strip()
]

# --- Email / notification ---
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "")          # recipient
SMTP_FROM = os.getenv("SMTP_FROM", "")                # sender Gmail address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")        # Gmail app password
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# --- Misc ---
MAX_RESULTS_PER_SEARCH = int(os.getenv("MAX_RESULTS_PER_SEARCH", "10"))
