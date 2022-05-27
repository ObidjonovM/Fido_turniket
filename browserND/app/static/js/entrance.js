const MAX_REC_ID_REPS = 2;

const temper_tek = document.getElementById("temper_tek");
const temper_zav = document.getElementById("temper_zav");
const temper_pos_zav = document.getElementById("temper_pos_zav");
const icon_weather_tek = document.getElementById("icon_weather_tek");
const icon_weather_zav = document.getElementById("icon_weather_zav");
const icon_weather_pos_zav = document.getElementById("icon_weather_pos_zav");
const con_text_tek = document.getElementById("con_text_tek");
const con_text_zav = document.getElementById("con_text_zav");
const con_tek_pos_zav = document.getElementById("con_tek_pos_zav");

var photos = document.getElementById("photos"); 
var photo_in = document.getElementById("photo_in");
var photo_out = document.getElementById("photo_out");
var audio = document.getElementById("song");
var birthday_photo = document.getElementById("birthday");
var clientName = document.getElementById("client_name");
var nameIn = document.getElementById("name_in");
var nameOut = document.getElementById("name_out");
var playing_audio = false;
var last_record_id = -1;
var record_id_reps = 0;

var ajax_worker = new Worker('/static/js/entrance_worker.js');


ajax_worker.onmessage = function (event) {
    const resp = event.data;
    if (resp.status_code == 0) {
        if (resp.birthday) { 
            if (!playing_audio) {
                photo_in.setAttribute('src', '');
                photo_out.setAttribute('src', '');
                clientName.innerHTML = resp.clientName;
                audio.play();
                playing_audio = true;
                fixView();
            }
            setTimeout(
                () => {
                    playing_audio = false;
                    audio.currentTime = 0;
                    photo_in.setAttribute('src', '/in_video_feed');
                    photo_out.setAttribute('src', '/out_video_feed');
                    fixView();
                    clientName.innerHTML = "";
                },
                (audio.duration + 1) * 1000);
        } else
            fixView();
        if (resp.client_id > 0) {
            if (resp.rec_id == last_record_id) {
                if (record_id_reps >= MAX_REC_ID_REPS) {
                    resp.clientName = "";
                } else {
                    record_id_reps += 1;
                }
            } else {
                last_record_id = resp.rec_id;
                record_id_reps = 0;
            }

            switch (resp.action) {
                case "in":
                    nameIn.innerHTML = '<img src="/static/img/ic_enter.svg"> Вход: ' + firstAndLastName(resp.clientName);
                    nameOut.innerHTML = '<img src="/static/img/ic_exit.svg"> Выход: ';
                    break;
                case "out":
                    nameIn.innerHTML = '<img src="/static/img/ic_enter.svg"> Вход: ';
                    nameOut.innerHTML = '<img src="/static/img/ic_exit.svg"> Выход: ' + firstAndLastName(resp.clientName);
                    break;
                default:
                    nameIn.innerHTML = '<img src="/static/img/ic_enter.svg"> Вход: ';
                    nameOut.innerHTML = '<img src="/static/img/ic_exit.svg">Выход: ';
            }
        } else {
            nameIn.innerHTML = '<img src="/static/img/ic_enter.svg"> Вход: ';
            nameOut.innerHTML = '<img src="/static/img/ic_exit.svg">Выход: ';
        }

    } else {
        if (resp.status_code == -1000 || resp.status_code == -1010) {
            location.reload(); 
        } else {
            fixView();
        }
    }

}


function fixView() {

    if (playing_audio) {
        if (photos.classList.contains("shown")) {
            photos.classList.remove("shown");
            photos.classList.remove("row");
            photos.classList.add("hidden");
        }

        if (birthday_photo.classList.contains("hidden")) {
            birthday_photo.classList.remove("hidden");
            birthday_photo.classList.add("shown");
        }
    } else {
        if (photos.classList.contains("hidden")) {
            photos.classList.remove("hidden");
            photos.classList.add("shown");
            photos.classList.add("row");
        }

        if (birthday_photo.classList.contains("shown")) {
            birthday_photo.classList.remove("shown");
            birthday_photo.classList.add("hidden");
        }
    }
}

function firstAndLastName(name) {
    if (name.length > 0) {
        const chunks = name.trim().split(" ");
        return chunks[1] + " " + chunks[0];
    } else {
        return "";
    }

}

