//-----------------------------------------------------------------------------
//File: searchbooks.js
//Author: Georgia
//Description: Handles UC3 - Search & Filter Books, and prepares UC4 Borrow.
//Notes: This file is basically the brain of the SearchBooks page.
//Date Updated: 24 November 2025
//-----------------------------------------------------------------------------

//Backend base URL (same as BooksInventory.html)
//If this ever stops working, we need to make sure that our FastAPI server is actually running.
const API_BASE = "http://127.0.0.1:8000";

//This will store ALL books we fetch from the backend.
let allBooks = [];

//When user clicks "Borrow", we temporarily store the chosen book here.
let selectedBook = null;

//Helper function because document.getElementById("something") is too long to type.
const $ = (id) => document.getElementById(id);

//
async function getCurrentUser() {
    try {
        const response = await fetch(`${API_BASE}/session/me`, {
            credentials: "include"
        });

        if (!response.ok) {
            console.warn("Session check failed:", response.status);
            alert("You must be logged in to borrow books.");
            return null;
        }

        const data = await response.json();

        if (!data.user_id) {
            alert("You must be logged in to borrow books.");
            return null;
        }

        return data.user_id;

    } catch (error) {
        console.error("Session fetch failed:", error);
        alert("Error checking login status.");
        return null;
    }
}

//-----------------------------------------------------------------------------
//Loading books from the backend
//-----------------------------------------------------------------------------
async function loadBooks() {
    try {
        //Asking the backend nicely for all books in the database
        const response = await fetch(`${API_BASE}/books/all`);
        const data = await response.json();

        //Safety check so the app doesn't explode if backend returns something weird
        allBooks = Array.isArray(data.books) ? data.books : [];

        //Displaying all books on page load
        renderBooks(allBooks);

    } catch (error) {
        console.error("The books have escaped the backend cage:", error);

        //Showing a polite message instead of a scary console error XD
        $("noResultsMessage").classList.remove("d-none");
        $("noResultsMessage").textContent =
            "Oops! We couldn't load the books from the server.Please try refreshing";
    }
}


//-----------------------------------------------------------------------------
//Rendering book card in the grid
//-----------------------------------------------------------------------------
function renderBooks(books) {
    const grid = $("booksGrid");
    const noResults = $("noResultsMessage");

    //Clearing old cards so they don’t stack like a Jenga tower
    grid.innerHTML = "";

    //If no books match the filters then we show message (and dramatic disappointment :()
    if (!books || books.length === 0) {
        noResults.classList.remove("d-none");
        return;
    }

    noResults.classList.add("d-none");

    //Loop through each book and creating a nice Bootstrap card
    books.forEach((book) => {

        const col = document.createElement("div");
        col.className = "col";

        const isAvailable = !!book.available;
        const statusClass = isAvailable ? "bg-success" : "bg-secondary";
        const statusText = isAvailable ? "Available" : "Not Available";

        //Building image URL — if a book has no image, we use a fallback
        const coverImage = book.cover_image
            ? `${API_BASE}/image/${book.cover_image}`
            : "/static/images/library1.jpg";

        col.innerHTML = `
            <div class="card h-100 shadow-sm">
                <img src="${coverImage}" 
                     alt="${escapeHtml(book.title || "Book Cover")}"
                     class="card-img-top"
                     style="height:250px; object-fit:contain; padding:10px;">
                
                <div class="card-body text-center">

                    <h6 class="card-title fw-bold mb-1">
                        ${escapeHtml(book.title || "Untitled")}
                    </h6>

                    <p class="mb-1"><strong>Author:</strong> ${escapeHtml(book.author || "Unknown")}</p>
                    <p class="mb-1"><strong>Year:</strong> ${book.year || "—"}</p>
                    <p class="mb-1"><strong>Language:</strong> ${escapeHtml(book.language || "—")}</p>

                    <p class="mb-2">
                        <strong>Status:</strong>
                        <span class="badge ${statusClass}">${statusText}</span>
                    </p>

                    ${
                        isAvailable
                            ? `<button class="btn btn-outline-primary btn-sm" 
                                       data-action="borrow" 
                                       data-book-id="${book.id}">
                                   Borrow
                               </button>`
                            : `<button class="btn btn-secondary btn-sm" disabled>Borrowed</button>`
                    }
                </div>
            </div>
        `;

        grid.appendChild(col);
    });
}


