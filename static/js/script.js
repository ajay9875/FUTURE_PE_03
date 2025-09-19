//Simple JavaScript just for UX (optional, can be removed)
// This is only for UX - focuses the input field and auto-scrolls
// The app will work even if JavaScript is disabled
document.addEventListener('DOMContentLoaded', function() {
    const inputField = document.getElementById('user-input');
    const chatHistory = document.querySelector('.chat-history');
    
    // Focus input field
    if (inputField) {
        inputField.focus();
    }
    
    // Auto-scroll to bottom of chat history
    if (chatHistory) {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});