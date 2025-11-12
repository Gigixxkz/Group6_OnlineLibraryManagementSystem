document.getElementById("registerForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const msg = document.getElementById("responseMsg");

    try {
        const response = await fetch("http://127.0.0.1:8000/register", {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        msg.textContent = result.message;
        msg.style.color = result.success ? "lightgreen" : "red";
    } catch (error) {
        msg.textContent = "An error occurred. Please try again.";
        msg.style.color = "red";
    }
});