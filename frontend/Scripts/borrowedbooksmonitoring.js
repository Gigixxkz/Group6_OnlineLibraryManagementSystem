//------------------------------------------------------------
// File: BorrowedBooksMonitoring.js
//  created by andreas andreou
// date:12 december 2025
// ------------------------------------------------------------

const API_BASE = "http://127.0.0.1:8000"; // backend URL
let borrowedBooks = [];
let selectedBorrowId = null;

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    loadBorrowedBooks();

    document.getElementById("searchBtn")
        .addEventListener("click", renderTable);

    document.getElementById("confirmReturnBtn")
        .addEventListener("click", confirmReturn);
});

// ------------------------------------------------------------
// Fetch borrowed books from backend
// ------------------------------------------------------------
async function loadBorrowedBooks() {
    try {
        const res = await fetch(`${API_BASE}/borrowedbooksmonitoring/all`, {
            credentials: "include"
        });
        console.log("Fetch response:", res);

        if (!res.ok) {
            const text = await res.text();
            throw new Error(`HTTP ${res.status}: ${text}`);
        }

        const data = await res.json();
        console.log("Data received:", data);

        borrowedBooks = data.borrowed_books || [];
        renderTable();
    } catch (err) {
        console.error("Failed to load borrowed books:", err);
        const tbody = document.getElementById("borrowedBooksTableBody");
        tbody.innerHTML = `<tr><td colspan="7" class="text-center">Failed to load data</td></tr>`;
    }
}



// ------------------------------------------------------------
// Render table
// ------------------------------------------------------------
function renderTable() {
    const tbody = document.getElementById("borrowedBooksTableBody");
    const search = document.getElementById("searchInput").value.toLowerCase();
    tbody.innerHTML = "";

    borrowedBooks
        .filter(r =>
            r.user.toLowerCase().includes(search) ||
            r.title.toLowerCase().includes(search) ||
            r.isbn.toLowerCase().includes(search) ||
            r.status.toLowerCase().includes(search)
        )
        .forEach(r => {
            const statusClass = r.status === "overdue" ? "overdue" : "";
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${r.user}</td>
                <td>${r.title}</td>
                <td>${r.isbn}</td>
                <td>${r.borrow_date}</td>
                <td>${r.due_date}</td>
                <td class="${statusClass}">${r.status}</td>
                <td>
                    <button class="btn btn-return btn-sm" onclick="openReturnModal(${r.id})">
                        Return
                    </button>
                </td>
            `;

            tbody.appendChild(tr);
        });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center">No records found</td></tr>`;
    }
}

// ------------------------------------------------------------
// Open return modal
// ------------------------------------------------------------
function openReturnModal(borrowId) {
    selectedBorrowId = borrowId;
    new bootstrap.Modal(document.getElementById("returnModal")).show();
}

// ------------------------------------------------------------
// Confirm return
// ------------------------------------------------------------
async function confirmReturn() {
    if (!selectedBorrowId) return;

    try {
        const res = await fetch(`${API_BASE}/borrowedbooksmonitoring/return/${selectedBorrowId}`, {
            method: "POST",
            credentials: "include"
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to return book");

        selectedBorrowId = null;
        bootstrap.Modal.getInstance(document.getElementById("returnModal")).hide();
        await loadBorrowedBooks();
    } catch (err) {
        console.error("Error returning book:", err);
        alert(err.message);
    }
}
