document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-button");
    const chatBox = document.getElementById("chat-history");
    const clearBtn = document.getElementById("clear-chat");

    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function addMessage(text, cls) {
        const div = document.createElement("div");
        div.className = `message ${cls}`;
        div.innerText = text;
        chatBox.appendChild(div);
        scrollToBottom();   // ✅ THIS IS THE KEY PART
        return div;
    }

    async function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        // User message (append, not replace)
        addMessage(message, "user-message");
        input.value = "";

        // Bot thinking message
        const thinking = addMessage("⏳ Thinking...", "bot-message");

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message })
            });

            const data = await res.json();

            // Replace only thinking text
            thinking.innerText = data.reply;
            scrollToBottom();

        } catch (err) {
            thinking.innerText = "⚠️ Server error. Try again.";
            scrollToBottom();
        }
    }

    sendBtn.addEventListener("click", sendMessage);

    input.addEventListener("keydown", e => {
        if (e.key === "Enter") sendMessage();
    });

    clearBtn.addEventListener("click", async () => {
        await fetch("/clear", { method: "POST" });
        chatBox.innerHTML = "";
    });

    // ✅ IMPORTANT: On page load, show last message
    scrollToBottom();
});
