
const canvasWidth = 800;
const canvasHeight = 900;

let canvas = document.getElementsByTagName("canvas")[0];
let upload_photo = document.getElementById("upload_photo");
let main_photo = document.getElementById("main_photo");
let add_photo = document.getElementById("add_photo");
let log_block = document.getElementById("log_block")
let photos = document.getElementsByClassName("photo");
let photoContent = null;
let url = window.location.href;
let emp_id = url.substring(url.lastIndexOf('/') + 1);
let photo_id = "";
let log_id = null;
let xhttp = new XMLHttpRequest();

const context = canvas.getContext("2d");

// window.onload = function () {
//     if (photos.length > 0) {
//         main_photo.src = photos[0].src;
//         main_photo.setAttribute("class", "main-photo");
//         photos[0].classList.add("selected");
//         photo_id = photos[0].id;
//     }
// }

function add_more_photos() {
    const logPhotos = document.getElementsByClassName("log-photo");
    xhttp.open("POST", "/emp_log_photos", true);
    xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify({ emp_id: emp_id, start_log_id: log_id, num_photos: 10 }));
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            const resp = JSON.parse(this.responseText);
            log_id = resp.records[resp.records.length - 1].log_id;
            for (let i = 0; i < resp.records.length; i++) {
                if (log_block.childElementCount < 11) {
                    let img = document.createElement("img");
                    img.setAttribute("id", "log_img" + resp.records[i].log_id);
                    img.setAttribute("class", "photo photo-other log-photo");
                    img.setAttribute("onclick", "setId(this)");
                    img.setAttribute("src", resp.records[i].photo);
                    log_block.appendChild(img);
                }else {
                    logPhotos[i].setAttribute("id", "log_img" + resp.records[i].log_id);
                    logPhotos[i].setAttribute("class", "photo photo-other log-photo");
                    logPhotos[i].setAttribute("onclick", "setId(this)");
                    logPhotos[i].setAttribute("src", resp.records[i].photo);
                }
            }
        }
    }
}

function photos_next() {

}

add_photo.onclick = function () {
    photoContent = canvas.toDataURL("image/jpeg");
    var new_photo = { new_photo: photoContent };
    xhttp.open("POST", "/more_emp_photos/" + emp_id, true);
    xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(new_photo));
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var obj = JSON.parse(this.responseText);
            if (obj.status_code == 0) {
                let img = document.createElement("img");
                img.setAttribute("id", "img" + obj.id);
                img.setAttribute("class", "photo photo-other");
                img.setAttribute("src", main_photo.src);
                img.setAttribute("onclick", "setId(this)");
                document.getElementById("other_photos").appendChild(img);
            }
        }
    };
}

main_photo.addEventListener("load", () => {
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    context.drawImage(main_photo, 0, 0, canvasWidth, canvasHeight);
})

upload_photo.addEventListener("change", (ev) => {
    readURL();
}, false);

function readURL() {
    if (upload_photo.files && upload_photo.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            main_photo.setAttribute("class", "main-photo");
            main_photo.setAttribute('src', e.target.result);
        }
        reader.readAsDataURL(upload_photo.files[0]);
    }
}

function deleteImg() {
    xhttp.open('DELETE', "/more_emp_photos/" + emp_id, true);
    xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify({ rec_id: extractId(photo_id) }));
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            const resp = JSON.parse(this.responseText);
            if (resp['status'] == 'OK') {
                if (typeof photo_id !== "undefined") {
                    document.getElementById(photo_id).remove();
                }
                if (photos.length && photos.length > 0) {
                    main_photo.src = photos[photos.length - 1].src;
                    photos[photos.length - 1].classList.add("selected");
                    photo_id = photos[photos.length - 1].id;
                } if (photos.length == 0) {
                    main_photo.removeAttribute("src");
                    main_photo.removeAttribute("class");
                }
            }
        }
    };
}

function setId(img) {
    photo_id = img.id;
    for (var i = 0; i < photos.length; i++) {
        if (photos.length > 0) {
            photos[i].classList.remove("selected");
        }
    }
    main_photo.setAttribute("class", "main-photo");
    main_photo.src = img.src;
    img.classList.add("selected");
}

function extractId(displayedId) {
    if (displayedId.length > 3) {
        return parseInt(displayedId.substring(3));
    }
    return -1;
}