//-----------------------------------------------------------------------------
//Applying filters based on user input
//-----------------------------------------------------------------------------
function applyFilters() {

    const titleFilter = $("filterTitle").value.trim().toLowerCase();
    const authorFilter = $("filterAuthor").value.trim().toLowerCase();
    const isbnFilter = $("filterIsbn").value.trim().toLowerCase();
    const yearFilter = $("filterYear").value.trim();
    const languageFilter = $("filterLanguage").value.trim().toLowerCase();
    const statusFilter = $("filterStatus").value;

    //Starting with all books and progressively filter down
    const filtered = allBooks.filter((book) => {

        const title = (book.title || "").toLowerCase();
        const author = (book.author || "").toLowerCase();
        const isbn = (book.isbn || "").toLowerCase();
        const year = book.year ? String(book.year) : "";
        const language = (book.language || "").toLowerCase();
        const isAvailable = !!book.available;

        //Title filtering
        if (titleFilter && !title.includes(titleFilter)) return false;

        //Author filtering
        if (authorFilter && !author.includes(authorFilter)) return false;

        //ISBN filtering
        if (isbnFilter && !isbn.includes(isbnFilter)) return false;

        //Year filtering (exact match)
        if (yearFilter && year !== yearFilter) return false;

        //Language filtering (partial)
        if (languageFilter && !language.includes(languageFilter)) return false;

        //Status filtering
        if (statusFilter === "available" && !isAvailable) return false;
        if (statusFilter === "unavailable" && isAvailable) return false;

        return true;
    });

    //Re-rendering the filtered list
    renderBooks(filtered);
}


//-----------------------------------------------------------------------------
//Our event listenners (Search button, Clear button, Borrow button)
//-----------------------------------------------------------------------------
function initEvents() {

    //SEARCH BUTTON
    $("btnSearch").addEventListener("click", () => {
        applyFilters();
    });

    //CLEAR BUTTON (resets everything)
    $("btnClear").addEventListener("click", () => {
        $("filterForm").reset();
        renderBooks(allBooks);
    });

    //BORROW BUTTON 
    $("booksGrid").addEventListener("click", (event) => {
        const btn = event.target.closest("[data-action='borrow']");
        if (!btn) return; 

        const bookId = btn.getAttribute("data-book-id");
        const book = allBooks.find((b) => String(b.id) === String(bookId));

        if (!book) return;

        selectedBook = book;
        $("borrowBookTitle").textContent = book.title || "this book";

        const modal = new bootstrap.Modal(document.getElementById("confirmBorrowModal"));
        modal.show();
    });

    //MAKE BORROW 
    $("confirmBorrowBtn").addEventListener("click", async () => {
    if (!selectedBook) return;

    // 1. Get the current logged-in user
    const userId = await getCurrentUser();
    if (!userId) return;

    // 2. Prepare API call
    try {
        const response = await fetch(`${API_BASE}/borrow`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
                user_id: userId,
                book_id: selectedBook.id
            })
        });

        const result = await response.json();

        // 3. Handle backend response
        if (response.ok && result.success) {
            alert("Successfully borrowed the book!");

            // Refresh books to update availability
            await loadBooks();

            // Close modal
            const modalEl = document.getElementById("confirmBorrowModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();

        } else {
            alert(result.detail || result.message || "Borrowing failed.");
        }
    } catch (error) {
        console.error("Borrow request failed:", error);
        alert("An error occurred while borrowing the book.");
    }
});
}


//-----------------------------------------------------------------------------
//HELPER: escapeHtml() function:
//This function makes sure that any weird characters in book titles (like < or >)
//are shown as normal text and NOT treated as real HTML.
//Example: "<Hello>" becomes "&lt;Hello&gt;" so the page doesn't break.
//-----------------------------------------------------------------------------
function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (char) => {
        return {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;",
        }[char];
    });
}


//-----------------------------------------------------------------------------
//When the page finishes loading, this runs our setup functions so the filters,
//buttons, and book list all start working immediately.
//-----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    initEvents();  // Attach buttons, listeners, etc.
    loadBooks();   // Fetch books from backend and display them
});
