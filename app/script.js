// ==========================================
// DOCUMIND - DOCUMENT Q&A FRONTEND
// ==========================================


// ==========================================
// APPLICATION STATE
// ==========================================

// Restore uploaded documents from browser storage
let documents = JSON.parse(
    localStorage.getItem("documents") || "[]"
);

// Restore selected document
let currentDocumentId =
    localStorage.getItem("currentDocumentId");


// ==========================================
// HTML ELEMENTS
// ==========================================

const chatArea =
    document.getElementById("chatArea");

const questionInput =
    document.getElementById("questionInput");

const sendButton =
    document.getElementById("sendButton");

const fileInput =
    document.getElementById("fileInput");

const fileName =
    document.getElementById("fileName");

const documentList =
    document.getElementById("documentList");


// ==========================================
// SAVE DOCUMENTS TO LOCAL STORAGE
// ==========================================

function saveDocuments() {

    localStorage.setItem(
        "documents",
        JSON.stringify(documents)
    );
}


// ==========================================
// SAVE CURRENT DOCUMENT
// ==========================================

function saveCurrentDocument() {

    if (currentDocumentId) {

        localStorage.setItem(
            "currentDocumentId",
            currentDocumentId
        );

    } else {

        localStorage.removeItem(
            "currentDocumentId"
        );
    }
}


// ==========================================
// ADD USER MESSAGE
// ==========================================

function addUserMessage(message) {

    const messageWrapper =
        document.createElement("div");

    messageWrapper.className =
        "message user-message";

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

    chatArea.appendChild(
        messageWrapper
    );

    scrollToBottom();
}


// ==========================================
// ADD ASSISTANT MESSAGE
// ==========================================

function addAssistantMessage(message) {

    const messageWrapper =
        document.createElement("div");

    messageWrapper.className =
        "message assistant-message";

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

    chatArea.appendChild(
        messageWrapper
    );

    scrollToBottom();
}


// ==========================================
// LOADING MESSAGE
// ==========================================

function addLoadingMessage() {

    const messageWrapper =
        document.createElement("div");

    messageWrapper.className =
        "message assistant-message";

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

    chatArea.appendChild(
        messageWrapper
    );

    scrollToBottom();

    return messageWrapper;
}


// ==========================================
// UPLOAD DOCUMENT
// ==========================================

fileInput.addEventListener(
    "change",
    async function () {

        if (
            fileInput.files.length === 0
        ) {
            return;
        }


        const file =
            fileInput.files[0];


        fileName.textContent =
            "Uploading " + file.name + "...";


        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );


        try {

            const response =
                await fetch(
                    "/upload",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            // --------------------------------------
            // UPLOAD ERROR
            // --------------------------------------

            if (!response.ok) {

                fileName.textContent =
                    "Upload failed";

                addAssistantMessage(
                    data.error ||
                    "Could not upload the document."
                );

                return;
            }


            // --------------------------------------
            // CREATE DOCUMENT OBJECT
            // --------------------------------------

            const documentItem = {

                id: data.document_id,

                name: data.filename,

                chunks: data.chunks

            };


            // --------------------------------------
            // ADD TO DOCUMENT LIST
            // --------------------------------------

            documents.push(
                documentItem
            );


            // --------------------------------------
            // SAVE DOCUMENT LIST
            // --------------------------------------

            saveDocuments();


            // --------------------------------------
            // SELECT NEW DOCUMENT
            // --------------------------------------

            currentDocumentId =
                data.document_id;


            saveCurrentDocument();


            fileName.textContent =
                data.filename;


            // --------------------------------------
            // UPDATE UI
            // --------------------------------------

            renderDocuments();


            // --------------------------------------
            // SUCCESS MESSAGE
            // --------------------------------------

            addAssistantMessage(
                `Document "${data.filename}" uploaded successfully.
${data.chunks} chunks added to the knowledge base.

This document is now selected.`
            );


            console.log(
                "Current document ID:",
                currentDocumentId
            );

        }

        catch (error) {

            console.error(
                "Upload error:",
                error
            );


            fileName.textContent =
                "Upload failed";


            addAssistantMessage(
                "Could not connect to the server while uploading the document."
            );

        }

        finally {

            // Allows same file to be selected again
            fileInput.value = "";

        }

    }
);


// ==========================================
// RENDER DOCUMENT LIST
// ==========================================

function renderDocuments() {

    documentList.innerHTML = "";


    // --------------------------------------
    // REMOVE INVALID SELECTED DOCUMENT
    // --------------------------------------

    if (
        currentDocumentId &&
        !documents.some(
            doc =>
                doc.id === currentDocumentId
        )
    ) {

        currentDocumentId = null;

        saveCurrentDocument();

    }


    // --------------------------------------
    // NO DOCUMENTS
    // --------------------------------------

    if (
        documents.length === 0
    ) {

        documentList.innerHTML = `
            <div class="empty-documents">
                No documents uploaded yet
            </div>
        `;

        return;
    }


    // --------------------------------------
    // DOCUMENT LIST
    // --------------------------------------

    documents.forEach(
        (doc) => {

            const item =
                document.createElement(
                    "button"
                );


            item.className =
                "document-item";


            // Highlight active document
            if (
                doc.id ===
                currentDocumentId
            ) {

                item.classList.add(
                    "active"
                );

            }


            item.innerHTML = `

                <div class="document-icon">
                    📄
                </div>

                <div class="document-info">

                    <div class="document-name">
                        ${escapeHtml(doc.name)}
                    </div>

                    <div class="document-meta">
                        ${doc.chunks} chunks
                    </div>

                </div>

            `;


            item.onclick =
                function () {

                    selectDocument(
                        doc.id
                    );

                };


            documentList.appendChild(
                item
            );

        }
    );
}


