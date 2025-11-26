   const API_BASE = "http://127.0.0.1:8000"; // backend URL
    let books = [];
    let bookToRemove = null;

    // Load all books
    async function loadBooks() {
      try {
        const res = await fetch(`${API_BASE}/books/all`);
        const data = await res.json();
        books = data.books;
        renderBooks();
      } catch (err) {
        console.error("Failed to load books:", err);
      }
    }

    // Render book table
    function renderBooks() {
      const tbody = document.getElementById("bookTableBody");
      const search = document.getElementById("searchInput").value.toLowerCase();
      tbody.innerHTML = "";

      books.filter(b => 
        b.isbn.toLowerCase().includes(search) ||
        b.title.toLowerCase().includes(search) ||
        b.author.toLowerCase().includes(search)
      ).forEach(book => {
        const row = document.createElement("tr");
        if (!book.available) row.classList.add("removed");

        row.innerHTML = `
          <td>${book.isbn}</td>
          <td>${book.title}</td>
          <td>${book.author}</td>
          <td>${book.available ? "Good" : "Removed"}</td>
          <td>${book.available ? "Available" : "Removed"}</td>
          <td>
            ${book.available 
              ? `<button class="btn btn-remove btn-sm" onclick="openRemoveModal(${book.id})">Remove</button>`
              : `<button class="btn btn-restore btn-sm" onclick="restoreBook(${book.id})">Restore</button>`}
          </td>
        `;
        tbody.appendChild(row);
      });
    }

    // Open remove modal
    function openRemoveModal(bookId) {
      bookToRemove = bookId;
      new bootstrap.Modal(document.getElementById("removeModal")).show();
    }

    // Confirm removal
    document.getElementById("confirmRemoveBtn").addEventListener("click", async () => {
      if (!bookToRemove) return;
      try {
        const res = await fetch(`${API_BASE}/books/remove/${bookToRemove}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ reason: document.getElementById("removeReason").value })
        });
        const data = await res.json();
        if (!res.ok) { alert(data.detail || "Failed to remove book"); return; }

        books = books.map(book => book.id === bookToRemove ? { ...book, available: 0 } : book);
        renderBooks();
        bootstrap.Modal.getInstance(document.getElementById("removeModal")).hide();
      } catch (err) {
        alert("Failed to remove book: " + err);
      }
    });

    // Restore book
    async function restoreBook(bookId) {
      try {
        const res = await fetch(`${API_BASE}/books/restore/${bookId}`, { method: "POST" });
        const data = await res.json();
        if (!res.ok) { alert(data.detail || "Failed to restore book"); return; }

        books = books.map(book => book.id === bookId ? { ...book, available: 1 } : book);
        renderBooks();
      } catch (err) {
        alert("Failed to restore book: " + err);
      }
    }

    // Add book
    async function addBook() {
      const form = document.getElementById("addBookForm");
      const formData = new FormData(form);

      try {
        const res = await fetch(`${API_BASE}/books/add`, { method: "POST", body: formData });
        const data = await res.json();
        if (!res.ok) { alert(data.detail || "Failed to add book"); return; }

        await loadBooks();
        form.reset();
        bootstrap.Modal.getInstance(document.getElementById("addBookModal")).hide();
      } catch (err) {
        alert("Error adding book: " + err);
      }
    }

    loadBooks();
