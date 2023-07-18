$(document).ready(function() {
  const params = new URLSearchParams(window.location.search)
  const access_token = params.get("t");
  let material_id = window.location.href.split("/").pop().split("?")[0];
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


// событие по клику

$("#relocate").on("click", function () {
  $("#new-geo-popup").fadeIn(200);
});
$("#submit-geo").on("click", async function () {
    let material_id = window.location.href.split("/").pop().split("?")[0];
      await update_geo({
          "material_id": material_id,
          "place": $('#new-geo-popup input[type="text"]').eq(0).val(),
          "client_mail": $('#new-geo-popup input[type="text"]').eq(1).val(),
          "status": $('#new-geo-popup input[type="text"]').eq(2).val(),
      });
      try {
        const response = await $.ajax({
          url: url,
          method: "POST",
          contentType: "application/json",
          headers: {
            'Authorization': 'Bearer ' + access_token
          },
          body: JSON.stringify(data),
        });
        console.log(response);
        // Обработка успешного удаления товара
      } catch (error) {
        console.error(error);
        // Обработка ошибки удаления товара
      }
  });
  // window.location.reload();
