console.log("A: SCRIPT STARTED");

document.addEventListener("DOMContentLoaded", () => {
    console.log("A1: DOM FINISHED LOADING");

const form = document.getElementById("registerForm");
console.log("B: FORM FOUND:", form);

form.addEventListener("submit", async function(e) {
    console.log("C: SUBMIT HANDLER CALLED");
    e.preventDefault();

    const formData = new FormData(this);
    const msg = document.getElementById("responseMsg");

    try {
        const response = await fetch("http://127.0.0.1:8000/register", {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        console.log("D: SUCCESS VALUE:", result.success);
        console.log("E: MESSAGE VALUE:", result.message);

        
        //msg.textContent = result.message;
        msg.innerHTML = `
            <div class="alert ${result.success ? 'alert-success' : 'alert-danger'} fw-bold fs-5" role="alert">
                ${result.message}
            </div>
        `;

        if (result.success) {
            console.log("F: Redirect should happen now.");
            setTimeout(() => {
                console.log("G: Redirecting...");
                window.location.href = "UserLogin.html"; 
            }, 3000);
        }

    } catch (error) {
        console.log("H: ERROR:", error);
        msg.textContent = "An error occurred. Please try again.";
        msg.style.color = "red";
    }
});
});
