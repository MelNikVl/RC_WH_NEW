
const params = new URLSearchParams(window.location.search)
const access_token = params.get("t");
const material_id = window.location.href.split("/").pop().split("?")[0];


// КНОПКИ
// удаление актива - кнопка
$(document).ready(function() {
  let url = window.location.origin + "/materials/delete?id_for_delete=" + material_id;
  $("#delete").on("click", async function() {
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
      window.location.href = window.location.origin+"/app?t="+access_token;
      // Обработка успешного удаления товара
    } catch (error) {
      console.error(error);
      // Обработка ошибки удаления товара
    }
  });
});

// перемещение
$("#relocate").on("click", function () {
  $("#new-geo-popup").fadeIn(200);
});
$("#submit-geo").on("click", async function () {
    await update_geo({
        "material_id": material_id,
        "place": $('#new-geo-popup input[type="text"]').eq(0).val(),
        "client_mail": $('#new-geo-popup input[type="text"]').eq(1).val(),
        "status": $('#new-geo-popup input[type="text"]').eq(2).val(),
    });
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
  });
  // window.location.reload();

// добавление файлов
