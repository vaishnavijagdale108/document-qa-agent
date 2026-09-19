from google import genai
from google.genai import types

from dotenv import load_dotenv
import os

from custom_tools import (
    calculate,
    summarize_document
)

from mcp_client import call_mcp_tool


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_answer(question, context, document_id):

    def calculator(expression: str) -> dict:
        """
        Perform a mathematical calculation.
        """
        return calculate(expression)

    def document_summary() -> dict:
        """
        Retrieve the currently selected document content
        for summarization.
        """
        return summarize_document(document_id)

    def mcp_document_statistics() -> dict:
        """
        Get statistics for the current document
        through the MCP server.
        """

        result = call_mcp_tool(
            "document_statistics",
            {
                "document_id": document_id
            }
        )

        return {
            "mcp_result": str(result)
        }

    prompt = f"""
You are a Document Question Answering Agent.

Your job is to answer questions using the provided document context,
conversation history, and available tools.

IMPORTANT RULES:

1. Use the document context when it contains the answer.
2. Use the conversation history when the user asks a follow-up question.
3. Use the calculator tool for mathematical calculations.
4. Use the document_summary tool when the user asks for a summary
   or when the complete document content is required.
5. When the user asks about document statistics such as:
   - number of chunks
   - document size
   - total characters
   - document statistics

   you MUST use the MCP document statistics tool.

6. Do not calculate or guess document statistics yourself.
7. Do not invent information.
8. If the document does not contain enough information, clearly say so.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[
                calculator,
                document_summary,
                mcp_document_statistics
            ]
        )
    )

    return response.text