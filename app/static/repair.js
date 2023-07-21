$(".file-wrapper input[type='file']").on("change", function () {
    $(this).parent().children("label").html("Выбрано файлов: " + $(this)[0].files.length);
})
async function move_to_repair(data){
    try {
        const response = await fetch(host+"/geolocation/move_to_repair", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            },
            body: JSON.stringify(data)
        });
        const resp = await response.json();
        if (resp["status"] != true){
            alert("Произошла ошибка! Скорее всего актив уже находится в ремонте");
        };
        window.location.reload();
    } catch (error) {
        console.error(error);
    }
}
async function add_to_repair(data){
    try {
        const response = await fetch(host+"/geolocation/add_details_to_repair", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            },
            body: JSON.stringify(data)
        });
        const resp = await response.json();
        if (resp["status"] != true){
            alert("Произошла ошибка! Актив не в ремонте");
        };
        window.location.reload();
    } catch (error) {
        console.error(error);
    }
}
async function move_from_repair(data){
    try {
        const response = await fetch(host+"/geolocation/move_from_repair", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            },
            body: JSON.stringify(data)
        });
        const resp = await response.json();
        if (resp["status"] != true){
            alert("Произошла ошибка! Актив не в ремонте");
        };
        window.location.reload();
    } catch (error) {
        console.error(error);
    }
}
async function short_repair(data, file = null){
    try {
        const url = new URL(host+"/geolocation/short_repair");
        url.search = new URLSearchParams(data);
        let form = null;
        if (file){
            form = new FormData();
            form.append('file', file);
        }
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + access_token
            },
            body: form
        });
        const resp = await response.json();
        if (resp["status"] != true){
            alert("Произошла ошибка! Для получения дополнительной информации зайдите в терминал программы");
        };
        window.location.reload();
    } catch (error) {
        console.error(error);
    }
}