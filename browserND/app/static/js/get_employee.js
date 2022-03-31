const VIDEO_INITIAL_WIDTH = 480;
const VIDEO_CHANGE_WIDTH = 800;

var changeInfo = null;
var removeEmployee = null;
var cancelChange = null;
var user_info = null;
var photo = null;
var video = null;
var canvas = null;
var take_photo = null;
var upload_photo = null;
var submit = null;
var dropChange = null;

var initial_info = {};
var width = VIDEO_INITIAL_WIDTH;
var height = 0.9 * width;
streaming = false;

const update_state = "/update_user_info";
const delete_state = "/delete_employee";


function startup() {
    changeInfo = document.getElementById("changeInfo");
    removeEmployee = document.getElementById("removeEmployee");
    saveInfo = document.getElementById("saveInfo");
    cancelChange = document.getElementById("cancelChange");
    user_info = document.getElementById("user_info");
    photo = document.getElementById("photo");
    video = document.getElementById("video");
    canvas = document.getElementById("canvas");
    take_photo = document.getElementById("take_photo");
    upload_photo = document.getElementById("upload_photo");
    submit = document.getElementById("submit");
    dropChange = document.getElementById("dropChange");


    video.addEventListener("canplay", () => {
        if (!streaming) {
            width = VIDEO_CHANGE_WIDTH;
            height = video.videoHeight / (video.videoWidth / width);
            video.setAttribute("width", width);
            video.setAttribute("height", height);
            canvas.setAttribute("width", width);
            canvas.setAttribute("width", height);
            streaming = true;
        }
    }, false);

    changeInfo.addEventListener("click", (ev) => {
        switchToChangeState();
        setChangeModeCSS();
    }, false);


    user_info.addEventListener("submit", (ev) => {
        ev.preventDefault();

        removeCustomer(ev);
        setFormAction(delete_state);
    }, false);


    saveInfo.addEventListener("click", (ev) => {
        switchToSavedState();
        setInitialModeCSS();
    }, false);


    cancelChange.addEventListener("click", (ev) => {
        switchToInitialState();
        setInitialModeCSS();
    }, false);


    dropChange.addEventListener("click", (ev) => {
        switchToInitialState();
        hideSavedStateButtons();
    }, false);


    take_photo.addEventListener("click", (ev) => {
        if (isPhotoShown()) {
            hidePhoto();
            showCamera();
            resetUploadPhoto();
        } else {
            takePhoto();
            hideCamera();
            showPhoto();
        }
    }, false);


    upload_photo.addEventListener("change", (ev) => {
        readURL();
        hideCamera();
        showPhoto();
    }, false);

}


function switchToChangeState() {
    setFormAction(update_state)
    saveInitialInfo();
    enableInputs();
    hideInitialStateButtons();
    showChangeStateButtons();
    hidePhoto();
    turnOnCamera();
    showCamera();
}


function switchToSavedState() {
    if (areAllFieldsFilled()) {
        disableInputs();
        hideChangeStateButtons();
        showSavedStateButtons();
        hideCamera();
        turnOffCamera();
        showPhoto();
    }
}


function switchToInitialState() {
    enterInitialInfo();
    disableInputs();
    hideChangeStateButtons();
    hideCamera();
    turnOffCamera();
    showInitialStateButtons();
    showInitialPhoto();
}


function removeCustomer(ev) {
    if (!confirm("Данный сотрудник будет удален из системы. Продолжить?")) {
        ev.preventDefault();
    }
}


function saveInitialInfo() {

    if (isEmpty(initial_info)) {
        initial_info['first_name'] = document.querySelector('input[name="fname"]').value;
        initial_info['middle_name'] = document.querySelector('input[name="mname"]').value;
        initial_info['last_name'] = document.querySelector('input[name="lname"]').value;
        initial_info['birthDate'] = document.querySelector('input[name="birthDate"]').value;
        initial_info['department'] = document.querySelector('input[name="dept"]').value;
        initial_info['job'] = document.querySelector('input[name="job"]').value;
        initial_info['photo'] = document.querySelector('input[name="jpeg_base64"]').value;
    }
}


function enterInitialInfo() {
    document.querySelector('input[name="fname"]').value = initial_info['first_name'];
    document.querySelector('input[name="mname"]').value = initial_info['middle_name'];
    document.querySelector('input[name="lname"]').value = initial_info['last_name'];
    document.querySelector('input[name="birthDate"]').value = initial_info['birthDate'];
    document.querySelector('input[name="dept"]').value = initial_info['department'];
    document.querySelector('input[name="job"]').value = initial_info['job'];
    document.querySelector('input[name="jpeg_base64"]').setAttribute("value", initial_info['photo']);

}


