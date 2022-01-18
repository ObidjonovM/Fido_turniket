
var xhttp = new XMLHttpRequest();
var connectionAbrupted = false;
var isOnline = true;

xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        postMessage(JSON.parse(this.responseText));
    }
};

function checkEntrance() {
    isOnline = navigator.onLine;

    if (isOnline) {
        if (!connectionAbrupted) {
            try {
                xhttp.open("POST", "https://10.50.50.212:5080/entrance_new", true);
                xhttp.send();
            }
            catch(err) {
                console.log("Error: ", err);
                if (err.name == 'InvalidStateError') {
                    postMessage({
                        status_code : -1010,
                        onLine : isOnline,
                        wasAbbrupted : connectionAbrupted,
                        invalidState : true                 // wifi is on but there is no connection to the server
                    });
                }
            }
        } else {
            connectionAbrupted = false;
            postMessage({
                status_code : -1000,
                online : true,
                wasAbbrupted : true
            });
        }
    } else {
        console.log("Not connected to the network");
        connectionAbrupted = true;
    }

    setTimeout("checkEntrance()", 1000);
}

checkEntrance();

console.log("Entrance worker started");