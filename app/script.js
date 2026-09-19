// ==========================================
// DOCUMENT Q&A AGENT - FRONTEND SCRIPT
// ==========================================

// Stores the ID of the currently uploaded document
let currentDocumentId = null;


// ==========================================
// GET HTML ELEMENTS
// ==========================================

const chatArea = document.getElementById("chatArea");
const questionInput = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");
const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");


// ==========================================
// ADD USER MESSAGE
// ==========================================

function addUserMessage(message) {

    const messageWrapper = document.createElement("div");

    messageWrapper.className = "message user-message";

    messageWrapper.innerHTML = `
        <div class="avatar">
            You
        </div>

        <div class="message-content">

            <div class="message-name">
                You
            </div>

            <div class="message-bubble">
                ${escapeHtml(message)}
            </div>

        </div>
    `;

    chatArea.appendChild(messageWrapper);

    scrollToBottom();
}


// ==========================================
// ADD ASSISTANT MESSAGE
// ==========================================

function addAssistantMessage(message) {

    const messageWrapper = document.createElement("div");

    messageWrapper.className = "message assistant-message";

    messageWrapper.innerHTML = `
        <div class="avatar">
            ✦
        </div>

        <div class="message-content">

            <div class="message-name">
                DocuMind
            </div>

            <div class="message-bubble">
                ${formatAnswer(message)}
            </div>

        </div>
    `;

    chatArea.appendChild(messageWrapper);

    scrollToBottom();
}


// ==========================================
// ADD LOADING MESSAGE
// ==========================================

function addLoadingMessage() {

    const messageWrapper = document.createElement("div");

    messageWrapper.className = "message assistant-message";

    messageWrapper.innerHTML = `
        <div class="avatar">
            ✦
        </div>

        <div class="message-content">

            <div class="message-name">
                DocuMind
            </div>

            <div class="message-bubble loading-bubble">
                <span class="loading-dot"></span>
                <span class="loading-dot"></span>
                <span class="loading-dot"></span>
            </div>

        </div>
    `;

    chatArea.appendChild(messageWrapper);

    scrollToBottom();

    return messageWrapper;
}


// ==========================================
// UPLOAD DOCUMENT
// ==========================================

fileInput.addEventListener("change", async function () {

    if (fileInput.files.length === 0) {

        currentDocumentId = null;

        fileName.textContent = "No document selected";

        return;
    }


    const file = fileInput.files[0];


    // Show uploading status
    fileName.textContent = "Uploading " + file.name + "...";


    const formData = new FormData();

    formData.append("file", file);


    try {

        const response = await fetch("/upload", {

            method: "POST",

            body: formData

        });


        const data = await response.json();


        if (!response.ok) {

            currentDocumentId = null;

            fileName.textContent = "Upload failed";

            addAssistantMessage(
                data.error || "Could not upload the document."
            );

            return;
        }


        // IMPORTANT:
        // Save the document ID returned by Flask
        currentDocumentId = data.document_id;


        // Show uploaded filename
        fileName.textContent = file.name;


        // Tell user upload was successful
        addAssistantMessage(
    `Document "${data.filename}" uploaded successfully.
${data.chunks} chunks added to the knowledge base.`
);


        console.log(
            "Current document ID:",
            currentDocumentId
        );

    }


    catch (error) {

        console.error("Upload error:", error);

        currentDocumentId = null;

        fileName.textContent = "Upload failed";

        addAssistantMessage(
            "Could not connect to the server while uploading the document."
        );

    }

});


// ==========================================
// ASK QUESTION
// ==========================================

