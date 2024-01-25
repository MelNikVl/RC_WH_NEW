const params = new URLSearchParams(window.location.search)
const access_token = params.get("t");
const host = window.location.origin;
const material_id = window.location.href.split("/").pop().split("?")[0];
var files_to_upload = [];

// КНОПКИ
// удаление актива - кнопка
$(document).ready(function () {
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
  let url = host + "/materials/delete?id_for_delete=" + material_id;
  $("#delete").on("click", async function () {
    // Выводим предупреждение
    if (!confirm("Вы точно хотите удалить этот актив?")) {
      return; // Отменяем удаление, если пользователь нажал "Отмена"
    }
    try {
      const response = await $.ajax({
        url: url,
        method: "DELETE",
        contentType: "application/json",
        headers: {
          'Authorization': 'Bearer ' + access_token
        },
      });
      console.log(response);
      window.location.href = host + "/app?t=" + access_token;
      // Обработка успешного удаления товара
    } catch (error) {
      console.error(error);
      // Обработка ошибки удаления товара
    }
  });

  // перемещение
  $("#relocate").on("click", function () {
    $("#new-geo-popup").fadeIn(200);
  });
  $("#submit-geo").on("click", async function () {
    $("#loader-geo").fadeIn(300);
    try {
      let data = {
        "material_id": material_id,
        "place": $('#new-geo-popup input[type="text"]').eq(0).val(),
        "client_mail": $('#new-geo-popup input[type="text"]').eq(1).val(),
        "status": $('#new-geo-popup input[type="text"]').eq(2).val(),
      };
      const response = await fetch(host + "/geolocation/create", {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + access_token
        }
      });
      const json = await response.json();
      if (!json["status"]) {
        alert("Ошибка! Возможно вы ввели некорректные данные");
      }
      window.location.reload();
      $("#new-geo-popup").fadeOut(200);
    } catch (error) {
      console.log(error);
    }
  });
  $(".close-btn").on("click", function () {
    $(this).closest(".popup-wrapper").fadeOut(200);
  });
  $("#submit-photo").on("click", async function () {
    const resp = await upload_photos(material_id);
    if (resp["status"])
      window.location.reload()
    else {
      alert("Фото не добавлено!");
      window.location.reload();
    }
  });
  $("#fast_repair").on("click", function () {
    $("#fast-repair-popup").fadeIn(200);
  });
  $("#add_photo").on("click", function () {
    $("#add-photo-popup").fadeIn(200);
  });
  $("#submit-short-repair").on("click", async function () {
    let problem = $("#fast-repair-popup textarea").val();
    let customer = $("#fast-repair-popup input").eq(0).val();
    if (customer && problem) {
      const data = {
        "material_id": material_id,
        "problem": problem,
        "customer": customer
      };
      let file = $("#short-repair-file")[0].files[0];
      await short_repair(data, file);
    }
  });
  $("#move_to_trash").on("click", async function () {
    if (confirm('Вы уверены, что хотите добавить к списку на списание данные активы? Это действие будет уже не отменить')) {
      await move_to_trash(material_id);
      window.location.reload();
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
        alert("произошла ошибка в комментариях, раздел с авторизацией!");
        window.location.reload();
        return;
      }
    }
  }
  async function send_comment(text) {
    let data = {
      "material_id": material_id,
      "text": text
    };
    try {
      const response = await fetch(host + "/materials/send_comment", {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
          'Authorization': 'Bearer ' + access_token,
          "Content-Type": "application/json"
        }
      });
      const json = await response.json();
      return json;
    } catch (error) {
      alert("произошла ошибка!");
      window.location.reload();
      return;
    }
  }
  $("#send_comment").on("click", async () => {
    if (!confirm("Вы действительно хотите отправить коммментарий?")) return;
    let text = $("#comment-text").val();
    if (text) {
      let res = await send_comment(text);
      if (!res["status"]) {
        alert("Произошла ошибка! комментарии, запись в бд");
      }
      location.reload()
    }
  });
  $("#update-1c-geo").on("click", async () => {
    try {
      const response = await fetch(host + "/geolocation/refresh_1c?id=" + material_id, {
        method: 'PUT',
        headers: {
          'Authorization': 'Bearer ' + access_token,
          "Content-Type": "application/json"
        }
      });
      const json = await response.json();
      if (!json["status"]) {
        alert("произошла ошибка!");
      }
      window.location.reload();
    } catch (error) {
      alert("произошла ошибка!");
      window.location.reload();

    }
  });
  $("#send_to_repair").on("click", function () {
    $("#add-to-repair-popup").fadeIn(300);
  });
  $("#submit-repair").on("click", function () {
    let customer = $("#add-to-repair-popup input").val();
    let problem = $("#add-to-repair-popup textarea").val();
    if (customer && problem) {
      const data = {
        "material_id": material_id,
        "problem": problem,
        "customer": customer
      };
      move_to_repair(data);
    }
    else {
      alert("Заполните все поля!");
    }
  });
  $("#end_repair").on("click", function () {
    $("#repair-end-popup").fadeIn(300);
  });
  $("#submit-repair-end").on("click", function () {
    let solution = $("#repair-end-popup textarea").val();
    let customer = $("#repair-end-popup input").eq(0).val();
    let place = $("#repair-end-popup input").eq(1).val();
    let status = $("#repair-end-popup input").eq(2).val();
    if (solution) {
      const data = {
        "material_id": material_id,
        "solution": solution,
        "customer": customer,
        "place": place,
        "status": status
      };
      $("#submit-repair-end").prop("disabled", true);
      move_from_repair(data);
    }
    else {
      alert("Заполните все поля!");
    }
  });

});