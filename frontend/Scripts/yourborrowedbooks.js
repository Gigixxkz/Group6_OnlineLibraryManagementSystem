// File: static/Scripts/yourborrowedbooks.js
const API_BASE = "http://127.0.0.1:8000";

let historyData = [];

document.addEventListener("DOMContentLoaded", () => {
  // Ensure all UI elements exist before adding listeners
  safeAddListener("applyBtn", "click", applyFilters);
  safeAddListener("resetBtn", "click", resetFilters);
  safeAddListener("searchInput", "input", applyFilters);
  safeAddListener("statusFilter", "change", applyFilters);
  safeAddListener("startDate", "change", applyFilters);
  safeAddListener("endDate", "change", applyFilters);

  loadHistory();
});

// Safe event listener helper
function safeAddListener(id, event, handler) {
  const el = document.getElementById(id);
  if (el) el.addEventListener(event, handler);
}

// Load borrowing history for the logged-in user
async function loadHistory() {
  try {
    const res = await fetch(`${API_BASE}/borrowed_books/`, {
      credentials: "include",
    });

    if (!res.ok) {
      throw new Error(`Server responded with ${res.status}`);
    }

    const data = await res.json();
    historyData = data.borrowed_books || [];

    renderBooks(historyData);
  } catch (err) {
    console.error("Error loading history:", err);
    document.getElementById("borrowedBooksContainer").innerHTML = `
      <div class="col-12">
        <div class="alert alert-danger">
          Failed to load borrowed books.<br>
          <small>${err.message}</small>
        </div>
      </div>`;
  }
}
function formatDate(dateStr) {
  if (!dateStr) return "-";
  return new Date(dateStr).toISOString().split("T")[0];
}



// Render books
function renderBooks(list) {
  const container = document.getElementById("borrowedBooksContainer");
  container.innerHTML = "";

  if (!list.length) {
    container.innerHTML = `
      <div class="col-12">
        <div class="text-center text-white-50">No borrowed books found.</div>
      </div>`;
    return;
  }

  list.forEach(item => {
    const col = document.createElement("div");
    col.className = "col-md-4";

    const card = document.createElement("div");
    card.className = "card p-3 shadow-sm bg-dark text-white";
    

    const imgTag = item.cover_image
      ? `<img src="/books/image/${item.cover_image}" class="me-3" 
             alt="${escapeHtml(item.title)}"
             style="width:64px;height:90px;object-fit:cover;border-radius:4px;">`
      : `<div class="me-3" style="width:64px;height:90px;background:#333;border-radius:4px;"></div>`;

    const badge = statusBadgeClass(item.status);

    card.innerHTML = `
      <div class="d-flex">
        ${imgTag}
        <div class="flex-grow-1">
          <h6 class="mb-1">${escapeHtml(item.title)}</h6>
          <div class="text-muted small mb-1">${escapeHtml(item.author || "")}</div>

          <div class="small mb-1">
            Borrowed: <strong>${formatDate(item.borrow_date)}</strong><br>
             Due: <strong>${formatDate(item.due_date)}</strong><br>
             Return: <strong>${formatDate(item.return_date)}</strong>
          </div>

          <div class="mb-2">
            <span class="badge ${badge}">${item.status}</span>
            <span class="badge bg-secondary">Fine: €${(item.fine_amount || 0).toFixed(2)}</span>
          </div>

          <div>${actionButtonsHtml(item)}</div>
        </div>
      </div>
    `;

    col.appendChild(card);
    container.appendChild(col);
  });
}

// Badge color mapping
function statusBadgeClass(status) {
  switch ((status || "").toLowerCase()) {
    case "active": return "bg-primary";
    case "due soon": return "bg-warning text-dark";
    case "overdue": return "bg-danger";
    case "returned": return "bg-success";
    default: return "bg-secondary";
  }
  
}

// Action buttons
function actionButtonsHtml(item) {
  if (item.status === "Returned") {
    return `<button class="btn btn-sm btn-outline-light" disabled>Returned</button>`;
  }

  let html = "";

  if (item.status === "Active" || item.status === "Due Soon") {
    html += `<button class="btn btn-sm btn-light me-2" onclick="renewBook(${item.borrowed_id})">Renew</button>`;
  }


  return html;
}

// Renew
async function renewBook(borrowedId) {
  if (!confirm("Renew this book? Borrow date will reset to today.")) return;

  try {
    const res = await fetch(`${API_BASE}/borrowed_books/renew/${borrowedId}`, {
      method: "POST",
      credentials: "include",
    });

    const data = await res.json();
    if (!res.ok) return alert(data.detail || "Failed to renew.");

    await loadHistory();
    alert("Book renewed.");
  } catch (err) {
    alert("Error: " + err.message);
  }
}




// Filters
function applyFilters() {
  let filtered = historyData.slice();

  const search = (document.getElementById("searchInput").value || "").toLowerCase();
  if (search) {
    filtered = filtered.filter(i =>
      (i.title && i.title.toLowerCase().includes(search)) ||
      (i.author && i.author.toLowerCase().includes(search))
    );
  }

  const status = document.getElementById("statusFilter").value;
  if (status !== "all") {
    filtered = filtered.filter(i => (i.status || "").toLowerCase() === status.toLowerCase());
  }

  const start = document.getElementById("startDate").value;
  const end = document.getElementById("endDate").value;

  if (start) filtered = filtered.filter(i => new Date(i.borrow_date) >= new Date(start));
  if (end) filtered = filtered.filter(i => new Date(i.borrow_date) <= new Date(end));

  renderBooks(filtered);
}

// Reset filters
function resetFilters() {
  document.getElementById("searchInput").value = "";
  document.getElementById("statusFilter").value = "all";
  document.getElementById("startDate").value = "";
  document.getElementById("endDate").value = "";
  renderBooks(historyData);
}

// Escape HTML safely
function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/[&<>\"']/g, c => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#039;"
  })[c]);
}