async function sendQuestion() {

    const question = questionInput.value.trim();


    // Don't send empty questions
    if (!question) {
        return;
    }


    // IMPORTANT:
    // User must upload a document first
    if (!currentDocumentId) {

        addAssistantMessage(
            "Please upload a document first before asking a question."
        );

        return;
    }


    // Add user's question to chat
    addUserMessage(question);


    // Clear input
    questionInput.value = "";


    // Disable send button
    sendButton.disabled = true;


    // Show loading animation
    const loadingMessage = addLoadingMessage();


    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                question: question,

                // IMPORTANT:
                // Send current document ID to backend
                document_id: currentDocumentId

            })

        });


        const data = await response.json();


        // Remove loading message
        loadingMessage.remove();


        if (!response.ok) {

            addAssistantMessage(
                data.error || "Something went wrong."
            );

            return;
        }


        // Display AI answer
        addAssistantMessage(data.answer);

    }


    catch (error) {

        console.error("Question error:", error);


        loadingMessage.remove();


        addAssistantMessage(
            "I couldn't connect to the server. Please make sure Flask is running."
        );

    }


    finally {

        sendButton.disabled = false;

        questionInput.focus();

    }

}


// ==========================================
// SUGGESTION BUTTONS
// ==========================================

function useSuggestion(question) {

    questionInput.value = question;

    questionInput.focus();

}


// ==========================================
// ENTER KEY
// ==========================================

function handleKeyDown(event) {

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        sendQuestion();

    }

}


// ==========================================
// CLEAR CONVERSATION
// ==========================================

function clearChat() {

    // Keep the welcome message
    chatArea.innerHTML = `

        <div class="message assistant-message">

            <div class="avatar">
                ✦
            </div>

            <div class="message-content">

                <div class="message-name">
                    DocuMind
                </div>

                <div class="message-bubble">

                    <p>
                        Hello! 👋 I'm your Document Q&A Agent.
                    </p>

                    <p>
                        Ask me questions about your uploaded
                        documents and I'll retrieve the relevant
                        information and generate an answer.
                    </p>

                </div>

            </div>

        </div>


        <div class="suggestions">

            <p>Try asking:</p>

            <div class="suggestion-list">

                <button
                    onclick="useSuggestion('What skills does the person have?')"
                >
                    What skills does the person have?
                </button>

                <button
                    onclick="useSuggestion('What experience does the person have?')"
                >
                    What experience does the person have?
                </button>

                <button
                    onclick="useSuggestion('Summarize this document.')"
                >
                    Summarize this document
                </button>

            </div>

        </div>

    `;


    // Reset current document
    currentDocumentId = null;


    // Reset file input
    fileInput.value = "";


    // Reset filename
    fileName.textContent = "No document selected";

}


// ==========================================
// FORMAT AI ANSWER
// ==========================================

function formatAnswer(text) {

    if (!text) {
        return "";
    }

    let formatted = escapeHtml(text);

    // Headings: ### Heading
    formatted = formatted.replace(
        /^### (.*)$/gm,
        '<h3>$1</h3>'
    );

    // Bold: **text**
    formatted = formatted.replace(
        /\*\*(.*?)\*\*/g,
        '<strong>$1</strong>'
    );

    // Bullet points: * text
    formatted = formatted.replace(
        /^\* (.*)$/gm,
        '<li>$1</li>'
    );

    // Convert consecutive <li> elements into a list
    formatted = formatted.replace(
        /(<li>.*?<\/li>)(?=\s*<li>)/gs,
        '$1'
    );

    // Wrap bullet groups
    formatted = formatted.replace(
        /((?:<li>.*?<\/li>\s*)+)/gs,
        '<ul>$1</ul>'
    );

    // Convert line breaks
    formatted = formatted.replace(
        /\n/g,
        '<br>'
    );

    // Remove unnecessary <br> around lists/headings
    formatted = formatted
        .replace(/<br>\s*<h3>/g, '<h3>')
        .replace(/<\/h3>\s*<br>/g, '</h3>')
        .replace(/<br>\s*<ul>/g, '<ul>')
        .replace(/<\/ul>\s*<br>/g, '</ul>');

    return formatted;
}

// ==========================================
// ESCAPE HTML
// ==========================================

function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}


// ==========================================
// SCROLL CHAT TO BOTTOM
// ==========================================

function scrollToBottom() {

    chatArea.scrollTop = chatArea.scrollHeight;

}


// ==========================================
// PAGE LOADED
// ==========================================

console.log("DocuMind frontend loaded.");
