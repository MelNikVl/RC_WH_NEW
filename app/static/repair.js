$(document).ready(function () {
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