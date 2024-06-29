document.addEventListener("DOMContentLoaded", function() {
    let suggestionRank = -1;

    document.getElementById("query-form").addEventListener("submit", async function(event) {
        event.preventDefault();
        const query = document.getElementById("query").value;
        console.log("Query submitted:", query);

        try {
            const response = await fetch(`/get_results?query=${query}`);
            console.log("Fetch response:", response);
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            const data = await response.json();
            console.log("Received data:", data);
            suggestionRank = data.suggestion_rank;
            const resultsContainer = document.getElementById("results");
            resultsContainer.innerHTML = "";

            data.results.forEach((result, index) => {
                const resultDiv = document.createElement("div");
                resultDiv.classList.add("result-item");

                const radio = document.createElement("input");
                radio.type = "radio";
                radio.name = "choice";
                radio.value = index + 1;

                const label = document.createElement("label");
                label.innerHTML = `
                    ${index + 1}. <br>
                    <strong>Latitude:</strong> ${result.lat}<br>
                    <strong>Longitude:</strong> ${result.lon}<br>
                    <strong>Description (English):</strong> ${result.description}<br>
                    <strong>Description (Mandarin):</strong> ${result["descriptions-mandarin"]}<br>
                    <div class="image-row">
                        <img src="${result.image_url_fwd}" alt="Image of the place">
                        <img src="${result.image_url_l}" alt="Image of the place">
                        <img src="${result.image_url_r}" alt="Image of the place">
                    </div>
                `;

                resultDiv.appendChild(radio);
                resultDiv.appendChild(label);
                resultsContainer.appendChild(resultDiv);
            });

            document.getElementById("results-container").style.display = "block";
        } catch (error) {
            console.error("Fetch error:", error);
        }
    });

    document.getElementById("results-form").addEventListener("submit", async function(event) {
        event.preventDefault();
        const query = document.getElementById("query").value;
        const choice = document.querySelector('input[name="choice"]:checked').value;
        console.log("Choice submitted:", choice);
        console.log("Suggestion Rank:", suggestionRank);  // Log suggestion rank

        const formData = new FormData();
        formData.append("query", query);
        formData.append("choice", choice);
        formData.append("suggestion_rank", suggestionRank);

        for (let pair of formData.entries()) {
            console.log(pair[0]+ ': ' + pair[1]);  // Log all form data entries
        }

        try {
            const response = await fetch("/submit_choice", {
                method: "POST",
                body: formData
            });
            console.log("Submit response:", response);
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            const data = await response.json();
            alert(data.message);
        } catch (error) {
            console.error("Submit error:", error);
        }
    });
});
