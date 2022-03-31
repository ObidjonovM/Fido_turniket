
var audio = document.getElementById("song");

audio.play();

setTimeout(
        () => window.location.replace('https://10.50.50.55:5080/entrance_old'),
        (audio.duration + 1)*1000
    );