const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

// Event listener
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", function(e){
    if(e.key === "Enter") sendMessage();
});

// Append message dengan scroll otomatis
function appendMessage(sender, message){
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("chat-message", sender);
    msgDiv.innerHTML = message; // pakai innerHTML agar bisa format HTML
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // scroll otomatis
}

// Pesan awal chatbot
window.addEventListener("DOMContentLoaded", () => {
    appendMessage("bot", "Halo! Saya Chatbot Gizi 🌱. Saya bisa membantu menjawab pertanyaan tentang gizi, stunting, IMT, dan kebutuhan kalori.");
    appendMessage("bot", `
        Contoh pertanyaan:<br>
        - Apa itu stunting?<br>
        - Bagaimana cara mencegah stunting?<br>
        - Cara menghitung IMT saya<br>
        - Kebutuhan kalori harian
    `);
});

// Mengirim pesan ke backend
async function sendMessage(){
    const message = userInput.value.trim();
    if(message === "") return;

    appendMessage("user", message);
    userInput.value = "";

    appendMessage("bot", "Bot sedang memproses...");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({prompt: message}) // hanya prompt
        });

        const data = await response.json();

        chatBox.lastChild.remove(); // hapus loading

        // Backend sekarang selalu kirim string (dengan <br>)
        appendMessage("bot", data.answer);

    } catch (err) {
        chatBox.lastChild.remove();
        appendMessage("bot", "Terjadi kesalahan. Silakan coba lagi.");
        console.error(err);
    }
}
