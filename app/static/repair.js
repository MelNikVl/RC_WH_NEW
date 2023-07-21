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
            console.log(file);
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
});

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