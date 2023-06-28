function adjustTextareaHeight(ident) {
    const textarea = document.getElementById(ident);
    textarea.style.height = "auto"; // Reset the height to auto
    textarea.style.height = textarea.scrollHeight + "px"; // Set the height to match the content
  }

function save_parsed_resume(i) {

// Send all fields
  var job_desc = document.getElementById("requisition_id");
  $.ajax({
    type: 'POST',
    url: '/parse_resume',
    data: JSON.stringify(job_desc.value),
    contentType: "application/json",
    dataType: 'json'
  });
  }