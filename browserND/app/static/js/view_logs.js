

const container_img = document.getElementById("container_img");
const container_reg_photo = document.getElementById("container_reg_photo");
const org_img = document.getElementById("original_img");
const log_img = document.getElementById("log_img");
const log_id = document.getElementById("log_id");
const logButTd = document.getElementsByClassName("logButTd");
const label_as_td = document.getElementsByClassName("label_as_td");
const dist_in_td = document.getElementsByClassName("dist_in_td");
const dist_out_td = document.getElementsByClassName("dist_out_td");
const face_dist_td = document.getElementsByClassName("face_dist_td");
const face_coors_td = document.getElementsByClassName("face_coors_td");
const label_as = document.getElementById("label_as");
const dist_in = document.getElementById("dist_in");
const dist_out = document.getElementById("dist_out");
const face_dist = document.getElementById("face_dist");
const face_coors = document.getElementById("face_coors");
const mark_container = document.getElementById("mark_container");
const okey = document.getElementById("okey");
const no = document.getElementById("no");
const correctId = document.getElementById("correct_id");
const xhttp = new XMLHttpRequest();
const tbody = document.getElementsByTagName("tbody");
const tr = tbody[0].getElementsByTagName("tr");


let index = 0;
let prevState = "";
let currState = "";

$(document).ready(function () {
    const all = [];
    const unknownface = [];
    const corruptedimage = [];
    const noface = [];
    const ok_correct = [];
    const ok_wrong = [];

    //grouping the logs by category
    for (let i = 0; i < $('tbody tr').length; i++) {
        all.push($('tbody tr')[i]);

        if ($('tbody tr')[i].cells[3].textContent == 'unknown face') {
            unknownface.push($('tbody tr')[i]);
        }

        if ($('tbody tr')[i].cells[3].textContent == 'corrupted image') {
            corruptedimage.push($('tbody tr')[i]);
        }

        if ($('tbody tr')[i].cells[3].textContent == 'no face') {
            noface.push($('tbody tr')[i]);
        }

        if ($('tbody td.label_as_td')[i].textContent == "CORRECT") {
            $('tbody tr')[i].cells[5].childNodes[0].classList.add('correct');
        }

        else if ($('tbody td.label_as_td')[i].textContent == "WRONG") {
            $('tbody tr')[i].cells[5].childNodes[0].classList.add('wrong');
        } else {
            $('tbody tr')[i].cells[5].childNodes[0].classList.add('no-checked');
        }
        if ($('tbody td.descrip')[i].textContent == "OK" && $('tbody button')[i].classList.contains('correct')) {
            ok_correct.push($('tbody button')[i])
        }
        if ($('tbody td.descrip')[i].textContent == "OK" && $('tbody button')[i].classList.contains('wrong')) {
            ok_wrong.push($('tbody button')[i])
        }
    }

    $('input').click(function () {
        var val1 = $('input[name=desc-entr]:checked').val();
        if (val1 == "all") {
            $('tbody').html(all);
        }
        if (val1 == "unknown face") {
            $('tbody').html(unknownface);
        }
        if (val1 == "corrupted image") {
            $('tbody').html(corruptedimage);
        }
        if (val1 == "no face") {
            $('tbody').html(noface);
        }
        $('#allLogs').html($('tbody tr').length);
        $('#allNoChecked').html($('tbody button.no-checked').length);
    });

    $('#allLogs').html($('tbody tr').length);

    $('#allNoChecked').html($('tbody button.no-checked').length);
    
    if (ok_correct.length > 0 || ok_wrong.length > 0) {
        $('#percentAcc').html(((ok_correct.length / (ok_correct.length + ok_wrong.length)) * 100).toString().substring(0, 5) + '%');
    }
});

