function adjustTextareaHeight(ident) {
    const textarea = document.getElementById(ident);
    textarea.style.height = "auto"; // Reset the height to auto
    textarea.style.height = textarea.scrollHeight + "px"; // Set the height to match the content
  }

function save_parsed_resume(i) {



  var textareaValues = {
    'name': $('#name').val(),
    'phone': $('#phone').val(),
    'email': $('#email').val(),
    'skills': $('#skills').val(),
    'education': $('#education').val(),
    'past_exp': $('#past_exp').val(),
    'certifications': $('#certifications').val()
};

$.ajax({
    url: '/save_parsed_resume',
    type: 'POST',
    data: JSON.stringify(textareaValues),
    contentType: "application/json",
    dataType: 'json'
});
  }