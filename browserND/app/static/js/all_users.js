function deleteUser(e) {
        let user_id = e.getAttribute('id');

        let xhttp = new XMLHttpRequest();

        var result = confirm("Удалить ?");

        if (result){

            xhttp.open('POST', '/remove_user/' + user_id, true);

            xhttp.setRequestHeader("Content-type", "application/json;charset=UTF-8");

            xhttp.send();

            xhttp.onreadystatechange = () => {

                if (xhttp.readyState == 4 && xhttp.status == 200) {
                    const resp = JSON.parse(xhttp.responseText);
                    if (resp) {
                        window.location.reload();
                        window.open('/all_users', '_self')
                    } else {
                        alert('Не удалось удалить тип сотрудника!');
                    }
                }
            }

        }
        else {
            return false;
        }


}