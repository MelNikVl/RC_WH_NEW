$(document).ready(function () {
    $("#send-to-trash-finally").prop("disabled", true);
    $("#send-to-trash-finally").on("click", async function () {
        if (confirm("Вы действительно хотите списать все активы из списка?")) {
            let form_data = new FormData();
            $.each($("#upload-trashing-photos")[0].files, function (key, input) {
                form_data.append('photos', input);
            });
            form_data.append('invoice', $("#upload-invoice")[0].files[0]);
            send_to_trash_finally(form_data);
        }
    });
    let form_changed = function () {
        let trashing = $("#upload-trashing-photos")[0].files.length;
        let invoice = $("#upload-invoice")[0].files.length;
        if (trashing && invoice)
            $("#send-to-trash-finally").prop("disabled", false);
        else
            $("#send-to-trash-finally").prop("disabled", true);

    };
    $("#move_to_archive").on("click", function () {
        $("#trash-popup").fadeIn(300);
    });
    $("input[type='file']").change(function () {
        let file_count = $(this)[0].files.length;
        $(this).siblings("label").text("Выбрано: " + file_count);
        form_changed();
    });
    $("#form_file").on("click", function () {
        let data = { "data": [] };
        let counter = 1;
        $('tbody > tr').each(function (index) {
            let id = $(this).children("td").eq(0).text();
            let category = $(this).children("td").eq(2).text();
            let title = $(this).children("td").eq(3).text();
            let description = $(this).children("td").eq(4).children("textarea").val();
            let date = $(this).children("td").eq(5).text();
            data["data"].push([counter, id, category, title, description, date]);
            counter++;
        });
        download(data);

    });
});
async function download(data) {
    try {
        const response = await fetch(host + "/materials/invoice", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            },
            body: JSON.stringify(data),
        });
        const blob = await response.blob();
        saveAs(blob, "Накладная.docx");
        // window.location.reload();
    } catch (error) {
        console.error(error);
    }
}
async function send_to_trash_finally(form_data) {
    try {
        const response = await fetch(host + "/geolocation/send_to_trash_finally", {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + access_token
            },
            body: form_data,
        });
        const json_response = await response.json();
        if (json_response["status"] == true) {
            alert("Активы были успешно списаны!");
        } else {
            alert("Произошла ошибка!");

        }
        window.location.reload();
    } catch (error) {
        alert("Произошла ошибка!");
    }
}
