function uploadPDF() {
    var pdfFile = document.getElementById('pdf-file').files[0];
    
    var formData = new FormData();
    formData.append('pdf_file', pdfFile);

    fetch('/parse_resume', {
        method: 'POST',
        body: formData
    })
    .then(function(response) {
        return response.text();
    })
    .then(function(message) {
        document.getElementById('output').textContent = message;
    });
}
