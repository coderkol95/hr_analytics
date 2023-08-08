function adjustTextareaHeight(ident) {
    const textarea = document.getElementById(ident);
    textarea.style.height = "auto"; // Reset the height to auto
    textarea.style.height = textarea.scrollHeight + "px"; // Set the height to match the content
  }

//   document.addEventListener("DOMContentLoaded", function() {
//     const dropdown = document.getElementById("optionSelect2");
//     const resultInput = document.getElementById("job_desc");

//     dropdown.addEventListener("change", function() {
//         const selectedOption = dropdown.value;

//         fetch(`/get_dropdown_result?selected_option=${selectedOption}`)
//             .then(response => response.json())
//             .then(data => {
//                 resultInput.value = data.response;
//             })
//             .catch(error => console.error(error));
//     });
// });

document.getElementById('optionSelect2').addEventListener('change', function() {
  const selectedOption = this.value;

  fetch('/get_dropdown_result', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({
          selected_option: selectedOption
      })
  })
  .then(response => response.json())
  .then(data => {
      document.getElementById('job_desc').value = data.response;
  })
  .catch(error => {
      console.error('Error:', error);
  });
});


function toggleDropdown() {
  var dropdownContent = document.getElementById("myDropdown");
  dropdownContent.style.display = dropdownContent.style.display === "block" ? "none" : "block";
}