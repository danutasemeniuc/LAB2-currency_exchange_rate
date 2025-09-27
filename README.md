# LAB2-currency_exchange_rate

## Scop

Acest proiect demonstrează cum putem interacționa cu un **Web API** folosind un script Python.
Obiectivele principale:

* Obținerea cursului de schimb dintre două valute la o anumită dată.
* Validarea monedelor și a datei introduse.
* Salvarea rezultatului într-un fișier JSON.
* Gestionarea erorilor și logarea acestora într-un fișier separat (`error.log`).
* Posibilitatea de a reutiliza datele salvate pentru conversii locale prin clasa `Convertor`.

---

## Rulare script

Format general:

```bash
python currency_exchange_rate.py <BASE> <TARGET> <DATE(YYYY-MM-DD)>
```

Exemple:

```bash
python currency_exchange_rate.py USD EUR 2025-01-01
python currency_exchange_rate.py MDL RON 2025-03-15
python currency_exchange_rate.py UAH USD 2025-07-10
```

 Rezultatul se salvează automat în directorul `data/` sub forma unui fișier JSON.
 Erorile (ex. API indisponibil, date invalide) se scriu în `error.log`.

---

##  Structura proiectului

```
lab02/
│
├── currency_exchange_rate.py   # Scriptul principal
├── data/                       # Directorul unde se salvează fișierele JSON
└── error.log                   # Fișierul cu erori logate
```

---

##  Cum funcționează scriptul

1. **`Enum Currency`** – definește monedele suportate (`MDL, USD, EUR, RON, RUS, UAH`).
2. **`is_known_currency()`** – verifică dacă un cod valutar este acceptat.
3. **`Convertor`** – demonstrează cum se pot face conversii folosind date locale stocate.
4. **`fetch_exchange_rate()`** – trimite cerere către API-ul `exchangerate.host`.
5. **`save_data_to_file()`** – salvează rezultatele într-un fișier JSON.
6. **`log_error()`** – scrie erorile într-un fișier `error.log`.
7. **`validate_date()`** – verifică dacă data este în intervalul `2025-01-01` → `2025-09-15`.
8. **`main()`** – pune totul cap la cap: citește parametrii din linia de comandă, validează intrările, apelează API-ul și salvează datele.

---

## Testare

Testează scriptul cu cel puțin 5 date diferite:

```bash
python currency_exchange_rate.py USD EUR 2025-01-01
python currency_exchange_rate.py USD EUR 2025-02-15
python currency_exchange_rate.py USD EUR 2025-04-01
python currency_exchange_rate.py USD EUR 2025-06-15
python currency_exchange_rate.py USD EUR 2025-09-01
```

În urma execuției, vei găsi în `data/` 5 fișiere JSON distincte.

---

##  Explicație cod 

### Importuri și setup

```python
import os
import sys
import json
import requests
from enum import Enum
from datetime import datetime, date as _date
```

* `os, sys` – lucrăm cu fișiere și argumente din linia de comandă.
* `json` – pentru salvarea răspunsurilor în format JSON.
* `requests` – pentru apeluri HTTP către API.
* `Enum` – pentru definirea valutară fixă.
* `datetime, date` – pentru lucrul cu date calendaristice.

---

### Definirea monedelor

```python
class Currency(Enum):
    MDL = "MDL"
    USD = "USD"
    EUR = "EUR"
    RON = "RON"
    RUS = "RUS"
    UAH = "UAH"
```

* `Enum` → set fix de monede acceptate.

```python
def is_known_currency(currency: str) -> bool:
    try:
        Currency(currency)
        return True
    except ValueError:
        return False
```

* verifică dacă moneda dată se află în enum.

---

### Clasa Convertor

```python
class Convertor:
    def __init__(self, exchangeRates: list[dict]):
        self.exchangeRates = exchangeRates
```

* constructor care primește o listă de cursuri valutare.

```python
def exchange(self, from_currency: Currency, to_currency: Currency, date: datetime = datetime.today()) -> float:
    date_str = date.strftime("%Y-%m-%d")
    rate = self.exchangeRates[-1]  # fallback ultima intrare
```

* metoda caută cursul valutar la data cerută sau folosește ultima intrare disponibilă.

