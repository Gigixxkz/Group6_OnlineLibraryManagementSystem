(async () => {
  try {
    const res = await fetch("/session/me", { credentials: "include" });
    if (!res.ok) return; // not logged in or session missing
    const data = await res.json();
    const role = (data.role || "").toLowerCase();
    if (role === "admin" || role === "librarian") {
      const item = document.getElementById("navBooksInventory");
      if (item) item.classList.remove("d-none");
    }
  } catch (err) {
    console.error("Session check failed", err);
  }
})();

// Handle logout click: call backend logout, then redirect to login page
document.addEventListener("DOMContentLoaded", () => {
  const logoutLink = document.getElementById("logoutLink");
  if (!logoutLink) return;

  logoutLink.addEventListener("click", async (event) => {
    event.preventDefault();
    try {
      const res = await fetch("/logout", {
        method: "POST",
        credentials: "include",
      });
      if (!res.ok) {
        console.error("Logout failed", res.status);
      }
    } catch (err) {
      console.error("Logout error", err);
    } finally {
      window.location.href = "/static/HTML/UserLogin.html";
    }
  });
});
