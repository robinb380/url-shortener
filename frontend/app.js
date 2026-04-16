async function shortenUrl() {
    const url = document.getElementById("urlInput").value;

    const resultDiv = document.getElementById("result");

    try {
        const response = await fetch("http://localhost:8080/shorten", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<p style="color:red">${data.error}</p>`;
            return;
        }

        const shortUrl = data.short_url;

        resultDiv.innerHTML = `
            <p>Short URL:</p>
            <a href="${shortUrl}" target="_blank">${shortUrl}</a>
            <br><br>
            <button onclick="copyToClipboard('${shortUrl}')">
                Copy
            </button>
        `;

    } catch (err) {
        console.log(err);
        resultDiv.innerHTML = `<p style="color:red">Server error</p>`;
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard");
}