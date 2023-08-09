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


  function sendEmail(button) {
    const email = button.getAttribute("data-email");
    
    // Send an AJAX request to the Flask backend to handle sending the email
    fetch('/send_round2_email', {
      method: 'POST',
      body: JSON.stringify({ email }), // Sending the email data
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(response => {
      if (response.ok) {
        // Email sent successfully
        console.log('Email sent');
        alert('Email is sent to the candidate')
      } else {
        // Handle error
        console.error('Error sending email');
      }
    }).catch(error => {
      console.error('Error sending email', error);
    });
  }
  
  // Update button states based on test scores
  document.addEventListener("DOMContentLoaded", function() {
    const rows = document.querySelectorAll("#table-body tr");
    rows.forEach(row => {
      const testScore = parseFloat(row.querySelector("td:nth-child(6)").textContent);
      console.log(testScore)
      const emailButton = row.querySelector(".send-email");
      
      if (Number(testScore) >= 20) {
        emailButton.removeAttribute("disabled");
      }
    });
  });


// const interviewScoreCells = document.querySelectorAll('.interview-score');

// interviewScoreCells.forEach(cell => {
//   const interviewScore = parseInt(cell.getAttribute('data-score'));

//   if (interviewScore >= 20) {
//     cell.innerHTML = '<span class="score-pass">Pass</span>';
//     cell.style.color = 'green';
//   } else {
//     cell.innerHTML = '<span class="score-fail">Fail</span>';
//     cell.style.color = 'red';
//   }
// });