document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-button");
    const chatBox = document.getElementById("chat-history");
    const clearBtn = document.getElementById("clear-chat");

    function addMessage(text, cls) {
        const div = document.createElement("div");
        div.className = `message ${cls}`;
        div.innerText = text;
        chatBox.appendChild(div);
    }

    async function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        addMessage(message, "user-message");
        input.value = "";

        const thinking = document.createElement("div");
        thinking.className = "message bot-message";
        thinking.innerText = "⏳ Thinking...";
        chatBox.appendChild(thinking);

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message })
            });

            const data = await res.json();
            thinking.innerText = data.reply;

        } catch (err) {
            thinking.innerText = "⚠️ Server error. Try again.";
        }
    }

    sendBtn.onclick = sendMessage;
    input.addEventListener("keypress", e => {
        if (e.key === "Enter") sendMessage();
    });

    clearBtn.onclick = async () => {
        await fetch("/clear", { method: "POST" });
        chatBox.innerHTML = "";
    };

    input.focus();
});
