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
    const req_id = cells[0].innerText;
    const name = cells[1].innerText;
    const email = cells[2].innerText;
    const phoneNumber = cells[3].innerText;
    const status = cells[4].innerText;
    const test_score = cells[5].innerText;
    const interview_score = cells[6].innerText;
  
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
      name: name,
      email: email,
      phone: phoneNumber,
      status:status,
      test_score:test_score,
      interview_score:interview_score
    };
  
    // Make an AJAX request to the Flask backend to save the data
    fetch('/save_journey', {
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
  }