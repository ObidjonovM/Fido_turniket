// const dataTable = document.getElementById("dataTable");
// const btnExportToCsv = document.getElementById("btnExportToCsv");
//
// btnExportToCsv.addEventListener("click", () => {
//     const exporter = new TableCSVExporter(dataTable);
//     const csvOutput = exporter.convertToCSV();
//     const csvBlob = new Blob([csvOutput], {
//         type: "text/csv;charset=utf-8"
//     });
//     const blobUrl = URL.createObjectURL(csvBlob);
//     const anchorElement = document.createElement("a");
//
//     anchorElement.href = blobUrl;
//     anchorElement.download = "logs.csv";
//     anchorElement.click();
//
//     setTimeout(() => {
//         URL.revokeObjectURL(blobUrl);
//     }, 500);
// });


function exceller(type, fn, dl) {
        var elt = document.getElementById('toExcel');
        var wb = XLSX.utils.table_to_book(elt, { sheet: "sheet1" });
        return dl ?
            XLSX.write(wb, { bookType: type, bookSST: true, type: 'base64' }):
            XLSX.writeFile(wb, fn || ('MySheetName.' + (type || 'xlsx')));
}


function imgOpen() {
    if (document.querySelector('.img_sort').style.display !== 'none') {
        document.querySelector('.img_sort').style.display = 'none';
        document.querySelector('.img_sort_open').style.display = 'block';
    } else {
        document.querySelector('.img_sort').style.display = 'block';
        document.querySelector('.img_sort_open').style.display = 'none';

    }
}

function imgOpen2() {
    if (document.querySelector('.img_sort1').style.display !== 'none') {
        document.querySelector('.img_sort1').style.display = 'none';
        document.querySelector('.img_sort_open1').style.display = 'block';
    } else {
        document.querySelector('.img_sort1').style.display = 'block';
        document.querySelector('.img_sort_open1').style.display = 'none';

    }
}

function imgOpen3() {
    if (document.querySelector('.img_sort2').style.display !== 'none') {
        document.querySelector('.img_sort2').style.display = 'none';
        document.querySelector('.img_sort_open2').style.display = 'block';
    } else {
        document.querySelector('.img_sort2').style.display = 'block';
        document.querySelector('.img_sort_open2').style.display = 'none';

    }
}

function imgOpen4() {
    if (document.querySelector('.img_sort3').style.display !== 'none') {
        document.querySelector('.img_sort3').style.display = 'none';
        document.querySelector('.img_sort_open3').style.display = 'block';
    } else {
        document.querySelector('.img_sort3').style.display = 'block';
        document.querySelector('.img_sort_open3').style.display = 'none';

    }
}

function imgOpen5() {
    if (document.querySelector('.img_sort4').style.display !== 'none') {
        document.querySelector('.img_sort4').style.display = 'none';
        document.querySelector('.img_sort_open4').style.display = 'block';
    } else {
        document.querySelector('.img_sort4').style.display = 'block';
        document.querySelector('.img_sort_open4').style.display = 'none';

    }
}


const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
        v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : ((v1 == '-') != (v2 == '-') ? (asc == true ? (v1 == '-' && v2 != '-' ? 1 : -1) : (v1 == '-' && v2 != '-' ? -1 : 1)) : (asc == true ? v1.toString().localeCompare(v2, undefined, {numeric: true, sensitivity: 'base'}) : (!v1.toString().localeCompare(v2, undefined, {numeric: true, sensitivity: 'base'}) ? -1 : 1)))
)(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

document.querySelectorAll('th').forEach(th => th.children[0] ? th.children[0].addEventListener('click', (() => {
    const table = th.closest('table');
    Array.from(table.querySelectorAll('tr:nth-child(n+2)'))
        .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
        .forEach(tr => table.appendChild(tr));
})) : '');