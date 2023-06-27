function adjustTextareaHeight(ident) {
    const textarea = document.getElementById(ident);
    textarea.style.height = "auto"; // Reset the height to auto
    textarea.style.height = textarea.scrollHeight + "px"; // Set the height to match the content
  }

function save_job_desc() {

  var job_desc = document.getElementById("generated_job_desc");
  $.ajax({
    type: 'POST',
    url: '/save_job_desc',
    data: JSON.stringify(job_desc.value),
    contentType: "application/json",
    dataType: 'json'
  });
  }