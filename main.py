"""
Flight deal alert system — searches Kiwi.com Tequila API for cheap flights
departing from PIT and sends an email when deals are found.
"""

import logging
import sys
from datetime import date, timedelta

import requests

import config
import notifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _headers() -> dict:
    if not config.TEQUILA_API_KEY:
        raise RuntimeError("TEQUILA_API_KEY is not set.")
    return {"apikey": config.TEQUILA_API_KEY}


def _date_str(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def _search(fly_from: str, date_from: date, date_to: date, trip_type: str) -> list[dict]:
    """Call the Tequila /v2/search endpoint and return raw result items."""
    params = {
        "fly_from": fly_from,
        "fly_to": "anywhere",
        "date_from": _date_str(date_from),
        "date_to": _date_str(date_to),
        "curr": "USD",
        "limit": config.MAX_RESULTS_PER_SEARCH,
        "sort": "price",
        "asc": 1,
        "one_per_city": 1,
    }

    if trip_type == "round":
        params["flight_type"] = "round"
        params["nights_in_dst_from"] = config.ROUND_TRIP_MIN_STAY
        params["nights_in_dst_to"] = config.ROUND_TRIP_MAX_STAY
    else:
        params["flight_type"] = "oneway"

    try:
        resp = requests.get(
            config.TEQUILA_BASE_URL,
            headers=_headers(),
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])
    except requests.RequestException as exc:
        logger.error("API request failed (%s %s): %s", trip_type, date_from, exc)
        return []


# ---------------------------------------------------------------------------
# Filtering & normalisation
# ---------------------------------------------------------------------------

def _duration_hours(flight: dict) -> float:
    """Total travel time in hours (fly_duration field is in seconds)."""
    return flight.get("fly_duration", 0) / 3600


def _booking_link(flight: dict) -> str:
    return flight.get("deep_link", "https://www.kiwi.com")


def _normalise(flight: dict, trip_type: str) -> dict:
    local_depart = flight.get("local_departure", "")[:10]
    local_arrival = flight.get("local_arrival", "")[:10]

    # For round trips the API returns the return date separately
    return_date = None
    if trip_type == "round":
        # The last route segment's local_arrival is the return
        routes = flight.get("route", [])
        if routes:
            return_date = routes[-1].get("local_arrival", "")[:10]

    return {
        "destination": flight.get("flyTo", ""),
        "destination_city": flight.get("cityTo", ""),
        "country": flight.get("countryTo", {}).get("name", ""),
        "depart": local_depart,
        "return": return_date,
        "price": flight.get("price", 0),
        "duration_hours": _duration_hours(flight),
        "trip_type": trip_type,
        "booking_link": _booking_link(flight),
    }


def _is_deal(flight: dict, trip_type: str) -> bool:
    price = flight.get("price", float("inf"))
    destination = flight.get("flyTo", "").upper()

    # Destination include/exclude filters
    if config.INCLUDE_DESTINATIONS and destination not in config.INCLUDE_DESTINATIONS:
        return False
    if destination in config.EXCLUDE_DESTINATIONS:
        return False

    # Duration filter
    if _duration_hours(flight) > config.MAX_FLIGHT_HOURS:
        return False

    # Price threshold
    threshold = config.MAX_PRICE_ROUND_TRIP if trip_type == "round" else config.MAX_PRICE_ONE_WAY
    return price <= threshold


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def find_deals() -> list[dict]:
    today = date.today()
    date_from = today + timedelta(days=config.DAYS_FROM_NOW_MIN)
    date_to = today + timedelta(days=config.SEARCH_WINDOW_DAYS)

    trip_types = (
        ["round", "oneway"] if config.TRIP_TYPE == "both"
        else [config.TRIP_TYPE]
    )

    deals: list[dict] = []
    seen: set[tuple] = set()  # deduplicate by (destination, depart, type)

    for trip_type in trip_types:
        logger.info("Searching %s trips from %s (%s → %s)...", trip_type, config.ORIGIN, date_from, date_to)
        results = _search(config.ORIGIN, date_from, date_to, trip_type)
        logger.info("  API returned %d result(s).", len(results))

        for flight in results:
            if not _is_deal(flight, trip_type):
                continue
            norm = _normalise(flight, trip_type)
            key = (norm["destination"], norm["depart"], trip_type)
            if key in seen:
                continue
            seen.add(key)
            deals.append(norm)

    deals.sort(key=lambda d: d["price"])
    return deals


def print_summary(deals: list[dict]) -> None:
    if not deals:
        print("\nNo deals found matching your criteria.\n")
        return

    print(f"\n{'='*70}")
    print(f"  {len(deals)} DEAL(S) FOUND FROM {config.ORIGIN}")
    print(f"{'='*70}")
    header = f"{'Destination':<28} {'Type':<8} {'Depart':<12} {'Return':<12} {'Price':>8} {'Hrs':>6}"
    print(header)
    print("-" * 70)
    for d in deals:
        print(
            f"{d['destination_city']} ({d['destination']}), {d['country']:<10}"[:28].ljust(28),
            f"{d['trip_type']:<8}",
            f"{d['depart']:<12}",
            f"{d['return'] or 'N/A':<12}",
            f"${d['price']:<7.0f}",
            f"{d['duration_hours']:>5.1f}h",
        )
    print(f"{'='*70}\n")


def main() -> None:
    logger.info("Flight deal search starting. Origin: %s", config.ORIGIN)
    deals = find_deals()
    print_summary(deals)

    if deals:
        logger.info("Sending notification for %d deal(s)...", len(deals))
        notifier.send_deals(deals)
    else:
        logger.info("No deals found — no email sent.")

    logger.info("Done.")


if __name__ == "__main__":
    main()
