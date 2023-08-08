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

  document.addEventListener('DOMContentLoaded', function () {
    const cells = document.querySelectorAll('td');

    cells.forEach(function (cell) {
      const originalContent = cell.innerHTML;
      const truncatedContent = originalContent.split(' ').slice(0, 80).join(' '); // Show only the first 200 words

      if (originalContent !== truncatedContent) {
        cell.innerHTML = truncatedContent + '...'; // Add ellipsis if the text is truncated
        cell.setAttribute('title', originalContent); // Set the full text as a tooltip
      } else {
        cell.removeAttribute('title'); // Remove the tooltip attribute if the text is not truncated
      }
    });
  });
  