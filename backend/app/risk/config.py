# backend/app/risk/config.py
RISK_BANDS = [
    {"max": 24.99, "name": "NORMAL"},
    {"max": 49.99, "name": "LOW"},
    {"max": 74.99, "name": "HIGH"},
    {"max": 100.0, "name": "CRITICAL"}
]

def get_severity_band(score: float) -> str:
    for band in RISK_BANDS:
        if score <= band["max"]:
            return band["name"]
    return "CRITICAL"
