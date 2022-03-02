(function(){
    var width = 640;
    var height = 480;
    var streaming = false;
    var state = "initial";    // other possible states: "another_photo", "upload_photo"
    var video = null;
    var canvas = null;
    var photo = null;
    var take_photo = null;
    var upload_photo = null;
    var img_container = null;
    var submit = null;



    function startup() {
        video = document.getElementById('video');
        canvas = document.getElementById('canvas');
        photo = document.getElementById('photo');
        take_photo = document.getElementById('take_photo');
        upload_photo = document.getElementById('upload_photo');
        img_container = document.getElementById('jpeg_base64');
        submit = document.getElementById('submit');
        
        navigator.mediaDevices.getUserMedia({video:true, audio:false}).then(
            function(stream) {
                video.srcObject = stream;
                video.play();
            }
        ).catch(function(err){
            console.log("Error occured: " + err)
        });

    video.addEventListener('canplay', function(ev){
        if (!streaming) {
            video.setAttribute('width', width);
            video.setAttribute('height', height);
            canvas.setAttribute('width', width);
            canvas.setAttribute('height', height);
            streaming = true;
        }
    }, false);

    take_photo.addEventListener('click', function(ev) {
        takepicture();
        ev.preventDefault();
    }, false);


    upload_photo.addEventListener('change', function(ev) {
        readURL();
        ev.preventDefault();
        photo.style.display = "inline-block";
        video.style.display = "none";
        state = "upload_photo";
    }, false);


    photo.addEventListener('load', function(ev) {
        img_container.value = photo.getAttribute('src');
 
    }, false);


    submit.addEventListener('click', function(ev) {
        if (img_container.value === "") {
            alert("Фото не указано");
            ev.preventDefault();
            }
    }, false);


    function takepicture() {
        switch(state) {
            case "initial":
                takepicture_initial_state();
                state = "another_photo";
                break;
            case "another_photo":
                takepicture_another_photo();
                state = "initial";
                break;
            case "upload_photo":
                photo.style.display = "none";
                video.style.display = "block";
                upload_photo.value = null;
                state = "initial"
                break;
            default:
                console.log("unkown state");
        }
    }

    function takepicture_initial_state() {
        const context = canvas.getContext('2d');
        if (width && height) {
            canvas.width = width;
            canvas.height = height;
            context.drawImage(video, 0, 0, width, height);
            const data = canvas.toDataURL('image/jpeg');
            photo.setAttribute('src', data);
            video.style.display = "none";
            photo.style.display = "inline-block";
            take_photo.value = "Новая Фотография";
            upload_photo.disabled = true;
        }
    }

    function takepicture_another_photo() {
        img_container.value = ""
        photo.setAttribute('src', "");
        photo.style.display = "none";
        video.style.display = "block";
        take_photo.value = "Фотографировать";
        upload_photo.disabled = false;
    }


    function readURL() {
        if (upload_photo.files && upload_photo.files[0]) {
            var reader = new FileReader();
            reader.onload = function(e) {
                photo.setAttribute('src', e.target.result);
                photo.width = width;
                photo.height = height;
            }
            reader.readAsDataURL(upload_photo.files[0]);
        }
    }

}

    window.addEventListener('load', startup, false);

})();