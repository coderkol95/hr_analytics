function adjustTextareaHeight(ident) {
    const textarea = document.getElementById(ident);
    textarea.style.height = "auto"; // Reset the height to auto
    textarea.style.height = textarea.scrollHeight + "px"; // Set the height to match the content
  }

function save_parsed_resume(i) {
  var textareaValues = {
    'requisition_id': $('#requisition_id').val(),
    'name': $('#name').val(),
    'phone': $('#phone').val(),
    'email': $('#email').val(),
    'skills': $('#skills').val(),
    'education': $('#education').val(),
    'past_exp': $('#past_exp').val(),
    'certifications': $('#certifications').val(),
    'job_role': $('#job_role').val(),
    'yoe': $('#yoe').val()
};
$.ajax({
    url: '/save_parsed_resume',
    type: 'POST',
    data: JSON.stringify(textareaValues),
    contentType: "application/json",
    dataType: 'json',
    success: function(response) {
        if (response.success) {
          alert("Success!!! Candidate information is saved");
          window.location.href = '/available_candidates';
        } else {
          alert("Sorry!!! Unable to save the candidate information.");
          window.location.href = '/parse_resume';
        }
      },
      error: function(error) {
        // Handle the error response if needed
        alert("Error!!! Unable to save the Job");
      }
    });
}
  

 // JavaScript to handle the dropdown selection and send the data to the backend
 document.getElementById('optionSelect').addEventListener('change', function(event) {
  event.preventDefault();
  const selectedOption = this.value;
  fetch('/parse_resume', {
      method: 'POST',
      body: new URLSearchParams({
          'selected_option': selectedOption
      }),
      headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
      }
  }).then(response => {
      if (response.ok) {
          return response.text();
      }
      throw new Error('Network response was not ok.');
  }).then(responseText => {
      console.log(responseText);
  }).catch(error => {
      console.error('Error:', error);
  });
});