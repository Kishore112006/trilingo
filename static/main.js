// ==========================================
// GET ELEMENTS
// ==========================================

const searchInput =
    document.getElementById("searchInput");

const searchButton =
    document.getElementById("searchButton");

const historyList =
    document.getElementById("historyList");

const deleteHistoryButton =
    document.getElementById("deleteHistoryButton");

const errorMessage =
    document.getElementById("errorMessage");


// ==========================================
// SEARCH
// ==========================================

async function searchWord() {

    const word = searchInput.value.trim();

    if (!word) {

        if (errorMessage) {
            errorMessage.textContent =
                "Please enter a word.";
        }

        return;
    }

    if (errorMessage) {
        errorMessage.textContent = "";
    }

    searchButton.disabled = true;
    searchButton.textContent = "Searching...";

    try {

        const response = await fetch("/api/search", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                word: word
            })

        });

        const data = await response.json();

        console.log("Search response:", data);

        if (!data.success) {

            if (errorMessage) {
                errorMessage.textContent =
                    data.message || "Search failed.";
            }

            return;
        }


        // Save result temporarily

        sessionStorage.setItem(
            "tridictResult",
            JSON.stringify(data)
        );


        // Open result page

        window.location.href = "/result";


    } catch (error) {

        console.error("Search error:", error);

        if (errorMessage) {
            errorMessage.textContent =
                "Something went wrong. Please try again.";
        }

    } finally {

        searchButton.disabled = false;
        searchButton.textContent = "Search";

    }
}


// ==========================================
// SEARCH BUTTON
// ==========================================

if (searchButton) {

    searchButton.addEventListener(
        "click",
        searchWord
    );

}


// ==========================================
// ENTER KEY
// ==========================================

if (searchInput) {

    searchInput.addEventListener(
        "keydown",
        function(event) {

            if (event.key === "Enter") {

                searchWord();

            }

        }
    );

}


// ==========================================
// LOAD HISTORY
// ==========================================

async function loadHistory() {

    // History section doesn't exist on this page

    if (!historyList) {
        return;
    }


    try {

        const response =
            await fetch("/api/history");

        console.log(
            "History HTTP status:",
            response.status
        );


        if (!response.ok) {

            throw new Error(
                "History API returned " +
                response.status
            );

        }


        const data =
            await response.json();

        console.log(
            "History response:",
            data
        );


        if (
            !data.success ||
            !Array.isArray(data.history) ||
            data.history.length === 0
        ) {

            historyList.innerHTML = `
                <p class="no-history">
                    No searches yet.
                </p>
            `;

            return;
        }


        historyList.innerHTML = "";


        data.history.forEach(
            function(item) {

                const historyItem =
                    document.createElement("div");

                historyItem.className =
                    "history-item";


                historyItem.innerHTML = `

                    <div class="history-info">

                        <strong>
                            ${escapeHTML(
                                item.searched_word || ""
                            )}
                        </strong>

                        <small>
                            ${escapeHTML(
                                item.detected_language || ""
                            )}
                        </small>

                    </div>

                    <span class="history-arrow">
                        →
                    </span>

                `;


                // Search again when history item is clicked

                historyItem.addEventListener(
                    "click",
                    function() {

                        if (searchInput) {

                            searchInput.value =
                                item.searched_word;

                            searchWord();

                        }

                    }
                );


                historyList.appendChild(
                    historyItem
                );

            }
        );


    } catch (error) {

        console.error(
            "History loading error:",
            error
        );

        historyList.innerHTML = `
            <p class="no-history">
                Unable to load history.
            </p>
        `;

    }
}


// ==========================================
// DELETE HISTORY
// ==========================================

if (deleteHistoryButton) {

    deleteHistoryButton.addEventListener(
        "click",
        async function() {

            const confirmDelete =
                confirm(
                    "Delete all search history?"
                );


            if (!confirmDelete) {
                return;
            }


            try {

                const response =
                    await fetch(
                        "/api/history/delete",
                        {
                            method: "DELETE"
                        }
                    );


                const data =
                    await response.json();


                console.log(
                    "Delete response:",
                    data
                );


                if (data.success) {

                    await loadHistory();

                } else {

                    alert(
                        data.message ||
                        "Could not delete history."
                    );

                }


            } catch (error) {

                console.error(
                    "Delete history error:",
                    error
                );

                alert(
                    "Could not delete history."
                );

            }

        }
    );

}


// ==========================================
// HTML SECURITY
// ==========================================

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent =
        String(text);

    return div.innerHTML;
}


// ==========================================
// LOAD HISTORY WHEN PAGE OPENS
// ==========================================

loadHistory();