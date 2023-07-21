const params = new URLSearchParams(window.location.search)
const access_token = params.get("t");

var host = document.location.origin;
var files_to_upload = [];

function invert_selection(elem) {
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
            $("#history, #delete, #relocate, #add_photo, #remont, #move_to_trash, #fast_repair, #send_to_repair, #add_repair_info, #end_repair").prop('disabled', true);
            $("#delete_user, #make_admin").addClass("disabled-btn");
            break;
        case 1:
            $("#history, #delete, #relocate, #add_photo, #remont, #move_to_trash,  #fast_repair, #send_to_repair, #add_repair_info, #end_repair").prop('disabled', false);
            $("#delete_user, #make_admin").removeClass("disabled-btn");
            if ($('tbody > tr.selected').children("td").eq(7).text() == "ремонт"){
                $("#fast_repair, #send_to_repair, #relocate").prop("disabled", true);
                $("#add_repair_info, #end_repair").prop("disabled", false);
            } else{
                $("#fast_repair, #send_to_repair").prop("disabled", false);
                $("#add_repair_info, #end_repair").prop("disabled", true);
            }
            break;
        default:
            $("#history, #add_photo, #remont, #fast_repair, #send_to_repair, #add_repair_info, #end_repair").prop('disabled', true);
            $("#delete").prop('disabled', false);
            $("#make_admin").addClass("disabled-btn");
            break;
    }
}

