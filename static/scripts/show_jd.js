// document.addEventListener("DOMContentLoaded", () => {
//     const tableBody = document.getElementById("table-body");
//     const nextBtn = document.getElementById("next-btn");
//     let currentPage = 1;
  
//     function loadData(page) {
//       fetch(`/show_jd/${page}`)
//         .then(response => response.json())
//         .then(data => {
//           tableBody.innerHTML = "";
//           data.forEach(row => {
//             const tr = document.createElement("tr");
//             tr.innerHTML = `
//               <td><input type="radio" name="select-row"></td>
//               <td>${row.requisition_id}</td>
//               <td>${row.jd}</td>
//               <td title="${row.jd_improvements}">${row.jd_improvements}</td>
//               <td title="${row.jd_score}">${row.jd_score}</td>
//             `;
//             tableBody.appendChild(tr);
//           });
//         })
//         .catch(error => console.error(error));
//     }
  
//     nextBtn.addEventListener("click", () => {
//       currentPage++;
//       loadData(currentPage);
//     });
  
//     // Initial data load
//     loadData(currentPage);
//   });

  // document.addEventListener('DOMContentLoaded', function () {
  //   const cells = document.querySelectorAll('td');
  
  //   cells.forEach(function (cell) {
  //     const originalContent = cell.innerHTML;
  //     const truncatedContent = originalContent.split(' ').slice(0, 80).join(' '); // Show only the first 80 words
  
  //     if (originalContent !== truncatedContent) {
  //       cell.innerHTML = truncatedContent + '...'; // Add ellipsis if the text is truncated
  //       cell.setAttribute('data-original-content', originalContent); // Store the full text in a data attribute
  //     }
  //   });
  
  //   const editButtons = document.querySelectorAll('.edit-button');
  
  //   editButtons.forEach(function (button) {
  //     button.addEventListener('click', function () {
  //       const cell = button.closest('td');
  //       const originalContent = cell.getAttribute('data-original-content');
        
  //       if (originalContent) {
  //         cell.innerHTML = originalContent; // Show the full text
  //         cell.removeAttribute('data-original-content'); // Remove the data attribute
  //       }
  //     });
  //   });
  // });
  

function editRow(button) {
  const row = button.parentElement.parentElement;
  const cells = row.cells;

  // Enable contenteditable for all cells except the last one (which contains the buttons)
  for (let i = 0; i < cells.length - 1; i++) {
    cells[i].contentEditable = true;
  }

  // Toggle buttons display
  button.style.display = "none";
  row.querySelector("button.btn-success").style.display = "block";
}

function saveRow(button) {
  const row = button.parentElement.parentElement;
  const cells = row.cells;
  const req_id = cells[0].innerHTML;
  const jd = document.getElementById('jd').title;
  const improvements =  document.getElementById('jd_improvement').title;
  const score = cells[3].innerHTML;

  // Disable contenteditable for all cells except the last one (which contains the buttons)
  for (let i = 0; i < cells.length - 1; i++) {
    cells[i].contentEditable = false;
  }

  // Toggle buttons display
  button.style.display = "none";
  row.querySelector("button.btn-primary").style.display = "block";
  // Create an object with the data to be sent to the backend
  const data = {
    req_id:req_id,
    jd:jd,
    improvements: improvements,
    score: score
  };

  // Make an AJAX request to the Flask backend to save the data
  fetch('/score_jd', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  .then(response => response.json())
  .then(result => {
    console.log(result.message);
  })
  .catch(error => {
    console.error('Error:', error);
  });
};

function adjustTextareaHeight(ident) {
  const textarea = document.getElementById(ident);
  textarea.style.height = "auto"; // Reset the height to auto
  textarea.style.height = textarea.scrollHeight + "px"; // Set the height to match the content
};
