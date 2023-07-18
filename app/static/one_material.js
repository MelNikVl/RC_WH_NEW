$(document).ready(function() {
  const params = new URLSearchParams(window.location.search)
  const access_token = params.get("t");
  $("#delete").on("click", async function() {
    let data1 = $("#materials_is").text();
    let urlParams = new URLSearchParams(window.location.search);
    let access_token = urlParams.get("t");
    let url = "http://127.0.0.1:9001/materials/delete?id_for_delete=" + data1;
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