// ==========================================
// SELECT DOCUMENT
// ==========================================

function selectDocument(
    documentId
) {

    const selectedDocument =
        documents.find(
            doc =>
                doc.id === documentId
        );


    if (!selectedDocument) {

        return;
    }


    // Set current document
    currentDocumentId =
        selectedDocument.id;


    // Save selected document
    saveCurrentDocument();


    // Update sidebar
    renderDocuments();


    // Update filename
    fileName.textContent =
        selectedDocument.name;


    // Tell user
    addAssistantMessage(
        `Switched to "${selectedDocument.name}".

Your questions will now be answered using this document.`
    );


    console.log(
        "Selected document:",
        currentDocumentId
    );
}


// ==========================================
// ASK QUESTION
// ==========================================

async function sendQuestion() {

    const question =
        questionInput.value.trim();


    // --------------------------------------
    // EMPTY QUESTION
    // --------------------------------------

    if (!question) {

        return;
    }


    // --------------------------------------
    // NO DOCUMENT
    // --------------------------------------

    if (!currentDocumentId) {

        addAssistantMessage(
            "Please upload and select a document first."
        );

        return;
    }


    // --------------------------------------
    // ADD USER MESSAGE
    // --------------------------------------

    addUserMessage(
        question
    );


    questionInput.value = "";


    sendButton.disabled = true;


    // --------------------------------------
    // LOADING
    // --------------------------------------

    const loadingMessage =
        addLoadingMessage();


    try {

        const response =
            await fetch(
                "/ask",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        question:
                            question,

                        document_id:
                            currentDocumentId

                    })

                }
            );


        const data =
            await response.json();


        // Remove loading
        loadingMessage.remove();


        // --------------------------------------
        // SERVER ERROR
        // --------------------------------------

        if (!response.ok) {

            addAssistantMessage(
                data.error ||
                "Something went wrong."
            );

            return;
        }


        // --------------------------------------
        // ANSWER
        // --------------------------------------

        addAssistantMessage(
            data.answer
        );

    }

    catch (error) {

        console.error(
            "Question error:",
            error
        );


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
// SUGGESTIONS
// ==========================================

function useSuggestion(
    question
) {

    questionInput.value =
        question;

    questionInput.focus();
}


// ==========================================
// ENTER KEY
// ==========================================

function handleKeyDown(
    event
) {

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

    // Clear visible conversation only.
    // Uploaded documents remain available.

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
                        Select a document and ask a question.
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


    // IMPORTANT:
    // We intentionally DO NOT clear
    // currentDocumentId here.
    //
    // The selected document stays active.

    renderDocuments();

}


// ==========================================
// FORMAT AI ANSWER
// ==========================================

function formatAnswer(
    text
) {

    if (!text) {

        return "";
    }


    let formatted =
        escapeHtml(text);


    // --------------------------------------
    // HEADINGS
    // --------------------------------------

    formatted =
        formatted.replace(
            /^### (.*)$/gm,
            "<h3>$1</h3>"
        );


    // --------------------------------------
    // BOLD
    // --------------------------------------

    formatted =
        formatted.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    // --------------------------------------
    // BULLETS
    // --------------------------------------

    formatted =
        formatted.replace(
            /^\* (.*)$/gm,
            "<li>$1</li>"
        );


    // --------------------------------------
    // BULLET GROUPS
    // --------------------------------------

    formatted =
        formatted.replace(
            /((?:<li>.*?<\/li>\s*)+)/gs,
            "<ul>$1</ul>"
        );


    // --------------------------------------
    // LINE BREAKS
    // --------------------------------------

    formatted =
        formatted.replace(
            /\n/g,
            "<br>"
        );


    // --------------------------------------
    // CLEAN FORMATTING
    // --------------------------------------

    formatted =
        formatted
            .replace(
                /<br>\s*<h3>/g,
                "<h3>"
            )
            .replace(
                /<\/h3>\s*<br>/g,
                "</h3>"
            )
            .replace(
                /<br>\s*<ul>/g,
                "<ul>"
            )
            .replace(
                /<\/ul>\s*<br>/g,
                "</ul>"
            );


    return formatted;
}


// ==========================================
// ESCAPE HTML
// ==========================================

function escapeHtml(
    text
) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        text;

    return div.innerHTML;
}


// ==========================================
// SCROLL CHAT
// ==========================================

function scrollToBottom() {

    chatArea.scrollTop =
        chatArea.scrollHeight;
}


// ==========================================
// RESTORE DOCUMENT ON PAGE LOAD
// ==========================================

function restoreSelectedDocument() {

    // If no saved document exists
    if (!currentDocumentId) {

        renderDocuments();

        return;
    }


    const selectedDocument =
        documents.find(
            doc =>
                doc.id ===
                currentDocumentId
        );


    // Saved document no longer exists
    if (!selectedDocument) {

        currentDocumentId =
            null;

        localStorage.removeItem(
            "currentDocumentId"
        );

        renderDocuments();

        return;
    }


    // Restore filename
    fileName.textContent =
        selectedDocument.name;


    // Highlight selected document
    renderDocuments();


    console.log(
        "Restored document:",
        selectedDocument.name
    );

    console.log(
        "Restored document ID:",
        currentDocumentId
    );
}


// ==========================================
// INITIALIZE FRONTEND
// ==========================================

restoreSelectedDocument();

console.log(
    "DocuMind frontend loaded."
);