// активность кнопок (доступна она или нет)
$(document).ready(function () {
    $("#end_repair").on("click", function(){
        $("#repair-end-popup").fadeIn(300);
    });
    $("#fast_repair").on("click", function(){
        $("#fast-repair-popup").fadeIn(300);
    });
    $("#add_repair_info").on("click", function(){
        $("#repair-details-popup").fadeIn(300);
    });
    $("#submit-short-repair").on("click", function(){
        let id = parseInt($("tbody > tr.selected td").eq(1).text());
        let problem = $("#fast-repair-popup textarea").val();
        let customer = $("#fast-repair-popup input").eq(0).val();
        if (customer && problem){
            const data = {
                "material_id": id,
                "problem": problem,
                "customer": customer
            };
            let file = $("#short-repair-file")[0].files[0];
            short_repair(data, file);
        }
        else{
            alert("Заполните все поля!");
        }
    });
    $("#submit-repair-end").on("click", function(){
        let id = $("tbody > tr.selected td").eq(1).text();
        let solution = $("#repair-end-popup textarea").val();
        let customer = $("#repair-end-popup input").eq(0).val();
        let place = $("#repair-end-popup input").eq(1).val();
        let status = $("#repair-end-popup input").eq(2).val();
        if (solution){
            const data = {
                "material_id": id,
                "solution": solution,
                "customer": customer,
                "place": place,
                "status": status
            };
            $("#submit-repair-end").prop("disabled", true);
            move_from_repair(data);
        }
        else{
            alert("Заполните все поля!");
        }
    });
    $("#send_to_repair").on("click", function(){
        $("#add-to-repair-popup").fadeIn(300);
    });
    $("#submit-repair-details").on("click", function(){
        let id = $("tbody > tr.selected td").eq(1).text();
        let details = $("#repair-details-popup textarea").val();
        if (details){
            const data = {
                "material_id": id,
                "details": details
            };
            $("#submit-repair-details").prop("disabled", true);
            add_to_repair(data);
        }
        else{
            alert("Заполните все поля!");
        }
    });
    $("#send_to_repair").on("click", function(){
        $("#add-to-repair-popup").fadeIn(300);
    });
    $("#submit-repair").on("click", function(){
        let id = $("tbody > tr.selected td").eq(1).text();
        let customer = $("#add-to-repair-popup input").val();
        let problem = $("#add-to-repair-popup textarea").val();
        if (customer && problem){
            const data = {
                "material_id": id,
                "problem": problem,
                "customer": customer
            };
            move_to_repair(data);
        }
        else{
            alert("Заполните все поля!");
        }
    });
    //Скрыть действия с активами при любом клике в окне
    $(window).click(function () {
        $(".action-buttons").fadeOut(300);
    });
    //При клике по кнопке показать действия с активами
    $("#open_actions").on("click", function (e) {
        e.stopPropagation(); //Прекратить распространение события клика на дальнейшие элементы
        $(".action-buttons").fadeToggle(300);
    });
    //Деактивация кнопок при старте страницы
    $("#delete_user, #make_admin").addClass("disabled-btn");
    $("#history, #submit-photo, #delete, #relocate, #add_photo, #remont, #move_to_trash, #fast_repair, #send_to_repair, #add_repair_info, #end_repair").prop('disabled', true);

    $("#move_to_trash").on("click", function () {
        if (confirm('Вы уверены, что хотите добавить к списку на списание данные активы? Это действие будет уже не отменить')) {
            $("tbody > tr.selected").each(async function (index) {
                let id = $(this).children("td").eq(1).text();
                await move_to_trash(id);
            });
            window.location.reload();
        }
    });
    $(".table-wrapper").hide().fadeIn(400);
    $("#submit-photo").on("click", async function () {
        let id = $("tbody > tr.selected").children('td').eq(1).text();
        const temp = await upload_photos(id);
        window.location.reload();
    });
    $("#add_photo").on("click", function () {
        $("#add-photo-popup").fadeIn(200);
    });
    $(".select-result").on("click", function () {
        $(this).parent().find(".select").fadeToggle(300);
    });

    // шаблоны типов техники при создании товара
    $("#new-popup-select").on("change", function () {
        let comp_template = 
`процессор: 
оперативная память (Gb): 
жестккий диск (Gb): 
ssd (Gb): 
блок питания (Вт) `;
        let laptop_template = 
`производитель: 
модель: 
процессор: 
оперативная память (Gb): 
жесткий диск (Gb): 
*дополнительная информация: `;
        let server_template = 
`производитель: 
модель: 
процессор: 
оперативная память (Gb): 
RAID: `;
        let switch_template = 
`производитель: 
модель: `;
        let camera_template = 
`производитель: 
модель: `;
        let other_template = ``;

        switch ($(this).val()) {
            case "Другое":
                $("#new-popup textarea").val(other_template);
                break;
            case "Компьютер":
                $("#new-popup textarea").val(comp_template);
                break;
            case "Ноутбук":
                $("#new-popup textarea").val(laptop_template);
                break;
            case "Сервер":
                $("#new-popup textarea").val(server_template);
                break;
            case "Маршрутизатор / свитч":
                $("#new-popup textarea").val(switch_template);
                break;
            case "Камера":
                $("#new-popup textarea").val(camera_template);
                break;
            default:
                $("#new-popup textarea").val(comp_template);
                break;
        }

    });
    $(".select-wrapper .option").on("click", function () {
        $(this).closest(".select-wrapper").find(".select-result").val($(this).find("span").html());
        $(this).closest(".select-wrapper").find(".select-result").trigger("change");
        $(this).parent().fadeOut(300);
    });

// событие по клику
    $("tbody > tr").on("dblclick", function () {
        if (!$(this).hasClass("inactive"))
            invert_selection(this);
    });
    $("#reset-filters").on("click", function(){
        $('#id-filter').val("");
        $('#category-filter').val("");
        $('#description-filter').val("");
        $('#date-filter').val("");
        $('#status-filter').val("");
        apply_filters();
    })

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
        $("tbody > tr.selected").each(async function (index) {
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
        $("tbody > tr.selected").each(function (index) {
            let id = $(this).children('td').eq(1).text();
            del("/materials/delete", id);
        });
    });

    $("#submit-new").on("click", function () {
        if (files_to_upload.length < 1) {
            alert("Выберите хотя бы 1 фото");
            return;
        }
        let data = {
            "id": $('#new-popup input[type="text"]').eq(0).val(),
            "category": $('#new-popup input[type="text"]').eq(1).val(),
            "title": $('#new-popup input[type="text"]').eq(2).val(),
            "description": $('#new-popup textarea').val(),
            "place": $('#new-popup input[type="text"]').eq(3).val(),
            //            "client_mail": $('#new-popup input[type="text"]').eq(5).val()
        }
        $("#submit-new").prop("disabled", true);
        $(".loader").fadeIn(100);
        post("/materials/create", data);
    });


    $('textarea').on('click', function (event) {
        event.stopPropagation();
    });
    $("tbody textarea").keypress(function (e) {
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
    $("#select-all").change(function () {
        if (!$(this).prop("checked")) {
            $('tbody > tr.selected').each(function (index) {
                invert_selection(this);
            });

        }
        else {
            $('tbody > tr').not(".selected").each(function (index) {
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

//============================== FILTERS
let apply_filters = function () {
    let text0 = $('#id-filter').val();
    let text2 = $('#category-filter').val();
    let text4 = $('#description-filter').val();
    let text5 = $('#date-filter').val();
    let text8 = $('#status-filter').val();
    // if (e.keyCode == 13 || e.keyCode == 8) { //Раскоментировать эту
    $("tbody tr").show();
    $("tbody tr").each(function (index) {
        if (text0)
            if (!$(this).children('td').eq(1).text().includes(text0))
                $(this).hide();
        if (text2)
            if (!$(this).children('td').eq(3).text().includes(text2))
                $(this).hide();
        if (text5)
            if (!$(this).children('td').eq(5).text().includes(text5))
                $(this).hide();
        if (text8)
            if (!$(this).children('td').eq(7).text().includes(text8))
                $(this).hide();
        if (text4)
            if (!$(this).find('td textarea').text().includes(text4))
                $(this).hide();
    });

    // } //и эту строку, если активов много
}
$("#status-filter").change(function () {
    apply_filters();
});
$('#id-filter, #category-filter, #date-filter, #description-filter').on("input", function (e) {
    e.preventDefault();
    apply_filters();
});

// КОД ДЛЯ ЗАГРУЗКИ ФОТО

$('.input-file input[type=file]').on('change', function () {
    files_to_upload = [];
    if (this.files.length > 0) {
        files_to_upload = this.files;
        $(this).next().html("Выбрано " + files_to_upload.length + " фото");
        $("#submit-photo").prop("disabled", false);
    } else {
        $(this).next().html("Выбрать фото");
        $("#submit-photo").prop("disabled", true);
    }
});
$('.input-file span').contextmenu(function () {
    return false;
});
$('.input-file span').mousedown(function (e) {
    if ((e.which == 3)) {
        e.preventDefault();
        files_to_upload = [];
        $(this).html("Выбрать фото");
        $('.input-file input[type=file]').val("");
        $("#submit-photo").prop("disabled", true);
    }
});

async function upload_photos(mat_id) {
    for (let i = 0; i < files_to_upload.length; i++) {
        let photo = new FormData();
        photo.append('file', files_to_upload[i]);
        try {
            const response = await fetch(host + "/materials/upload_photo?material_id=" + mat_id, {
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
setInterval(ping, 5000);