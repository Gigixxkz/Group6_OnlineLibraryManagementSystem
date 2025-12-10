// Shared navbar renderer and logic (role-based links + logout)
function renderNavbar() {
  // Shared navbar markup used across pages
  return `
    <nav class="navbar navbar-expand-lg navbar-dark" style="background-color:#5a0033;">
      <div class="container-fluid">
        <a class="navbar-brand fw-bold fs-3" href="/static/HTML/HomePage.html">Archive of Light Library</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarUser" aria-controls="navbarUser" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarUser">
          <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
            <li class="nav-item"><a class="nav-link fs-5" href="/static/HTML/HomePage.html" data-nav="home">Home</a></li>
            <li class="nav-item"><a class="nav-link fs-5" href="/static/HTML/SearchBooks.html" data-nav="search">Search Books</a></li>
            <li class="nav-item" id="yourborrowed"><a class="nav-link fs-5" href="/static/HTML/YourBorrowedBooks.html" data-nav="history">Borrowing History</a></li>
            <li class="nav-item d-none" id="navBooksInventory">
              <a class="nav-link fs-5" href="/static/HTML/BooksInventory.html" data-nav="inventory">Books Inventory</a>
            </li>
            <li class="nav-item d-none" id="borroewedbooksmonitoring">
              <a class="nav-link fs-5" href="/static/HTML/BorrowedBooksMonitoring.html" data-nav="monitoring">Borrowed Books Monitoring</a>
            </li>
            <li class="nav-item position-relative">
              <a class="nav-link fs-4" href="#" id="finesBell">
                🔔
                <span id="finesBadge" 
                      class="position-absolute top-0 start-100 translate-middle p-1 bg-danger text-white rounded-circle d-none"
                      style="font-size: 0.7rem; font-weight: bold;">
                  !
                </span>
              </a>
            </li>
            <li class="nav-item"><a class="nav-link fs-5" href="#" id="logoutLink">Logout</a></li>
          </ul>
        </div>
      </div>
    </nav>
  `;
}

function renderGlobalModals() {
  return `
    <!-- FINES MODAL -->
    <div class="modal fade" id="finesModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">

          <div class="modal-header" style="background-color:#5a0033; color:white;">
            <h5 class="modal-title">Unpaid Fines</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body text-dark" id="finesModalBody">
            <p class="text-center text-muted">Loading fines...</p>
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>

        </div>
      </div>
    </div>
  `;
}

function markActiveNavLink() {
  // Highlight the current page based on URL
  const path = (window.location.pathname || "").toLowerCase();
  const map = [
    { key: "home", match: "homepage.html" },
    { key: "search", match: "searchbooks.html" },
    { key: "history", match: "yourborrowedbooks.html" },
    { key: "inventory", match: "booksinventory.html" },
    { key: "monitoring", match: "borrowedbooksmonitoring.html" },
  ];
  for (const { key, match } of map) {
    if (path.includes(match)) {
      const link = document.querySelector(`[data-nav="${key}"]`);
      if (link) link.classList.add("active");
      break;
    }
  }
}

async function loadSessionAndWireNav() {
  // Show/hide role-based items
  try {
    const res = await fetch("/session/me", { credentials: "include" });
    if (res.ok) {
      const data = await res.json();
      const role = (data.role || "").toLowerCase();
      if (role === "admin" || role === "librarian") {
        const item = document.getElementById("navBooksInventory");
        const item2 = document.getElementById("yourborrowed");
        const item3 = document.getElementById("borroewedbooksmonitoring");
        if (item) item.classList.remove("d-none");
        item2.classList.add("d-none");
        if (item3) item3.classList.remove("d-none");
      }
    }
  } catch (err) {
    console.error("Session check failed", err);
  }
}

async function checkUserFines() {
  try {
    const res = await fetch("/getfines", { credentials: "include" });
    if (!res.ok) return;

    const fines = await res.json(); // ← expects: [{id, amount, status, book_title, due_date}, ...]

    const badge = document.getElementById("finesBadge");
    if (fines.length > 0) {
      badge.classList.remove("d-none");
    } else {
      badge.classList.add("d-none");
    }

    // Save fines for modal use
    window._userFines = fines;

  } catch (err) {
    console.error("Error checking fines:", err);
  }
}
//
function setupFinesBellClick() {
  const bell = document.getElementById("finesBell");
  const modalBody = document.getElementById("finesModalBody");
  const finesModal = new bootstrap.Modal(document.getElementById("finesModal"));

  bell.addEventListener("click", () => {
    const fines = window._userFines || [];

    if (fines.length === 0) {
      modalBody.innerHTML = `
        <p class="text-center text-success fs-4">You have no unpaid fines</p>
      `;
    } else {
      modalBody.innerHTML = fines.map(f => `
        <div class="border rounded p-3 mb-2">
          <div><strong>Book:</strong> ${f.book_title}</div>
          <div><strong>Amount:</strong> €${f.amount.toFixed(2)}</div>
          <div><strong>Due:</strong> ${f.due_date}</div>
          <div><strong>Status:</strong> ${f.status}</div>
        </div>
      `).join("");
    }

    finesModal.show();
  });
}

  // Logout handler
  const logoutLink = document.getElementById("logoutLink");
  if (logoutLink) {
    logoutLink.addEventListener("click", async (event) => {
      event.preventDefault();
      try {
        await fetch("/logout", { method: "POST", credentials: "include" });
      } catch (err) {
        console.error("Logout error", err);
      } finally {
        window.location.href = "/static/HTML/UserLogin.html";
      }
    });
  }


document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("navbar-container");
  if (!container) return;
  //render navbar
  container.innerHTML = renderNavbar();
  //render modal
  const modalContainer = document.getElementById("global-modals");
  if (modalContainer) {
    modalContainer.innerHTML = renderGlobalModals();
  }

  markActiveNavLink();
  loadSessionAndWireNav();

  checkUserFines();
  setupFinesBellClick();
});
