// --------------------------------
// Get elements
// --------------------------------

const searchInput =
    document.getElementById("searchInput");

const searchButton =
    document.getElementById("searchButton");

const historyList =
    document.getElementById("historyList");

const deleteHistoryButton =
    document.getElementById(
        "deleteHistoryButton"
    );

const errorMessage =
    document.getElementById("errorMessage");


// --------------------------------
// Search
// --------------------------------

async function searchWord() {

    const word =
        searchInput.value.trim();


    if (!word) {

        errorMessage.textContent =
            "Please enter a word.";

        return;
    }


    errorMessage.textContent = "";


    searchButton.disabled = true;

    searchButton.textContent =
        "Searching...";


    try {

        const response =
            await fetch("/api/search", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    word: word
                })

            });


        const data =
            await response.json();


        if (!data.success) {

            errorMessage.textContent =
                data.message;

            return;
        }


        // Store result temporarily

        sessionStorage.setItem(
            "tridictResult",
            JSON.stringify(data)
        );


        // Open result page

        window.location.href =
            "/result";


    } catch (error) {

        console.error(error);

        errorMessage.textContent =
            "Something went wrong. Please try again.";

    } finally {

        searchButton.disabled = false;

        searchButton.textContent =
            "Search";
    }
}


// --------------------------------
// Search button
// --------------------------------

searchButton.addEventListener(
    "click",
    searchWord
);


// --------------------------------
// Enter key
// --------------------------------

searchInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            searchWord();

        }

    }
);


// --------------------------------
// Load History
// --------------------------------

async function loadHistory() {

    try {

        const response =
            await fetch("/api/history");


        const data =
            await response.json();


        if (!data.success ||
            data.history.length === 0) {

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

                    <div>

                        <strong>
                            ${escapeHTML(
                                item.searched_word
                            )}
                        </strong>

                        <small>
                            ${escapeHTML(
                                item.detected_language
                            )}
                        </small>

                    </div>

                    <span>
                        →
                    </span>

                `;


                historyItem.addEventListener(
                    "click",
                    function() {

                        searchInput.value =
                            item.searched_word;

                        searchWord();

                    }
                );


                historyList.appendChild(
                    historyItem
                );

            }
        );

    } catch (error) {

        console.error(error);

    }
}


// --------------------------------
// Delete History
// --------------------------------

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


            if (data.success) {

                loadHistory();

            }

        } catch (error) {

            console.error(error);

        }

    }
);


// --------------------------------
// HTML Security Helper
// --------------------------------

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;
}


// --------------------------------
// Load history on startup
// --------------------------------

loadHistory();