function areAllFieldsFilled() {
    const inputs = document.querySelectorAll("input[type='text']");
    const labels = document.querySelectorAll("label");
    var labelValues = {};
    var allFieldsAreFilled = true;

    labels.forEach(label => {
        labelValues[label.getAttribute("for")] = label.innerText;
    });

    inputs.forEach(input => {
        if (input.value === "" && allFieldsAreFilled) {
            alert("Поля " + labelValues[input.name] + " не заполнена");
            allFieldsAreFilled = false;
        }
    });

    return allFieldsAreFilled;
}


function enableInputs() {
    for (elem of user_info.elements) {
        if (elem.type === "text" || elem.type === "date") {
            elem.removeAttribute("readonly");
        }
    }
}


function disableInputs() {
    for (elem of user_info.elements) {
        if (elem.type === "text" || elem.type === "date") {
            elem.setAttribute("readonly", true);
        }
    }
}


function setFormAction(actionValue) {
    if (user_info.hasAttribute("action")) {
        user_info.setAttribute("action", actionValue);
    } else {
        var attr = document.createAttribute("action");
        user_info.setAttributeNode(attr);
        user_info.setAttribute("action", actionValue)
    }
}


function showChangeStateButtons() {
    saveInfo.style.display = "inline-block";
    cancelChange.style.display = "inline-block";
    take_photo.style.display = "inline-block";
    document.querySelector('label[for="upload_photo"]').style.display = "inline-block";
}


function hideChangeStateButtons() {
    saveInfo.style.display = "none";
    cancelChange.style.display = "none";
    take_photo.style.display = "none";
    document.querySelector('label[for="upload_photo"]').style.display = "none";
}


function showSavedStateButtons() {
    submit.style.display = "inline-block";
    dropChange.style.display = "inline-block";
}


function hideSavedStateButtons() {
    submit.style.display = "none";
    dropChange.style.display = "none";
}


function showInitialStateButtons() {
    changeInfo.style.display = "inline-block";
    removeEmployee.style.display = "inline-block";
}


function hideInitialStateButtons() {
    changeInfo.style.display = "none";
    removeEmployee.style.display = "none";
}


function hidePhoto() {
    photo.style.display = "none";
}


function showPhoto() {
    photo.style.display = "block";
}


function showInitialPhoto() {
    showPhoto();
    photo.setAttribute("src", initial_info['photo']);
}


function isPhotoShown() {
    return photo.style.display === "block";
}


function hideCamera() {
    video.style.display = "none";
}


function showCamera() {
    video.style.display = "block";
}


function turnOnCamera() {

    navigator.mediaDevices.getUserMedia({video: true, audio: false}).then(
        stream => {
            video.srcObject = stream;
            video.play();
        }
    ).catch(err => {
        console.log("Error occured: " + err)
    });
}


function turnOffCamera() {
    if (video.srcObject !== null) {
        const tracks = video.srcObject.getTracks();

        tracks.forEach((track) => {
            track.stop();
        });

        video.srcObject = null;
    }
}


function takePhoto() {
    const context = canvas.getContext('2d');
    if (width && height) {
        canvas.width = width;
        canvas.height = height;
        context.drawImage(video, 0, 0, width, height);
        photo.setAttribute('src', canvas.toDataURL('image/jpeg'));
        assignPhotoToFormInput();
    }
}


function assignPhotoToFormInput() {
    document.getElementById("jpeg_base64").setAttribute("value", photo.getAttribute('src'));

}


function readURL() {
    if (upload_photo.files && upload_photo.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            photo.setAttribute('src', e.target.result);
            photo.width = width;
            photo.height = height;
            assignPhotoToFormInput();
        }
        reader.readAsDataURL(upload_photo.files[0]);
    }
}


function resetUploadPhoto() {
    upload_photo.value = null;
}


function isEmpty(obj) {
    for (var key in obj) {
        if (obj.hasOwnProperty(key))
            return false;
    }
    return true;
}


function setChangeModeCSS() {
    document.getElementsByClassName("info")[0].className = "change_info";
    document.getElementsByClassName("emp_info")[0].className = "change_emp_info";
    document.getElementsByClassName("emp_photo")[0].className = "change_emp_photo";
    showPhotoButtons();
}


function setInitialModeCSS() {
    document.getElementsByClassName("change_info")[0].className = "info";
    document.getElementsByClassName("change_emp_info")[0].className = "emp_info";
    document.getElementsByClassName("change_emp_photo")[0].className = "emp_photo";
    hidePhotoButtons();
}


function showPhotoButtons() {
    document.getElementsByClassName("photo_buttons")[0].style.display = "block";
}


function hidePhotoButtons() {
    document.getElementsByClassName("photo_buttons")[0].style.display = "none";
}


startup();