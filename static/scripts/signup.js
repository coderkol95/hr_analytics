document.getElementById("signup-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const form = event.target;
    const data = new FormData(form);
    const requestData = {
        method: "POST",
        body: data,
    };

    fetch("/signup", requestData)
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                alert(data.message);
                window.location.href = "/"; // Redirect to the login page after successful sign-up
            } else {
                alert(data.message);
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
});
