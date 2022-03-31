const MAX_REC_ID_REPS = 2;

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

var ajax_worker = new Worker('/static/js/entrance_worker_old.js');


ajax_worker.onmessage = function (event) {
    const resp = event.data;
    console.log("resp");
    console.log(resp);
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
                    nameIn.innerText = "Вход: " + firstAndLastName(resp.clientName);
                    nameOut.innerText = "Выход: ";
                    break;
                case "out":
                    nameIn.innerText = "Вход: ";
                    nameOut.innerText = "Выход: " + firstAndLastName(resp.clientName);
                    break;
                default:
                    nameIn.innerText = "Вход: ";
                    nameOut.innerText = "Выход: ";
            }
        } else {
            nameIn.innerText = "Вход: ";
            nameOut.innerText = "Выход: ";
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
        }

        if (birthday_photo.classList.contains("shown")) {
            ;
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

window.onload = function() {
    var image=document.getElementById("image");
    var img_array=['/static/img/daily_img/photo_2021-01-06_11-49-33.jpg', '/static/img/daily_img/photo_2021-01-07_17-18-13.jpg'];
    var index=0;
    var interval = 8000;
    function slide() {
        image.src = img_array[index++%img_array.length];
    }

    setTimeout(function() {
        slide();
        setTimeout(arguments.callee, interval)
    }, interval);
}
window.addEventListener("load", function(){
    const interval = 10000;
    let darkMode = false;
    function slide() {
        const currentTime = new Date();
        const hours = currentTime.getHours();
        console.log("slide - 1");
        console.log("hours = " + hours);
        if (hours >= 7 && hours < 19) {
            console.log("slide - 2");
            document.body.style.visibility = "";
            document.body.style.backgroundColor = "";
            if (darkMode) {
                window.location.reload();
                console.log("reload");
            }
        } else {
            console.log("slide - 3");
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