from vector_store import search_documents
from llm import generate_answer


def ask_question(question, document_id, history=None):

    # ==========================================
    # GET RELEVANT DOCUMENT CHUNKS
    # ==========================================

    context = search_documents(
        question,
        document_id
    )

    context = "\n".join(context)


    # ==========================================
    # BUILD CONVERSATION HISTORY
    # ==========================================

    conversation = ""

    if history:

        for item in history:

            conversation += f"""
User: {item["question"]}
Assistant: {item["answer"]}
"""


    # ==========================================
    # ADD HISTORY TO CONTEXT
    # ==========================================

    if conversation:

        context = f"""
Previous Conversation:
{conversation}

Relevant Document Context:
{context}
"""


    # ==========================================
    # GENERATE ANSWER
    # ==========================================

    answer = generate_answer(
        question,
        context,
        document_id
    )


    # ==========================================
    # RETURN ANSWER
    # ==========================================

    return answer