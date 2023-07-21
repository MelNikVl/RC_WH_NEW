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
      console.log('Успех:', JSON.stringify(json));
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
        alert("произошла ошибка!");
        window.location.reload();
        return;
      }
    }
  }

});
// добавление файлов
