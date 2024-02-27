

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

function calctime(offset) {
    let milsecs = 60000;
    var currentTime = new Date();
    var utc = Date.parse(currentTime) + (currentTime.getTimezoneOffset() * milsecs);

    let new_date = new Date(utc + (offset * milsecs));
   return new_date;
}

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

function toggleBar(bars) {
    bars.classList.toggle("change");
}

function toggleNav() {
    let nav = $('#navbtn');
    nav.toggleClass('responsive');
}

function nav_toggle(thisClass) {
    $('nav a').removeClass('active');
    $(thisClass).toggleClass('active');
}

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

function flip_card(el) {
    $(el).toggleClass('is-flipped');
}