```python
    for exchangeRate in self.exchangeRates:
        if exchangeRate["date"] == date_str:
            rate = exchangeRate
            break
```

* verifică dacă data există în lista de cursuri.

```python
    rate["mdl"] = 1.0
```

* stabilește MDL ca valoare fixă de referință.

```python
    from_key = from_currency.name.lower()
    to_key = to_currency.name.lower()
```

* convertește monedele în chei de tip string.

```python
    if from_key not in rate or to_key not in rate:
        raise ValueError(f"Unknown currency {from_currency} or {to_currency}")
```

* verifică dacă monedele sunt prezente în date.

```python
    return rate[to_key] / rate[from_key]
```

* calculează raportul dintre cele două monede.

---

### Configurări directoare și fișiere

```python
BASE_URL = "https://api.exchangerate.host"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(BASE_DIR, "error.log")
```

* `BASE_URL` – endpoint API.
* `DATA_DIR` – folder pentru salvarea datelor.
* `LOG_FILE` – fișier pentru erori.

---

### Funcții utilitare

```python
def log_error(message: str) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")
```

* scrie erorile cu timestamp în `error.log`.

```python
def validate_date(date_str: str) -> bool:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return False
    earliest = _date(2025, 1, 1)
    latest = _date(2025, 9, 15)
    return earliest <= dt <= latest
```

* verifică formatul și dacă data este în intervalul acceptat.

---

### Funcții pentru API și fișiere

```python
def fetch_exchange_rate(base_currency: str, target_currency: str, date_str: str):
    url = f"{BASE_URL}/{date_str}"
    params = {"base": base_currency, "symbols": target_currency}
```

* construiește cererea către API.

```python
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
```

* trimite cererea, verifică răspunsul și returnează JSON-ul.

```python
    except Exception as e:
        msg = f"API request failed: {e}"
        log_error(msg)
        print(f"[ERROR] {msg}")
        return None
```

* gestionează erorile de rețea sau API.

---

```python
def save_data_to_file(data: dict, base_currency: str, target_currency: str, date_str: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    filename = f"{base_currency}_{target_currency}_{date_str}.json"
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return filepath
```

* creează folderul `data/` (dacă nu există) și salvează fișierul JSON.

---

### Funcția principală

```python
def print_usage_and_exit():
    print("Usage: python currency_exchange_rate.py <BASE> <TARGET> <DATE(YYYY-MM-DD)>")
    sys.exit(1)
```

* afișează modul de utilizare.

```python
def main():
    if len(sys.argv) != 4:
        print_usage_and_exit()
```

* verifică numărul de argumente.

```python
    base = sys.argv[1].upper()
    target = sys.argv[2].upper()
    date_str = sys.argv[3]
```

* citește argumentele.

```python
    if not is_known_currency(base):
        print(f"[ERROR] Invalid base currency: {base}")
        sys.exit(1)
```

* verifică validitatea monedei de bază.

```python
    if not validate_date(date_str):
        print(f"[ERROR] Invalid date {date_str}. Expected between 2025-01-01 and 2025-09-15")
        sys.exit(1)
```

* verifică validitatea datei.

```python
    result = fetch_exchange_rate(base, target, date_str)
    if not result:
        print(f"[ERROR] No data received for {base} -> {target} on {date_str}")
        sys.exit(1)
```

* apelează API-ul și verifică răspunsul.

```python
    try:
        filepath = save_data_to_file(result, base, target, date_str)
        print(f"[INFO] Data saved to {filepath}")
    except Exception as e:
        log_error(str(e))
        print(f"[ERROR] Failed saving data: {e}")
```

* salvează rezultatele într-un fișier JSON.

---

```python
if __name__ == "__main__":
    main()
```

* rulează programul doar dacă fișierul este executat direct.

---
# Codul integral:
```python
```python
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
```

## Concluzie:
Proiectul currency_exchange_rate.py demonstrează eficient interacțiunea cu un Web API, validarea intrărilor, gestionarea erorilor și salvarea datelor în format JSON. Structura modulară și utilizarea claselor și funcțiilor fac codul ușor de întreținut și extins. Datele salvate permit reutilizare ulterioară, iar logarea erorilor asigură trasabilitate. În ansamblu, scriptul oferă o bază solidă pentru aplicații practice și educaționale legate de cursuri valutare.