window.addEventListener("load", function(){
    const interval = 10000;
    let darkMode = false;
    function slide() {
        const currentTime = new Date();
        const hours = currentTime.getHours();
        if (hours >= 7 && hours < 19) {
            document.body.style.visibility = "";
            document.body.style.backgroundColor = "";
            if (darkMode) {
                window.location.reload();
            }
        } else {
            document.body.style.visibility = "hidden";
            document.body.style.backgroundColor = "black";
            darkMode = true;
        }
    }
    window.addEventListener("load", slide());

    setTimeout(function () {
        slide();
        setTimeout(arguments.callee, interval)
    }, interval);
})

window.addEventListener("load", function () {
    const interval = 1000 * 60 * 15;
    function getTempTek() {
        const xhr = new XMLHttpRequest();
        xhr.addEventListener("readystatechange", function () {
            if (this.readyState == 4 && this.status == 200) {
                const resp = JSON.parse(this.responseText);
                temper_tek.innerHTML = Math.round(resp.main.temp);
            }
        });

        xhr.open("POST", "http://api.openweathermap.org/data/2.5/weather?q=Tashkent,Uzbekistan&APPID=87ea10a19e895caef5319978b09d9bb6&lang=ru&units=metric", true);
        xhr.send();
    }
    window.addEventListener("load", getTempTek());

    setTimeout(function () {
        getTempTek();
        setTimeout(arguments.callee, interval)
    }, interval);
})

window.addEventListener("load", function () {
    const interval = 1000 * 60 * 15;
    const today = new Date();
    const h = today.getHours();
    function getTempAll() {
        const xhr = new XMLHttpRequest();
        xhr.addEventListener("readystatechange", function () {
            if (this.readyState == 4 && this.status == 200) {
                const resp = JSON.parse(this.responseText);

                let temp_all = [];
                let temp_all1 = [];
                for (let i = 0; i < resp.forecast.forecastday[1].hour.length; i++) {
                    temp_all.push(resp.forecast.forecastday[1].hour[i].temp_c);
                }
                for (let i = 0; i < resp.forecast.forecastday[2].hour.length; i++) {
                    temp_all1.push(resp.forecast.forecastday[2].hour[i].temp_c);
                }
                var min = Math.min.apply(null, temp_all),
                    max = Math.max.apply(null, temp_all);
                min1 = Math.min.apply(null, temp_all1),
                    max1 = Math.max.apply(null, temp_all1);
                const minRound = Math.round(min);
                const maxRound = Math.round(max);
                const minRound1 = Math.round(min1);
                const maxRound1 = Math.round(max1);
                temper_zav.innerHTML = minRound + "..." + maxRound;
                temper_pos_zav.innerHTML = minRound1 + "..." + maxRound1;
                icon_weather_tek.setAttribute("src", resp.forecast.forecastday[0].hour[h].condition.icon);
                icon_weather_zav.setAttribute("src", resp.forecast.forecastday[1].day.condition.icon);
                icon_weather_pos_zav.setAttribute("src", resp.forecast.forecastday[2].day.condition.icon);
            }
        });

        xhr.open("POST", "http://api.weatherapi.com/v1/forecast.json?key=eb2d3032f2a14fe089655010212408&q=Tashkent&days=3&aqi=no&alerts=no&lang=ru", true);
        xhr.send();
    }
    window.addEventListener("load", getTempAll());

    setTimeout(function () {
        getTempAll();
        setTimeout(arguments.callee, interval)
    }, interval);
})

function startTime() {
    const today = new Date();
    const mon = today.getMonth();
    const date = today.getDate();
    const n = today.getDay();
    const h = today.getHours();
    var m = today.getMinutes();
    var month = [
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря"
    ]
    var days = [
        'Воскресенье',
        'Понедельник',
        'Вторник',
        'Среда',
        'Четверг',
        'Пятница',
        'Суббота'
    ];
    m = checkTime(m);
    document.getElementById("day").innerHTML = days[n] + "<br>" + date + " " + month[mon];
    document.getElementById("time").innerHTML = h + ":" + m;
    var t = setTimeout(function () { startTime() }, 500);
}

function checkTime(i) {
    if (i < 10) {
        i = "0" + i;
    }
    return i;
}