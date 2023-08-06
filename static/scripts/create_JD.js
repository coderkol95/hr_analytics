function adjustTextareaHeight(ident) {
    const textarea = document.getElementById(ident);
    textarea.style.height = "auto"; // Reset the height to auto
    textarea.style.height = textarea.scrollHeight + "px"; // Set the height to match the content
  }

function save_job_desc(requisition_id) {

  var req_id = requisition_id;
  var job_desc = document.getElementById("generated_job_desc").value;
  
  var dataToSend = {
    requisition_id: req_id,
    job_description: job_desc
  };

  $.ajax({
    type: 'POST',
    url: '/save_job_desc',
    data: JSON.stringify(dataToSend),
    contentType: "application/json",
    dataType: 'json',
    // success: function(response) {
    //   if (response.success) {
    //     alert("Success!!! Job description is saved.");
    //   } else {
    //     alert("Success!!! Job description updated and saved.");
    //   }
    // },
    // error: function(error) {
    //   // Handle the error response if needed
    //   alert("Error!!! Unable to save the Job");
    // }
  });
}