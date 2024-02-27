from flask import Flask, render_template,jsonify, request, redirect
from helpers import get_current_gps_coordinates, sunrise_sunset, randquote, countries, coor_sunset
from cs50 import SQL

app = Flask(__name__)

db = SQL("sqlite:///quotes.db")
dbcities = SQL("sqlite:///cities.db")

COORDINATES = get_current_gps_coordinates()

@app.route("/")
def home():
    if COORDINATES is not None:
        latitude, longitude = COORDINATES
        sun = sunrise_sunset(latitude, longitude)
    else:
        apology = "Unable to retrieve your coordinates."
        return render_template("failure.html", text=apology)
    
    if sun is not None:
        quotes = randquote()
        country = countries()
        return render_template("home.html", quote=quotes[0], today=sun["today"], times=sun["times"], countries=country, coordinate=COORDINATES)
    else:
        apology = "Unable to get retrieve API"
        return render_template("failure.html", text=apology)

@app.route("/getcities/<country>")
def getcities(country = None):
    country_id = dbcities.execute("SELECT * FROM countries WHERE id  = ?", country)
    if country_id:
        cities = dbcities.execute("SELECT * FROM cities WHERE country_id = ? ORDER BY name", country_id[0]["id"])
    else:
        cities = []
    
    return jsonify(cities)


@app.route("/sun_time", methods=["POST"])
def sun_time():
    coor = request.form.getlist("coordinate")
    lat_long = {}
    location = ''
    if coor:
        lat_long["latitude"] = coor[0]
        lat_long["longitude"] = coor[1]
        location = location + "current location"
    else:
        city_id = request.form.get("city")
        if not city_id:
            return redirect("/")
        else:
            city_coor = dbcities.execute("SELECT * FROM cities WHERE id = ?", city_id)
            if len(city_coor) < 1:
                return redirect("/")
        lat_long["latitude"] = city_coor[0]["latitude"]
        lat_long["longitude"] = city_coor[0]["longitude"]
        location = location + city_coor[0]["name"]
        
    coor_sun = coor_sunset(lat_long["latitude"], lat_long["longitude"])
    if coor_sun is not None:
        return render_template("sunrise_sunset.html", utc_offset=coor_sun["next"]["utc_offset"], location=location, coor_sun=coor_sun)
    else:
        apology = "Unable to get retrieve API"
        return render_template("failure.html", text=apology)

@app.route("/ref")
def ref():
    return render_template("references.html")

@app.route("/about")
def about():
    return render_template("about.html")