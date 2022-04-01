/** tableda kunlik kirgan chiqgan soatlarni chizish open **/

let dateLogs = document.getElementById("dateLogs");
dateLogs.value = new Date().toISOString().substring(0,10);
function getDateLogs() {
    const xhr = new XMLHttpRequest();
    xhr.addEventListener("readystatechange", function () {
        if (this.readyState == 4 && this.status == 200) {
            const resp = JSON.parse(this.responseText);
            addDateLogs(resp);
        }
    });
    xhr.open("POST", "/all_employees", true);
    xhr.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({'date': dateLogs.value}));
}
function addDateLogs(resp) {
    let daily_logs_in = document.querySelectorAll('.daily-logs-in');
    let daily_logs_out = document.querySelectorAll('.daily-logs-out');
    for (let i=0; i < daily_logs_in.length; i++) {
        if (daily_logs_in[i].getAttribute('emp_id') in resp['daily_logs_in']){
            daily_logs_in[i].innerHTML = resp['daily_logs_in'][daily_logs_in[i].getAttribute('emp_id')];
        }else {
            daily_logs_in[i].innerHTML = '-';
        }
    }
    for (let i=0; i < daily_logs_out.length; i++) {
        if (daily_logs_out[i].getAttribute('emp_id') in resp['daily_logs_out']){
            console.log(daily_logs_out[i].getAttribute('emp_id'));
            daily_logs_out[i].innerHTML = resp['daily_logs_out'][daily_logs_out[i].getAttribute('emp_id')];
        }else {
            daily_logs_out[i].innerHTML = '-';
        }
    }
}

/** tableda kunlik kirgan chiqgan soatlarni chizish close **/

/** excel da tableni dounloud qilish open**/

function ExportToExcel(type, fn, dl) {
    var elt = document.getElementById('dataTable');
    var wb = XLSX.utils.table_to_book(elt, { sheet: "sheet1" });
    return dl ?
        XLSX.write(wb, { bookType: type, bookSST: true, type: 'base64' }):
        XLSX.writeFile(wb, fn || ('MySheetName.' + (type || 'xlsx')));
}

/** excel da tableni dounloud qilish close**/
