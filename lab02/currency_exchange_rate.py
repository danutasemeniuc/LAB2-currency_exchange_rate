import os
import sys
import json
import requests
from enum import Enum
from datetime import datetime, date as _date

# ---------------- ENUM pentru monede ----------------
class Currency(Enum):
    MDL = "MDL"
    USD = "USD"
    EUR = "EUR"
    RON = "RON"
    RUS = "RUS"
    UAH = "UAH"

def is_known_currency(currency: str) -> bool:
    try:
        Currency(currency)
        return True
    except ValueError:
        return False


# ---------------- Convertor ----------------
class Convertor:
    def __init__(self, exchangeRates: list[dict]):
        self.exchangeRates = exchangeRates

    def exchange(self, from_currency: Currency, to_currency: Currency, date: datetime = datetime.today()) -> float:
        date_str = date.strftime("%Y-%m-%d")
        rate = self.exchangeRates[-1]  # fallback ultima intrare

        for exchangeRate in self.exchangeRates:
            if exchangeRate["date"] == date_str:
                rate = exchangeRate
                break

        rate["mdl"] = 1.0  # MDL fix

        from_key = from_currency.name.lower()
        to_key = to_currency.name.lower()

        if from_key not in rate or to_key not in rate:
            raise ValueError(f"Unknown currency {from_currency} or {to_currency}")

        return rate[to_key] / rate[from_key]


# ---------------- Directoare proiect ----------------
BASE_URL = "https://api.exchangerate.host"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(BASE_DIR, "error.log")


# ---------------- Utilitare ----------------
def log_error(message: str) -> None:
    """Scrie erorile într-un fișier error.log"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")


def validate_date(date_str: str) -> bool:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return False
    earliest = _date(2025, 1, 1)
    latest = _date(2025, 9, 15)
    return earliest <= dt <= latest


def fetch_exchange_rate(base_currency: str, target_currency: str, date_str: str):
    """Preia cursul de la API-ul public"""
    url = f"{BASE_URL}/{date_str}"
    params = {"base": base_currency, "symbols": target_currency}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        msg = f"API request failed: {e}"
        log_error(msg)
        print(f"[ERROR] {msg}")
        return None


def save_data_to_file(data: dict, base_currency: str, target_currency: str, date_str: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    filename = f"{base_currency}_{target_currency}_{date_str}.json"
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return filepath


def print_usage_and_exit():
    print("Usage: python currency_exchange_rate.py <BASE> <TARGET> <DATE(YYYY-MM-DD)>")
    sys.exit(1)


# ---------------- Main ----------------
def main():
    if len(sys.argv) != 4:
        print_usage_and_exit()

    base = sys.argv[1].upper()
    target = sys.argv[2].upper()
    date_str = sys.argv[3]

    if not is_known_currency(base):
        print(f"[ERROR] Invalid base currency: {base}")
        sys.exit(1)
    if not is_known_currency(target):
        print(f"[ERROR] Invalid target currency: {target}")
        sys.exit(1)
    if not validate_date(date_str):
        print(f"[ERROR] Invalid date {date_str}. Expected between 2025-01-01 and 2025-09-15")
        sys.exit(1)

    result = fetch_exchange_rate(base, target, date_str)
    if not result:
        print(f"[ERROR] No data received for {base} -> {target} on {date_str}")
        sys.exit(1)

    try:
        filepath = save_data_to_file(result, base, target, date_str)
        print(f"[INFO] Data saved to {filepath}")
    except Exception as e:
        log_error(str(e))
        print(f"[ERROR] Failed saving data: {e}")


if __name__ == "__main__":
    main()
