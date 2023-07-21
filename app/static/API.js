//========================================    Методы для работы с апи
async function move_to_trash(id) {
    try {
        const response = await fetch(host + "/geolocation/add_to_trash?material_id=" + id, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
        });
        const text = await response.text();
    } catch (error) {
        console.error(error);
    }
}
async function delete_user(username) {
    try {
        const response = await fetch(host + "/auth/delete_user" + "?user_for_delete=" + username, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
        });
        const text = await response.text();
        window.location.reload();
    } catch (error) {
        console.error(error);
    }
}

// пинг приложения для проверки валидности токена
async function ping() {
    try {
        const response = await fetch(host + "/app/ping", {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
        });
        const text = await response.text();
        if (text != "ok") {
            window.location.reload();
        }
    } catch (error) {
        console.error(error);
    }
}
async function get_history(id) {

    try {
        const response = await fetch(host + "/geolocation/get-by-id", {
            method: 'POST',
            body: JSON.stringify({ "material_id": id }),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
        });
        const json = await response.json();
        let temp = "";
        for (i in json["data"]) {
            temp += `<p>${json["data"][i]["place"]}  |||  ${json["data"][i]["client_mail"]}  |||
             ${json["data"][i]["date_time"]}  |||  ${json["data"][i]["status"]}, </p>`
        }
        $("#history-block").html(temp);
    } catch (error) {
        alert('Ошибка!');
    }
}
async function post(uri, data) {

    try {
        const response = await fetch(host + uri, {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
        });
        const json = await response.json();
        console.log('Успех:', JSON.stringify(json));
        await upload_photos(data["id"]);
        window.location.reload();
    } catch (error) {
        console.log(error);
    }
}
async function update_geo(data) {

    try {
        const response = await fetch(host + "/geolocation/create", {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
        });
        const json = await response.json();
        response.
            console.log('Успех:', JSON.stringify(json));
        $("#new-geo-popup").fadeOut(200);
    } catch (error) {
        console.log(error);
    }
}
async function update_desc(data) {

    try {
        const response = await fetch(host + "/materials/update-description", {
            method: 'PUT',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
        });
        const json = await response.json();
        console.log('Успех:', JSON.stringify(json));
        $('textarea').blur();
    } catch (error) {
        console.error('Ошибка:', error);
    }
}
async function del(uri, id) {

    try {
        const response = await fetch(host + uri + "?id_for_delete=" + id, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
        });
        const json = await response.json();
        console.log('Успех:', JSON.stringify(json));
        window.location.reload();
    } catch (error) {
        console.error('Ошибка:', error);
    }
}