import geocoder
import requests
import random
from cs50 import SQL
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import pytz

db = SQL("sqlite:///quotes.db")
dbcities = SQL("sqlite:///cities.db")

TIMES = ['sunrise', 'sunset', 'first_light', 'last_light', 'dawn', 'dusk', 'solar_noon', 'golden_hour']

def get_current_gps_coordinates():
    g = geocoder.ip('me')
    if g.latlng is not None: 
        return g.latlng
    else:
        return None
    
def sunrise_sunset(latitude, longitude):
    presentday = datetime.now()
    tomorrow = presentday + timedelta(1)
    url = (
        f"https://api.sunrisesunset.io/json?lat={latitude}&lng={longitude}"
        f"&date_start={presentday.strftime('%Y-%m-%d')}&date_end={tomorrow.strftime('%Y-%m-%d')}"
    )

    try: 
        response = requests.get(
            url
        )

        response_json = response.json()
        results = response_json["results"]
        for result in results:
            for time in TIMES:
                result[time] = datetime.strftime(datetime.strptime(result[time], "%I:%M:%S %p"), "%H:%M:%S")

        today = {}
        for time in TIMES:
            today[time] = results[0]["date"] + " " + results[0][time]
        return {"today":today, "times":TIMES}
    except (KeyError, IndexError, requests.RequestException, ValueError):
        return None
    
def randquote():
    idnum = random.randint(1,10)
    quote = db.execute("SELECT * FROM quotes WHERE id = ?", idnum)
    return quote

def countries():
    country = dbcities.execute("SELECT * FROM countries ORDER BY name")
    return country

def coor_sunset(latitude, longitude):
    obj = TimezoneFinder()
    tz = obj.timezone_at(lng=float(longitude), lat=float(latitude))
    presentday = datetime.now(pytz.timezone(tz))
    tomorrow = presentday + timedelta(1)
    url = (
        f"https://api.sunrisesunset.io/json?lat={latitude}&lng={longitude}"
        f"&date_start={presentday.strftime('%Y-%m-%d')}&date_end={tomorrow.strftime('%Y-%m-%d')}"
    )

    try: 
        response = requests.get(
            url
        )

        response_json = response.json()
        results = response_json["results"]
        for result in results:
            for time in TIMES:
                result[time] = datetime.strftime(datetime.strptime(result[time], "%I:%M:%S %p"), "%H:%M:%S")

        next = {}
        for time in TIMES:
            if presentday.strftime("%H:%M:%S") > results[0][time]:
                next[time] = results[1]["date"] + " " + results[1][time]
            else:
                next[time] = results[0]["date"] + " " + results[0][time]
                
        next["day_length"] = results[0]["day_length"]
        next["utc_offset"] = results[0]["utc_offset"]
        
        return {"next":next, "times":TIMES}
    except (KeyError, IndexError, requests.RequestException, ValueError):
        return None