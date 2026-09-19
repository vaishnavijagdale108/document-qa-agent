from vector_store import search_documents
from llm import generate_answer


def ask_question(question, document_id, history=None):

    # Get relevant document chunks
    context = search_documents(
        question,
        document_id
    )

    context = "\n".join(context)


    # Build conversation history
    conversation = ""

    if history:

        for item in history:

            conversation += f"""
User: {item["question"]}
Assistant: {item["answer"]}
"""


    # Add conversation history to the context
    if conversation:

        context = f"""
Previous Conversation:
{conversation}

Relevant Document Context:
{context}
"""


    # Generate answer
    answer = generate_answer(
        question,
        context
    )


    return answer