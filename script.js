document.querySelector("button").addEventListener("click", async () => {
    const songName = document.querySelector('input[placeholder="Enter song name"]').value;
    const songAuthor = document.querySelector('input[placeholder="Enter artist name"]').value;
    const coverFile = document.getElementById("cover-upload").files[0];
    const audioFile = document.getElementById("audio-upload").files[0];
    const environmentPath = document.querySelector("select").value;

    if (!songName || !songAuthor || !coverFile || !audioFile) {
        alert("Fill in all fields and select files!");
        return;
    }

    const formData = new FormData();
    formData.append("song_name", songName);
    formData.append("song_author", songAuthor);
    formData.append("cover", coverFile);
    formData.append("audio", audioFile);
    formData.append("environment", environmentPath)

    const difficulties = [];
    document.querySelectorAll('input[type="checkbox"]:checked').forEach(el => {
        difficulties.push(el.nextElementSibling.textContent);
    });

    formData.append("difficulties", JSON.stringify(difficulties));

    try {
        const response = await fetch("http://127.0.0.1:8000/upload", {
            method: "POST",
            body: formData,
        });

        const text = await response.text();
        console.log("📦 Raw response text:", text);

        if (!response.ok) {
            throw new Error(`Szerver válasz: ${response.status} – ${text}`);
        }

        const result = JSON.parse(text);
        console.log("✅ JSON result:", result);
        alert("Files uploaded and processed!");

    } catch (err) {
        console.error("❌ Hiba:", err);
        alert("An error occurred while uploading:\n" + err.message);
    }

});