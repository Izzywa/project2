# SUNLIGHT
#### Video Demo:  https://youtu.be/1XG8WHbeC18
#### Description:
Sunlight utilize the API from [Sunrise Sunset](https://sunrisesunset.io) to display the time before, after and in between the sunrise and sunset. The rising and setting of the sun is a wonderous thing that had become too routine that we forgot its wonder. This web application will help those who wishes to enjoy how the colour of the sky changes as the world turns, including those who might not be able to see it outdoors.


# App.py
Included in `app.py` are imports including flask, CS50 SQL, and some helper functions.

After conifguring Flask, the file then configure CS50's SQL module to use `quotes.db`(containing 10 random quotes relating to the sun) and `dbcities.db`(containing about 43 thousand cities across the world).

A global variable `COORDINATES` is established with the value of the latitude and longitude of the current location using a helper function.

Thereafter are routes:
### 1.  `"/"` (homepage)

- It first check if the coordinates of the current location is succesfully retrieved to assign value to the variable `latitude` and `longitude`. Then, the variables is used as arguments to the helper function `sunrise_sunset` and the return value assigned to the `sun` variable.

```
    if COORDINATES is not None:
    latitude, longitude = COORDINATES
    sun = sunrise_sunset(latitude, longitude)
```

- If the coordinates is not available, user will be redirected to the failure page and given an apology message.
    
```
        else:
    apology = "Unable to retrieve your coordinates."
    return render_template("failure.html", text=apology)
```

- Should `sunrise_sunset` function able to retrieve the API, a random quote is assigned to the `quote` variable using `randquote()`.
- The country function will retrieve a list of countries with `countries()`.
- Finally, the homepage is rendered while passing a few arguments:
    - `quote` = the selected quote
    - `today` = the times for the sunrise for today
    - `times` = a list of the events included in the return API
    - `countries` = list of countries
    - `coordinates` = current coordinate
- Otherwise an apology is displayed on `failure.html` if the API failed to be retrieved
    
```
if sun is not None:
    quotes = randquote()
    country = countries()
    return render_template("home.html", quote=quotes[0], today=sun["today"], times=sun["times"], countries=country, coordinate=COORDINATES)
else:
    apology = "Unable to get retrieve API"
    return render_template("failure.html", text=apology)
```

### 2. `"/getcities/<country>"`
- This route functions to get the list of cities under a given country.
- With the `dbcities.db`, first data is retrieved to check if `country` is a valid country id in the countries table.
- If it is, the `cities` variable is populated with a list of cities from the cities table that contains said country's id.
```
def getcities(country = None):
    country_id = dbcities.execute("SELECT * FROM countries WHERE id  = ?", country)
    if country_id:
        cities = dbcities.execute("SELECT * FROM cities WHERE country_id = ? ORDER BY name", country_id[0]["id"])
    else:
        cities = []
    
    return jsonify(cities)
```

### 3. `"/sun_time"`
- Firstly this route will check if the `POST` method returns a coordinate with `request.form.getlist("coordinates")`.
- If yes, the dictionary `lat_long` will fill the key "latitude" and "longitude" with the respective value while the variable `location` will contain a string of "current location"
```
coor = request.form.getlist("coordinate")
    lat_long = {}
    location = ''
    if coor:
        lat_long["latitude"] = coor[0]
        lat_long["longitude"] = coor[1]
        location = location + "current location"
```
- Otherwise, the route will request the `city_id` through `request.form.get("city")`.
    - Should this return an empty value or the city id that is not available in the `dbcities.db`, the user will be redirected to the homepage.

    ```
    city_id = request.form.get("city")
        if not city_id:
            return redirect("/")
        else:
            city_coor = dbcities.execute("SELECT * FROM cities WHERE id = ?", city_id)
            if len(city_coor) < 1:
                return redirect("/")
    ```
- The `dbcities` will return the data containing the coordinates and city name relating the the city id to populate the variable `lat_long` and `location`.
- Using the coordinates, the `coor_sunset` helper function will retrieve the API to return the time for the next sunset.
- If successful, the template `sunrise_sunset.html` will be rendered while passing a few arguments.
- Else the `failure.html` is rendered
```
    coor_sun = coor_sunset(lat_long["latitude"], lat_long["longitude"])
    if coor_sun is not None:
        return render_template("sunrise_sunset.html", utc_offset=coor_sun["next"]["utc_offset"], location=location, coor_sun=coor_sun)
    else:
        apology = "Unable to get retrieve API"
        return render_template("failure.html", text=apology)
```

### 4. `"/ref"`
- Renders the Reference page.
```
def ref():
    return render_template("references.html")
```

### 5. `"/about"`
- Renders the About page.
```
def about():
    return render_template("about.html")
```


# Helpers.py
Imports included in `helpers.py` are as follows:
```
import geocoder
import requests
import random
from cs50 import SQL
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import pytz
```

This file them configure CS50's SQL to use `quotes.db` and `dbcities,db`.

A constant variable `TIMES` is declared containing a list of strings to be used with the results from SunriseSunset.io api.
```
TIMES = ['sunrise', 'sunset', 'first_light', 'last_light', 'dawn', 'dusk', 'solar_noon', 'golden_hour']
```

Thereafter are several functions:
### 1. `get_current_coordinates`
- Configuring `geocoder`, this function return the coordinates of the current user ip address
```
def get_current_gps_coordinates():
    g = geocoder.ip('me')
    if g.latlng is not None: 
        return g.latlng
    else:
        return None
```
### 2. `sunrise_sunset`
- This function take in the arguments `latitude` and `longitude`.
- The variable `presentday` represets the current date and time while `tomorrow` is the day after.
- Usin the above variables inserted to a `url` string to be used with and a response is requested.
- The date and time in the results are formatted into 24 hour date format and the relevant information are inserted into the dictionary `today`.
- Returned is a dictionary containing the dictionary `today` and the list `TIMES`.
```
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
```
### 3. `randquote`
- A random quote is selected from the the ten quotes in `quotes.db`.
```
def randquote():
    idnum = random.randint(1,10)
    quote = db.execute("SELECT * FROM quotes WHERE id = ?", idnum)
    return quote
```
### 4. `countries`
- From the table countries in `dbcities.db`, a list of all the available countries is returned.
```
def countries():
    country = dbcities.execute("SELECT * FROM countries ORDER BY name")
    return country
```
### 5. `coor_sunset`
- Similar to `sunrise_sunset` function above, this function takes in the arguments `latitude` and `longitude` to be used in the url for API request to get the time for sunrise and sunset for today and tomorrow.
- Slightly different however is that first the `TimezoneFinder` is used to determine the timezone based on the coordinates provided before establising the date and time for `today` and `tomorrow`.
- After formatting the response, the dictionary `next` is populated with the values of the next closest events as well as the day length and utc offset.
- For example; If the current time is after the current day sunrise, the next sunrise shall be the one the day after.
- a dictionary containing the dictionary `next` and the list `TIMES` is returned.
```
ef coor_sunset(latitude, longitude):
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
```
# `home_script.js`
This file contains the javascript function used in the web application
### 1. `clock`
- This function will be used whenever a page will display a clock.
- This function takes in the argument `utc_offset` and an optional argument `date`.
- Three elements are selected `hrs`, `min`, and `sec` which will display the current hour, minute and second respectively.
- Should the value for the `utc_offset` be 'none', the current `time` is selected using `new Date`.
- Otherwise, the current time is calculated using the function `calctime` using the `utc_offset` as an argument.
- The variable today will be the current date and if the argument `date` is passed, the element shall display today's date
- Finally, the elements selected will display the current time.
- All of the above is wrapped under `setInterval` so that is repeated every 1 second so that it imitates an actual clock.
```
function clock(utc_offset, date){
    var timer = setInterval( () => {
        let time;
        let hrs = document.getElementById('hrs');
        let min = document.getElementById('min');
        let sec = document.getElementById('sec');

        if (utc_offset === 'none') {
            time = new Date();
        }
        else {
            time = calctime(utc_offset);
        }

        let today = time.getFullYear() + '/' + (time.getMonth() + 1 ) + '/' + time.getDate();

        if (arguments.length === 2) {
            date.innerHTML = today;
        }

        hrs.innerHTML = (time.getHours() < 10? '0':'') + time.getHours();
        min.innerHTML = (time.getMinutes() < 10? '0':'') + time.getMinutes();
        sec.innerHTML = (time.getSeconds() < 10? '0':'') + time.getSeconds();

    }, 1000);

    
}
```

### 2. `countdown`
- This function is used when there is a countdown to a certain event.
- The arguments taken will be a dictionary `next_sun`, the `utc_offset` and `suntime` which will be a string.
- After declaring the selected elements, and interval is set for every second to calculate the `distance` between the current time of the selcted location (`time`) and the time for the event(`next_sun[suntime]`)
- The selected elements will display the countdown until the `distance` reaches 0.
```
function countdown(next_sun, utc_offset, suntime) {
    let hrs_el =  $('.' + suntime + '_countdown .hrs');
    let min_el =  $('.' + suntime + '_countdown .min');
    let sec_el =  $('.' + suntime + '_countdown .sec');
    var x = setInterval(() => {
        let time = calctime(utc_offset);

        var distance = next_sun[suntime] - Date.parse(time);
        var hours = Math.floor(distance / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        hrs_el.html(hours);
        min_el.html(minutes);
        sec_el.html(seconds);

        if (distance < 0) {
            clearInterval(x);
            hrs_el.html('00');
            min_el.html('00');
            sec_el.html('00');
          }

    }, 1000);
}
```
### 3. `suntime_time`
- This function is used to display the time for the given event.
- The arguments taken will be;
    - `suntime_array`; a dictionary containing all of the time for the events.
    - `current_time`; the current time according to the timezone.
    - `suntime`; the 'event' in a string.
- The event `suntime` will be the key to the dictionary `suntime_array` to get the date and time for the event.
- The only exception is if the `suntime` event is the day length as that will be the length of the day instead of date and time.
- The elements will be selected according to the `suntime` events to display the date and time on the page.
```
function suntime_time(suntime_array, current_time, time) {
    let date = '';
    let hrs_time = '';
    let min_time = '';
    let sec_time = '';
    if (time === 'day_length') {
        date += current_time.getFullYear() + '/' + (current_time.getMonth() + 1 ) + '/' + current_time.getDate();
        hrs_time += suntime_array['day_length'].split(':')[0];
        min_time += suntime_array['day_length'].split(':')[1];
        sec_time += suntime_array['day_length'].split(':')[2];
    }
    else {
        date += suntime_array[time].split(' ')[0];
        let datetime = new Date(suntime_array[time]);
        hrs_time += (datetime.getHours() < 10? '0':'') + datetime.getHours();
        min_time += (datetime.getMinutes() < 10? '0':'') + datetime.getMinutes();
        sec_time += (datetime.getSeconds() < 10? '0':'') + datetime.getSeconds();
    }
    let date_el = $('.' + time + ' .date');
    date_el.html(date);

    let hrs_el =  $('.' + time + ' .hrs');
    let min_el =  $('.' + time + ' .min');
    let sec_el =  $('.' + time + ' .sec');
    hrs_el.html(hrs_time);
    min_el.html(min_time);
    sec_el.html(sec_time);
}
```
### 4. `calctime`
- This function takes the argument `utc_offset` to calculate the current time of a particular place.
```
function calctime(offset) {
    let milsecs = 60000;
    var currentTime = new Date();
    var utc = Date.parse(currentTime) + (currentTime.getTimezoneOffset() * milsecs);

    let new_date = new Date(utc + (offset * milsecs));
   return new_date;
}
```
### 5. `observer`
- On the page that displays the time for the sunrise and sunset, the container with the information will be responsive with the vertical scrolling.
- This function observes if the the target element of the class `.innerbox` intersects the top-level document viewpor to toggle the class `show`.
```
function observer() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.parentElement.classList.add('show');
            }
            else {
                entry.target.parentElement.classList.remove('show');
            }
        });
    }, {rootMargin: "-50px"});
    const container = document.querySelectorAll(".innerbox");
    container.forEach((el) => observer.observe(el));
}
```

```
.show {
   transform: scale(1, 1);
   transition: all 1.5s;
}
```
### 6. `toggleBar`
- This function will change the shape of the menu bar by toggling the class `change`.
```
function toggleBar(bars) {
    bars.classList.toggle("change");
}
```
### 7. `toggleNav`
- This function will slide the navigation button in and out of view by toggling the class `responsive`.
```
function toggleNav() {
    let nav = $('#navbtn');
    nav.toggleClass('responsive');
}

```
### 8. `nav_toggle`
- This function will change the display of the active button by taking in the argument `thisClass` to determine which button to add the class `active`.
```
function nav_toggle(thisClass) {
    $('nav a').removeClass('active');
    $(thisClass).toggleClass('active');
}
```
### 9. `cities`
- This is an asynchronous function which will change the list of cities option according to the selected country.
- The argument will use the argument `country` which should be the country id to be passed to the route `"/getcities"`
- The response from the request should return a list of cities under the country and inserted under the form as the options available for selection.
```
async function cities(country) {
    if (country == '') {
        return;
    }
    let response = await fetch('/getcities/' + country);
    let cities = await response.json();
    let text = '<option disabled selected value="">CITY</option>';
    for (let i = 0; i < cities.length; i++) {
        text = text + "<option value=" + cities[i]["id"] + ">" + cities[i]["name"] + "</option>";
    }
    $('#city').html(text);

}
```
### 10. `toggle_sky`
- This function will change the colour of the clock and its background by taking in an argument `light`.
- The display that will change with the event include;
    - The background.
        - The elements selected will be `sky` and `sky2`.
        - Both elements are displayed as the background and overlap each other.
        - With the given event, an animation will be triggerred that will fade in one background and fade out another.
        - This will imitate the change of the sky during sunrise and sunset.
    - The movement of the sun.
        - During certain events, the sun object will be animated to move across the background
    - The clock font colour.

```
function toggle_sky (light) {
    $('.sky').css({
        "animation-name": light
    });
    $('.sky2').css({
        "animation-name": "bg_" + light
    });

    const sun_anim = ['sunrise', 'solar_noon', 'sunset', 'dusk']
    if (sun_anim.includes(light)) {
        $('.sun').css({
        "animation-name": "sun_" + light
    });
    }

    const dark_mode = ['dusk', 'last_light', 'first_light']
    if (dark_mode.includes(light)) {
        $('.clock span').css({
        "color": "#F2E5D5"
        });
    }
    else {
        $('.clock span').css({
        "color": "#0D0D0D"
        });
    }
}
```

### 11. `flip_card`
- By toglling the class `is-flipped` of the given element (`el`), this function will 'flip' the between the time for an event and the countdown.
```
function flip_card(el) {
    $(el).toggleClass('is-flipped');
}
```
# Templates
## `Layout.html`
The layout includes the script for jQuery, bootstrap and the local javascript file 'home.js'. The stylesheet linked is '/static/style.scc'.

There are three blocks tags in this template including:
- Block script
    - Under the `<head>` tag for scripts applicable to each child template.
- Title script
    - Within the `<title>` tag.
- Content script
    - Within the `<main>` tag for the main content of the page.

The `<body>` of the template contains three component `<header>`, `<main>`, and `<footer>` under a wrapper div to prevent horizontal scrolling for better presentation.

### Header
```
<header>
    <nav class="navigation text-right">
        <div class="navbtn" id="navbtn">
            <a href="/" class="home">Home</a>
            <a href="/about" class="about">About</a>
            <a href="/ref" class="references">References</a>
        </div>
        <div class="container bars" onclick="toggleBar(this); toggleNav();">
            <div class="bar1"></div>
            <div class="bar2"></div>
            <div class="bar3"></div>
        </div>
    </nav>
    
</header>
```

The navigation bar under the `<header>` contains three links:
- Home
    - This will bring the user to the homepage.
- About
    - The About contains the information shown at the beginning of the demo video.
- References 
    - The references includes the link for the materials used for this web application such as the images, quotes, and city names.


The `.bars` container holds the three bars that represents the menu toggle in smaller screen. Clicking this will trigger two function:
1. [toggleBar(bars)](#6-togglebar)

The class change of this element will rotate the first and third bar of the menu bar to form an 'X' while the second bar will disappear.
```
.bar1, .bar2, .bar3 {
    width: 35px;
    height: 5px;
    background-color: #333;
    margin: 6px 0;
    transition: 0.4s;
  }

.change .bar1 {
transform: translate(0, 11px) rotate(-45deg);
}

.change .bar2 {opacity: 0;}

.change .bar3 {
transform: translate(0, -11px) rotate(45deg);
}
```

2. [`toggleNav()`](#7-togglenav)

This will animate the navigation buttons sliding in and out of view.
```
.navbtn {
    animation-name: navslideout;
    animation-duration: 1s;
    animation-fill-mode: forwards;
    transition: all 0.5s ease;
}
@keyframes navslideout {
    0% {
        transform: translateX(0);
    }
    100% {
        transform: translateX(-120%);
    }
}
.navbtn.responsive {
    display: block;
    animation-name: navslidein;
    animation-duration: 1s;
    animation-fill-mode: forwards;
}
@keyframes navslidein {
    0% {
        transform: translateX(-100%);
    }
    100%{
        transform: translateX(0);
    }
}
```

### Main
The content block is nestled here for the main body of each templates.

### Footer
Linked under the footer is a link to https://sunrisesunset.io/

## `home.html`
The homepage will have a hero image that will span the entirety of the viewport.

Under the title 'SUNLIGHT' a random quote is displayed. 
The title will also move upwards as the user scroll down.
```
        let title = document.getElementById('title');

        window.addEventListener('scroll', () => {
            let value = window.scrollY;

            title.style.marginTop = value * -1.5 + 'px';
        });
```
As this is the homepage, the `home` button on the navigation will be be active with [nav_toggle](#8-nav_toggle).
```
        let home = $('.home');
        nav_toggle(home);
```
Below the description of the page, a clock will display the current time using the [clock](#1-clock) function.

```
        clock('none');
```
The background of the clock will change according to the time:
    - Firstly, the event 'golden hour' is removed from the list of events.
    - Then the events will be sorted according to the time.
    - An interval is set to compare the current time and the time of the events.
    - The background will change by calling the [toggle_sky](#10-toggle_sky) function.
```
        setInterval(() => {
        let time = new Date();

        for (let i = 0; i < today_sun.length; i++) {
            if (Date.parse(time) > today_sun[i].split(' ')[0]) {
                if (today_sun[i].split(' ')[1] == 'last_light') {
                    toggle_sky('last_light');
                    break;
                }
                continue;
            }
            else {
                if (today_sun[i].split(' ')[1] == 'first_light') {
                    toggle_sky('last_light');
                    break;
                }
                else {
                    toggle_sky(today_sun[i - 1].split(' ')[1]);
                    break;
                }
            }
        }

        }, 1000); 
```

Lastly will be the form that will get the coordinate of the requested location to redirect to the page that dispay the times of the sunrise and sunset.

The user will have two options:
1. The current location
    - This will submit the current coordinate and the string 'Curent Location'

    ```
    <form action="/sun_time" method="post" class="col p-3 justify-content-center"> 
        <input name="coordinate" value="{{ coordinate[0] }}" type="hidden">
        <input name="coordinate" value="{{ coordinate[1] }}" type="hidden">
        <input type="submit" value="Current Location" class="col-8 text-center">
    </form>
    ```


2. A city of choice
    - After selecting the country, the async function [cities](#9-cities) will fill in the option with the list of cities under said country.

```
    <form action="/sun_time" method="post" class="col p-3">
        <div class="row justify-content-center">
            <select name="country" onchange="cities(this.value)" class="country col-10">
                <option disabled selected value="">COUNTRY</option>
                {% for country in countries%}
                <option value="{{ country.id }}">{{ country.name }}</option>
                {% endfor %}
            </select>
            <select name="city" id="city" class="city col-10">
            </select>
            <input type="submit" value="Submit Location" class="col-6 text-center">
        </div>
    </form>
```

This form will submit to the route [/sun_time](#3-sun_time) using the method POST and user will be redirected to the Sunrise Sunset page.

## `sunrise_sunset.html`
A few variable is declared to be used on this page
1. `suntime_array`
    - Contains the results from [coor_sunset](#5-coor_sunset)
2. `now`
    - Utilise the [calctime](#4-calctime) function to get the current time of the given location.
3. `times`
    - A list of strings that will be event to be displayed

```
    const suntime_array = {{ coor_sun|tojson }};
    let now = calctime({{ utc_offset|tojson }});
    const times = suntime_array['times'];
```

The containers displayed is made to be interactive using the [observer](#5-observer) function.

This page functions to display:

 - The current time of the selected location
    - This is done by utilising the [clock](#1-clock) function and passing the utc offset as argument.

    ```
        clock({{ utc_offset|tojson }});
    ```

- The current day length

```
        suntime_time(suntime_array['next'], now, 'day_length');
```

- The time and countdown for the given events
```
    for (let i = 0; i < times.length; i++) {
        suntime_time(suntime_array['next'], now, times[i]);
        countdown(next_sun, {{ utc_offset|tojson }}, times[i]);
    }

```

## `about.html`
This page display the information shown at the start of the demo video.

The [clock](#1-clock) is used to display the current date and time.
```
$(document).ready(function() {
    let about = $('.about');
    nav_toggle(about);
    
    let date = document.getElementById('date');

    clock('none', date);
});
```

## `references.html`
This page displays a list of the references used and links to them.

## `failure.html`
This page is displayed if an error is encountered when running the application.


# Database

## `quotes.db`
Ten random quotes are selected from [BrainyQuote](https://www.brainyquote.com/topics/sun-quotes) that mentions the sun or are related to the sun and inserted to the table quotes.

The table includes the quote and the quotee.

```
CREATE TABLE quotes (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
quote TEXT NOT NULL);
```

## `cities.db`
The list of cities is obtained from [simplemaps](https://simplemaps.com/data/world-cities) contains about 43,000 number of entries.

There are two tables in this database:
1. countries

```
CREATE TABLE countries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
```
2. cities

```
CREATE TABLE cities (
    id INTEGER UNIQUE,
    name TEXT NOT NULL,
    country_id INTEGER NOT NULL,
    latitude DECIMAL NOT NULL,
    longitude DECIMAL NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(id)
);
```