function getLogAndRegPhoto(element) {
    currState = element;
    index = element.parentNode.parentNode.rowIndex - 1;
    xhttp.open("POST", "/reg_photo_log_photo/", true);
    xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify({
        emp_id: element.getAttribute("emp_id"),
        log_id: extractId(element.id)
    }));

    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            const resp = JSON.parse(this.responseText);
            if (resp['status_code'] == 0) {
                if (resp['emp_id'] == -1) {
                    container_reg_photo.style.display = "none";
                } else {
                    container_reg_photo.style.display = "";
                }
                if (log_img.src != resp.log_photo) {
                    container_img.style.display = "inline-block";
                    if (prevState != "") {
                        prevState.style.backgroundColor = "transparent";
                    }
                    currState.style.backgroundColor = "rgba(46, 46, 46, 0.979)";
                    prevState = currState;
                    org_img.src = resp.reg_photo;
                    log_img.src = resp.log_photo;
                    label_as.innerHTML = label_as_td[index].innerHTML;
                    dist_in.innerHTML = "Вх. рас.:  " + "<b style='color:white'>" + dist_in_td[index].innerHTML + "</b>";
                    dist_out.innerHTML = "Вых. рас.:  " + "<b style='color:white'>" + dist_out_td[index].innerHTML + "</b>";
                    face_dist.innerHTML = "Лиц. рас.:  " + "<b style='color:white'>" + face_dist_td[index].innerHTML + "</b>";
                    face_coors.innerHTML = "Лиц. кор.:  " + "<b style='color:white'>" + face_coors_td[index].innerHTML + "</b>";
                    log_id.innerHTML = "Лог ид: " + "<b style='color:white'>" + extractId(element.id) + "</b>";
                    if (label_as.innerHTML == okey.value) {
                        okey.checked = true;
                    } else if (label_as.innerHTML == no.value) {
                        no.checked = true;
                    } else {
                        okey.checked = false;
                        no.checked = false;
                    }
                } else {
                    container_img.style.display = "none";
                    org_img.removeAttribute("src");
                    log_img.removeAttribute("src");
                    log_id.innerHTML = "";
                }
            }
        }
    }
}

function updateLabel(e) {
    xhttp.open("POST", "/update_label_as", true);
    xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify({
        log_id: extractId(currState.id),
        label_as: e.value
    }));
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            const resp = JSON.parse(this.responseText);
            if (resp['status_code'] == 0) {
                label_as_td[index].innerHTML = resp.label_as;
                label_as.innerHTML = resp.label_as;
                if (label_as_td[index].innerHTML == "CORRECT") {
                    okey.checked = true;
                    logButTd[index].childNodes[0].className = "logref correct";
                }
                if (label_as_td[index].innerHTML == "WRONG") {
                    no.checked = true;
                    logButTd[index].childNodes[0].className = "logref wrong";
                }
            }
        }
    }
}

function extractId(displayedId) {
    if (displayedId.length > 2) {
        return parseInt(displayedId.substring(2));
    }
    return -1;
}

function keyUpDown(event) {
    const key = event.which || event.keyCode;
    if (key == 38) {
        if (index > 0) {
            index--;
            getLogAndRegPhoto(tr[index].getElementsByTagName("td")[5].getElementsByTagName("button")[0]);
        }
    }
    if (key == 40) {
        if (index < tr.length - 1) {
            index++;
            getLogAndRegPhoto(tr[index].getElementsByTagName("td")[5].getElementsByTagName("button")[0]);
        }
    }
    if (key == 49) {
        updateLabel(okey);
    }
    if (key == 50) {
        updateLabel(no);
    }
}

function updateClientID() {
    const logVal = log_id.children[0].innerText;
    xhttp.open("POST", "/update_log_info", true);
    xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify({
        log_id: logVal,
        correct_id : correctId.value
    }));

    xhttp.onreadystatechange = () => {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            const resp = JSON.parse(xhttp.responseText);
            if (resp['status'] == 'OK') {
                // grab the record containing the log
                const record = document.getElementById('id' + logVal);
                let nameNode = record.parentElement.parentElement.children[2];
                // set the correct name and photo
                nameNode.innerHTML = resp['fullname'];
                org_img.src = resp['photo']
                record.setAttribute("emp_id", correctId.value);
            }
        }
    }
}