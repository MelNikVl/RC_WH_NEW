const params = new URLSearchParams(window.location.search)
const access_token = params.get("t");

var host = document.location.origin;
var files_to_upload = [];

function invert_selection(elem){
    if ($(elem).hasClass("selected")) {
        $(elem).removeClass("selected");
        $(elem).find('input[type="checkbox"]').prop("checked", false);
    }
    else {
        $(elem).addClass("selected");
        $(elem).find('input[type="checkbox"]').prop("checked", true);
    }

    // здесь мы прописываем какие кнопки активны после выбора товара или товаров
    switch ($('tbody > tr.selected').length) {
        case 0:
            $("#history, #delete, #relocate, #add_photo, #remont, #send_to_trash").prop('disabled', true);
            $("#delete_user, #make_admin").addClass("disabled-btn");
            break;
        case 1:
            $("#history, #delete, #relocate, #add_photo, #remont, #send_to_trash").prop('disabled', false);
            $("#delete_user, #make_admin").removeClass("disabled-btn");
            break;
        default:
            $("#history, #add_photo, #remont").prop('disabled', true);
            $("#delete").prop('disabled', false);
            $("#make_admin").addClass("disabled-btn");
            break;
    }
}

// активность кнопок (доступна она или нет)
$(document).ready(function () {
    $("#delete_user, #make_admin").addClass("disabled-btn");
    $("#submit-photo").on("click", async function(){
        let id = $("tbody > tr.selected").children('td').eq(1).text();
        const temp = await upload_photos(id);
        window.location.reload();
    });
    $(".table-wrapper").hide().fadeIn(400);
    $("#history,#submit-photo, #delete, #relocate, #send_to_trash, #add_photo, #remont").prop('disabled', true);
    $("#add_photo").on("click", function () {
        $("#add-photo-popup").fadeIn(200);
    });
    $(".select-result").on("click", function (){
        $(this).parent().find(".select").fadeToggle(300);

    });
    $(".select-wrapper .option").on("click", function(){
        $(this).closest(".select-wrapper").find(".select-result").val($(this).find("span").html());
        $(this).parent().fadeOut(300);

    });
    $("tbody > tr").on("click", function () {
        invert_selection(this);
    });
    $("#new").on("click", function () {
        $("#new-popup").fadeIn(200);
    });
    $("#delete").on("click", function () {
        $("#delete-popup").fadeIn(200);
    });
    $("#relocate").on("click", function () {
        $("#new-geo-popup").fadeIn(200);
    });
    $(".close-btn").on("click", function () {
        $(this).closest(".popup-wrapper").fadeOut(200);
    });


    $("#history").on("click", function () {
        $("#history-popup").fadeIn(200);
        let id = $("tbody > tr.selected").children('td').eq(1).text();
        get_history(id);
    });

    $("#submit-geo").on("click", function () {
        $("tbody > tr.selected").each(async function(index){
            let id = $(this).children("td").eq(1).text();
            await update_geo({
                "material_id": id,
                "place": $('#new-geo-popup input[type="text"]').eq(0).val(),
                "client_mail": $('#new-geo-popup input[type="text"]').eq(1).val(),
                "status": $('#new-geo-popup input[type="text"]').eq(2).val(),
            });
        });
        window.location.reload();
    });


    $("#submit-delete").on("click", function () {
        $("tbody > tr.selected").each(function(index){
            let id = $(this).children('td').eq(1).text();
            del("/materials/delete", id);
        });
    });

    $("#submit-new").on("click", function () {
        if (files_to_upload.length<1){
            alert("Выберите хотя бы 1 фото");
            return;
        }
        let data = {
            "id": $('#new-popup input[type="text"]').eq(0).val(),
            "category": $('#new-popup input[type="text"]').eq(1).val(),
            "title": $('#new-popup input[type="text"]').eq(2).val(),
            "description": $('#new-popup input[type="text"]').eq(3).val(),
            "place": $('#new-popup input[type="text"]').eq(4).val(),
//            "client_mail": $('#new-popup input[type="text"]').eq(5).val()
        }
        post("/materials/create", data);
    });



    $('textarea').on('click', function (event) {
        event.stopPropagation();
    });
    $("textarea").keypress(function (e) {
        if (e.key == "Escape") {
            $('textarea').blur();
        }
        if (e.which === 13 && !e.shiftKey) {
            e.preventDefault();

            let desc = ($(this).val());
            let id = $(this).parent().parent().children('td').eq(1).text();
            update_desc({ "id": id, "description": desc });
        }
    });
    $("#select-all").change(function(){
        if (!$(this).prop("checked")){
            $('tbody > tr.selected').each(function(index){
                invert_selection(this);
            });

        }
        else{
            $('tbody > tr').not(".selected").each(function(index){
                invert_selection(this);
            });
        }
    });


});

//========================================    Методы для работы с апи


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
            temp += `<p>${json["data"][i]["place"]}:  ${json["data"][i]["date_time"]}, ${json["data"][i]["client_mail"]}</p>`
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
        const response = await fetch(host + uri+"?id_for_delete="+id, {
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

//============================== FILTERS
$('#id-filter, #category-filter, #date-filter').keyup(function (e) {
    let text0 = $('#id-filter').val();
    let text2 = $('#category-filter').val();
    let text5 = $('#date-filter').val();
    // if (e.keyCode == 13 || e.keyCode == 8) { //Раскоментировать эту
    e.preventDefault();
    $("tbody tr").show();
    $("tbody tr").each(function (index) {
        if (text0)
            if (!$(this).children('td').eq(1).text().includes(text0))
                $(this).hide();
        if (text2)
            if (!$(this).children('td').eq(3).text().includes(text2))
                $(this).hide();
        if (text5)
            if (!$(this).children('td').eq(6).text().includes(text5))
                $(this).hide();
    });

    // } //и эту строку, если активов много
});

// КОД ДЛЯ ЗАГРУЗКИ ФОТО

$('.input-file input[type=file]').on('change', function () {
    files_to_upload = [];
    if(this.files.length>0){
        files_to_upload = this.files;
        $(this).next().html("Выбрано " + files_to_upload.length + " фото");
        $("#submit-photo").prop("disabled", false);
    }else{
        $(this).next().html("Выбрать фото");
        $("#submit-photo").prop("disabled", true);
    }
});
$('.input-file span').contextmenu(function() {
    return false;
});
$('.input-file span').mousedown(function (e) {
    if ((e.which == 3)) {
        e.preventDefault();
        files_to_upload = [];
        $(this).html("Выбрать фото");
        $("#submit-photo").prop("disabled", true);
    }
});

async function upload_photos(mat_id) {
    for (let i=0; i<files_to_upload.length; i++){
        let photo = new FormData();
        photo.append('file', files_to_upload[i]);
        try {
            const response = await fetch(host + "/materials/upload_photo?material_id="+mat_id, {
                method: 'POST',
                body: photo,
                headers: {
                    'Authorization': 'Bearer ' + access_token
                }
            });
            const json = await response.json();
            return json;
        } catch (error) {
            alert(error);
            return;
        }
    }
}

async function delete_user(username){
    try {
        const response = await fetch(host+"/auth/delete_user"+"?user_for_delete="+username, {
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
async function ping(){
    try {
        const response = await fetch(host+"/app/ping", {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
        });
        const text = await response.text();
        if (text != "ok"){
            window.location.reload();
        }
    } catch (error) {
        console.error(error);
    }
}
setInterval(ping, 5000);