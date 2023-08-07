// // Keep track of the current page number
// let currentPage = 1;
// // Number of entries to show per page
// const entriesPerPage = 5;

// // Function to show the next set of entries
// function showNextEntries() {
//   const rows = document.querySelectorAll('.data-table tbody tr');
//   const maxPages = Math.ceil(rows.length / entriesPerPage);
//   if (currentPage < maxPages) {
//     const startIndex = (currentPage - 1) * entriesPerPage;
//     const endIndex = startIndex + entriesPerPage;
//     rows.forEach((row, index) => {
//       if (index >= startIndex && index < endIndex) {
//         row.style.display = 'table-row';
//       } else {
//         row.style.display = 'none';
//       }
//     });
//     currentPage++;
//   }
// }


document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.getElementById("table-body");
    const nextBtn = document.getElementById("next-btn");
    let currentPage = 1;
  
    function loadData(page) {
      fetch(`/available_candidates/${page}`)
        .then(response => response.json())
        .then(data => {
          tableBody.innerHTML = "";
          data.forEach(row => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
              <td><input type="radio" name="select-row"></td>
              <td>${row.Name}</td>
              <td>${row.Age}</td>
              <td title="${row.Email}">${row.Email}</td>
              <td title="${row.Location}">${row.Location}</td>
            `;
            tableBody.appendChild(tr);
          });
        })
        .catch(error => console.error(error));
    }
  
    nextBtn.addEventListener("click", () => {
      currentPage++;
      loadData(currentPage);
    });
  
    // Initial data load
    loadData(currentPage);
  });
  