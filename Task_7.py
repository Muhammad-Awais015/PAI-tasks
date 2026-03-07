from flask import Flask, jsonify, request
import requests
from datetime import datetime, timezone, timedelta

server = Flask(__name__)

API  = "18699046af8113add3859f8fad3932d0"
URL = "https://api.openweathermap.org/data/2.5"

PKT = timezone(timedelta(hours=5)) 

PK_CITIES = [
    "Lahore", "Karachi", "Islamabad", "Rawalpindi", "Peshawar",
    "Quetta", "Multan", "Faisalabad", "Hyderabad", "Sialkot",
    "Gujranwala", "Bahawalpur", "Sargodha", "Abbottabad", "Murree",
]

PERIODS = {
    "morning":   (5, 11),
    "afternoon": (12, 16),
    "evening":   (17, 20),
    "night":     (21,  4),
}


def get_period(hr):
    if 5 <= hr <= 11:
        return "morning"
    if 12 <= hr <= 16:
        return "afternoon"
    if 17 <= hr <= 20:
        return "evening"
    return "night"


def build_summary(main_cond, desc, hum, wind_kph, rain_pct=0):
    cond_lower = main_cond.lower()
    msg = ""

    if "thunderstorm" in cond_lower:
        msg = "Thunderstorm expected"
    elif "drizzle" in cond_lower:
        msg = "Light drizzle expected"
    elif "rain" in cond_lower or rain_pct > 60:
        msg = "Rain expected"
    elif rain_pct > 30:
        msg = "Possible light rain"
    elif "snow" in cond_lower:
        msg = "Snow expected"
    elif any(w in cond_lower for w in ("mist", "fog", "haze")):
        msg = "Foggy or hazy conditions"
    elif "clear" in cond_lower:
        msg = "Clear but windy" if wind_kph > 20 else "Clear sky"
    elif "cloud" in cond_lower:
        msg = "Partly cloudy" if any(w in desc for w in ("few", "scattered")) else "Cloudy"
    else:
        msg = desc.title()

    if hum > 80:
        msg += " | very humid"
    elif hum > 60:
        msg += " | humid"

    if wind_kph > 30:
        msg += " | strong wind"
    elif wind_kph > 15:
        msg += " | moderate wind"

    return msg


def _fetch_forecast(city_name):
    resp = requests.get(f"{OWM_BASE}/forecast", params={
        "q": f"{city_name},PK",
        "appid": OWM_KEY,
        "units": "metric",
        "cnt": 40,
    })
    return resp


def _parse_entry(entry):
    utc_dt  = datetime.fromtimestamp(entry["dt"], tz=timezone.utc)
    pak_dt  = utc_dt.astimezone(PKT)
    w       = entry["weather"][0]
    wind_kph = round(entry["wind"]["speed"] * 3.6)
    rain_pct = round(entry.get("pop", 0) * 100)

    return pak_dt, {
        "date":        pak_dt.strftime("%A, %d %b"),
        "time":        pak_dt.strftime("%I:%M %p"),
        "temperature": round(entry["main"]["temp"]),
        "feels_like":  round(entry["main"]["feels_like"]),
        "humidity":    entry["main"]["humidity"],
        "condition":   w["main"],
        "description": w["description"].title(),
        "wind_speed":  wind_kph,
        "rain_chance": rain_pct,
        "summary":     build_summary(w["main"], w["description"],
                                     entry["main"]["humidity"],
                                     wind_kph, rain_pct),
    }


@server.route("/weather")
def weather_by_slot():
    city    = request.args.get("city", "Lahore").strip().title()
    period  = request.args.get("time", "morning").strip().lower()

    if period not in PERIODS:
        return jsonify({"error": "Invalid time value"}), 400

    resp = _fetch_forecast(city)
    data = resp.json()

    if resp.status_code != 200:
        return jsonify({"error": "City not found"}), 404

    matches = []
    for entry in data["list"]:
        pak_dt, info = _parse_entry(entry)
        if get_period(pak_dt.hour) == period:
            matches.append(info)

    if not matches:
        return jsonify({"message": "No data available"})

    return jsonify({
        "city":      data["city"]["name"],
        "country":   "Pakistan",
        "time_slot": period,
        "results":   matches,
    })


@server.route("/weather/day")
def weather_full_day():
    city = request.args.get("city", "Lahore").strip().title()

    resp = _fetch_forecast(city)
    data = resp.json()

    if resp.status_code != 200:
        return jsonify({"error": "City not found"}), 404

    day_map = {}
    for entry in data["list"]:
        pak_dt, info = _parse_entry(entry)
        day_label = pak_dt.strftime("%A, %d %b")
        slot      = get_period(pak_dt.hour)

        day_map.setdefault(day_label, {})
        if slot not in day_map[day_label]:
            day_map[day_label][slot] = info

    output = [
        {
            "date":      day,
            "morning":   slots.get("morning",   "No data"),
            "afternoon": slots.get("afternoon", "No data"),
            "evening":   slots.get("evening",   "No data"),
            "night":     slots.get("night",     "No data"),
        }
        for day, slots in day_map.items()
    ]

    return jsonify({
        "city":    data["city"]["name"],
        "country": "Pakistan",
        "days":    output,
    })


@server.route("/weather/now")
def weather_current():
    city = request.args.get("city", "Lahore").strip().title()

    resp = requests.get(f"{OWM_BASE}/weather", params={
        "q":     f"{city},PK",
        "appid": OWM_KEY,
        "units": "metric",
    })
    data = resp.json()

    if resp.status_code != 200:
        return jsonify({"error": "City not found"}), 404

    now  = datetime.now(PKT)
    w    = data["weather"][0]
    wind_kph = round(data["wind"]["speed"] * 3.6)

    return jsonify({
        "city":         data["name"],
        "country":      "Pakistan",
        "current_time": now.strftime("%I:%M %p"),
        "time_slot":    get_period(now.hour),
        "temperature":  round(data["main"]["temp"]),
        "feels_like":   round(data["main"]["feels_like"]),
        "humidity":     data["main"]["humidity"],
        "condition":    w["main"],
        "description":  w["description"].title(),
        "wind_speed":   wind_kph,
        "visibility":   round(data.get("visibility", 0) / 1000, 1),
        "summary":      build_summary(w["main"], w["description"],
                                      data["main"]["humidity"], wind_kph),
    })


@server.route("/cities")
def city_list():
    return jsonify({"cities": PK_CITIES})


if __name__ == "__main__":
    server.run(debug=True, port=5000)
